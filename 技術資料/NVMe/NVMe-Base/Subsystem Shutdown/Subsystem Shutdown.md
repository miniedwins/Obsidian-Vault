在 NVMe 規範（_NVM Express Base Specification Revision 2.3_，Section 3.6.3 與 Section 3.1.4.20）中，**NVM Subsystem Shutdown（子系統關機）** 是一項專為「多控制器（Multi-Controller）」與「多網域（Multi-Domain）」架構設計的進階關機機制。

---

### 一、 Subsystem Shutdown 的用途是什麼？（Why need it?）

1. **一鍵協調多控制器同步關機**：
    
    - 在標準的 **Controller Shutdown**（透過 `CC.SHN`）中，主機只能針對「單一控制器」發出關機通知。如果是一顆 Dual-port SSD 或具備多個 Controller（如 SR-IOV 實體功能、NVMe-oF 連接）的儲存子系統，主機軟體若要逐一對每個控制器發起關機，程序繁瑣且容易出現時間差或競態問題。
    - **Subsystem Shutdown 的核心用途**：允許主機**「僅對單一控制器下達一次命令」**，或由底板管理控制器（BMC）**「透過帶外管理介面發出一次命令」**，就能直接連動**整個 NVM Subsystem（或該 Domain 內）的所有控制器同步執行安全關機**。
2. **確保底層共享媒體資料完整性並加速下次開機**：
    
    - 當整個子系統的所有控制器完成關機處理（快取回寫至 NAND、狀態落地）後，底層儲存媒體會進入 **Shutdown 狀態**。
    - 系統在此時切斷主電源（Power-off）不會增加「不安全斷電計數（Unexpected Power Losses）」，且能確保下次重新通電初始化時，SSD 可以在最短時間內就緒（避免耗費過長時間進行斷電資料修復與掃描）。

---

### 二、 Subsystem Shutdown 的主要功能與運作機制

#### 1. 觸發途徑（Initiation Methods）

主機可透過以下兩種管道觸發子系統關機：

- **帶內暫存器（In-band Register）**： 主機向控制器的 **`NSSD.NSSC`**（NVM Subsystem Shutdown Control，Offset 64h）暫存器寫入特定 4 位元組字元：
    - 寫入 `4E726D6Ch`（ASCII 字串 `"Nrml"`）\(\to\) 觸發 **Normal NVM Subsystem Shutdown（正常子系統關機）**。
    - 寫入 `41627074h`（ASCII 字串 `"Abpt"`）\(\to\) 觸發 **Abrupt NVM Subsystem Shutdown（緊急/突然子系統關機）**。
- **帶外管理介面（Out-of-band NVMe-MI）**： BMC 可透過 MCTP 發送 NVMe-MI **`Shutdown` 指令**（Opcode 0Ch），同樣可指定 Normal 或 Abrupt。

#### 2. 影響範圍（Scope）

關機範圍由控制器回報的 `CAP.CPS`（Controller Power Scope）決定：

- **`CAP.CPS = 11b`（Subsystem Scope）**：整顆 SSD（NVM Subsystem）內部的**所有控制器**全部同步執行關機。
- **`CAP.CPS = 10b`（Domain Scope）**：僅針對該控制器所屬 **Domain 內的所有控制器**執行關機。

#### 3. 預警與狀態回報機制（Status & Notification）

- **AER 即時預警**： 在發起 Normal Subsystem Shutdown 時，各控制器若有已掛載的 Asynchronous Event Request（AER），控制器會在正式關閉前主動發出 **`Normal NVM Subsystem Shutdown` 即時事件（Immediate Event）** 通知相關主機系統。
- **狀態識別（CSTS.ST 與 CSTS.SHST）**：
    - 各控制器的狀態暫存器中，**`CSTS.ST`（Shutdown Type）會被置為 `1`**（表示當前正處於「Subsystem Shutdown」，區別於一般 Controller Shutdown 的 `0`）。
    - **`CSTS.SHST`（Shutdown Status）** 會轉移至 `01b`（處理中），待所有內部操作落地後轉移至 **`10b`（Shutdown processing complete）**。
    - 規範強制要求：**只有當整個子系統完全就緒且可安全斷電時，所有控制器才會同步將 `CSTS.SHST` 設為 `10b`**。

#### 4. 關機後的重啟限制（嚴格的重置要求）

這也是 Subsystem Shutdown 與一般 Controller Shutdown 最大的不同點：

- **一般 Controller Shutdown**：關閉後只需將 `CC.EN` 重新拉起（0 \(\to\) 1）即可重新初始化控制器。
- **NVM Subsystem Shutdown**：
    - 一旦狀態進入 Subsystem Shutdown（`CSTS.ST = 1` 且 `CSTS.SHST = 10b`），**單純修改 `CC.EN` 完全無效**。
    - 控制器必須經歷 **`NVM Subsystem Reset`（NSSR，寫入 4E564D65h "NVMe" 至 NSSR 暫存器）** 或 **實體重新上電循環（Power Cycle）**，才能解除鎖定並重新恢復指令處理。

---

### 三、 Controller Shutdown vs. Subsystem Shutdown 快速對照

|比較項目|**Controller Shutdown**|**NVM Subsystem Shutdown**|
|:--|:--|:--|
|**觸發暫存器**|`CC.SHN`（Offset 14h）|`NSSD.NSSC`（Offset 64h）或 NVMe-MI|
|**影響對象**|僅接收命令的**單一控制器**|子系統或 Domain 內的**所有控制器**|
|**狀態識別碼**|`CSTS.ST = 0`|`CSTS.ST = 1`|
|**適用場景**|單一 Host 卸載、單一連接埠重置、單控制器進入低功耗|伺服器整機關機、整顆 SSD 拔除更換、BMC 帶外控制斷電|
|**復原方式**|重設 `CC.EN`（1 \(\to\) 0 \(\to\) 1）即可|**必須執行 NVM Subsystem Reset** 或實體重新斷電循環|

---

💡 如果您正在開發或驗證相關韌體，是否需要進一步了解 CAP 暫存器中關於 `NSSS` 與 `NSSES`（Subsystem Shutdown Enhancements）的支援判斷與時序要求？


===========================================================================

根據《NVM Express Base Specification Revision 2.3》與《NVMe Management Interface Specification Revision 2.0》，針對這 4 個問題的深入解析如下：

---

### 1. Subsystem Shutdown 後，怎麼還可以寫到 NSSR 暫存器？

- **硬體分層架構（PCIe 通訊層 vs. 儲存媒體層）**： Subsystem Shutdown 主要關閉的是 **NVM 儲存媒體層（Media state 進入 Shutdown）** 與 **NVMe 命令處理引擎**，確保快取寫回 Flash 並停止擷取指令。但是，**PCIe 實體層、數據鏈路層（Data Link Layer）以及控制器的暫存器解碼邏輯（MMIO BAR0）依然維持通電與運作**。
- **NSSR 是單純的硬體暫存器寫入（PCIe Memory Write TLP）**： `NSSR`（Offset 20h）是 PCIe BAR0 記憶體映射暫存器。當 Host 對 NSSR 寫入 `4E564D65h`（"NVMe"）時，在 PCIe 匯流排上只是一個標準的 **Memory Write 交易（TLP）**。控制器的硬體邏輯電路接收到此特定值後，會直接由硬體觸發內部 Subsystem Reset 訊號線，將所有控制器硬體邏輯與內部狀態重置。
- **規範的明文復原路徑**： 規範明確要求，在 Subsystem Shutdown 完成後（`CSTS.ST = 1` 且 `CSTS.SHST = 10b`），**單靠修改 `CC.EN`（1 \(\to\) 0 \(\to\) 1）是完全無法重新啟用硬碟的**，唯一的軟體恢復手段就是對 `NSSR` 寫入觸發 **NVM Subsystem Reset**。因此控制器在架構上必須在關機後持續監聽並回應對 NSSR 暫存器的寫入操作。

---

### 2. 還可以再收 NVMe 命令嗎？PCIe 命令還可以收嗎？

這兩個層次的命令在規範中有嚴格的區隔：

#### (1) NVMe 命令（Admin / I/O Commands）：**不能再處理！**

- **常規 Submission Queue 提交之命令**： 當進入 Subsystem Shutdown（`CSTS.SHST` 為 `01b` 處理中，或 `10b` 已完成）時，規範明訂**控制器不得再處理 Admin 與 I/O 命令**（Figure 85: Controller able to process Admin and I/O commands = No）。
    - 處理中時提交的指令，控制器會以 `Commands Aborted due to Power Loss Notification` 狀態碼予以中止。
    - 關機完成後（`CSTS.SHST = 10b`），若主機在未先執行 NVM Subsystem Reset 的情況下繼續往 SQ 丟指令，規範定義其行為為**未定義（Undefined Behavior）**。
- _(例外)_：在帶外管理（NVMe-MI）中，只有極少數帶有 `Ignore Shutdown (ISH = 1)` 旗標的 Admin 指令才被允許存取媒體。

#### (2) PCIe 命令（PCIe Transactions / Commands）：**可以接收！**

- **匯流排層級交易（PCIe TLPs）**： PCIe 匯流排讀寫（Memory Read/Write TLP、Configuration Read/Write TLP）**完全正常運作**。主機仍可自由讀取 `CSTS` 狀態暫存器、讀寫 PCIe Config Space，或是對 `NSSR` 寫入重置字串。
- **NVMe-MI 規範中的「PCIe Command Set」**： NVMe-MI 定義的 PCIe Command（如 PCIe Configuration Read/Write、PCIe Memory Read/Write 等帶外命令），其規範特別明訂：**PCIe Commands 的執行獨立於控制器是否處於 Disabled 或 Reset 狀態，依然可以被正常處理**。

---

### 3. CSTS.ST 與 CSTS.SHST 之間的關係？

兩者皆位於 `CSTS`（Controller Status，Offset 1Ch）暫存器中，**`CSTS.SHST` 代表關機的「進度狀態」，而 `CSTS.ST` 則代表該關機的「種類與範圍」**：

|欄位|位元位置|數值與意義|
|:--|:--|:--|
|**`CSTS.SHST`**(Shutdown Status)|Bits 03:02|表示關機流程的進展：• `00b`：正常運作（未發起關機）• `01b`：關機處理中（Shutdown processing in progress）• `10b`：關機處理完成（Shutdown processing complete）|
|**`CSTS.ST`**(Shutdown Type)|Bit 06|當 `CSTS.SHST` 不為 00b 時有效，標示是哪一種關機：• **`0`：Controller Shutdown**（單控制器關機，由 `CC.SHN` 觸發）• **`1`：NVM Subsystem Shutdown**（全子系統關機，由 `NSSD.NSSC` 或 NVMe-MI 觸發）|

#### 兩者的互動關係：

1. **聯合判定狀態**：
    - `CSTS.ST = 0` 且 `CSTS.SHST = 10b` \(\to\) **單一控制器關機完成**。主機若想重新使用，只需將 `CC.EN` 設為 0 重置該控制器，再設為 1 重新初始化即可。
    - `CSTS.ST = 1` 且 `CSTS.SHST = 10b` \(\to\) **整個子系統關機完成**。此時修改 `CC.EN` 完全無效，**必須使用 NVM Subsystem Reset（或斷電重啟）才能清除 `CSTS.ST` 並恢復正常**。
2. **清除條件差異**：
    - 一般 Controller Level Reset（如 `CC.EN=0`）無法將 `CSTS.ST` 清除為 0；**只有 NVM Subsystem Reset 才能將 `CSTS.ST` 清為 `0` 且將 `CSTS.SHST` 清為 `00b`**。

---

### 4. 進行了 Subsystem Shutdown，Host 要看哪一個狀態確認 Subsystem Shutdown 完成？

Host 必須輪詢（Poll）**`CSTS` 暫存器（Offset 1Ch）**，確認滿足以下狀態組合：

> **`CSTS.ST == 1`** 且 **`CSTS.SHST == 10b`**

#### 規範的判定規則：

1. **就緒判定標準**： 當且僅當 **`CSTS.ST` 為 `1`（確認是子系統層級關機）** 且 **`CSTS.SHST` 轉為 `10b`（關機處理完成）** 時，才代表 NVM Subsystem 內部快取已完全保存完畢，媒體處於安全 Shutdown 狀態，可以安全切斷主電源（Ready to be powered off）。
2. **多控制器環境要求**： 若子系統具備多個 Controller（或屬於同一 Domain），規範強制要求：**子系統只有在確認所有內部運作就緒後，才會將所有 Controller 上的 `CSTS.SHST` 同步轉移為 `10b`**。因此 Host 檢查發起關機的該控制器（或檢查該網域內所有控制器）的 `CSTS.ST == 1` 與 `CSTS.SHST == 10b` 即可確認完成。
3. **逾時等待依據**： Host 應參考 Identify Controller 資料結構中的 **`NSSL`（NVM Subsystem Shutdown Latency）** 作為輪詢等待的最長時間依據（若未回報或為 0h，規範建議至少等待 30 秒）。

---

💡 若需要了解驅動程式在執行 NVM Subsystem Reset 之後，重新進行 Controller 枚舉與 AQA / ASQ / ACQ 初始化（Section 3.5）的標準步驟，我也可以為您整理對照流程！