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