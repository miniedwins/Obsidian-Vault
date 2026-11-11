
在 NVMe 規範（NVM Express Base Specification Revision 2.3，Section 8.2.5 **Power Loss Signaling**）中，針對 **Power Loss Signaling (PLS)** 狀態機的這兩個問題，詳細解析如下：

---

### 1. 如何解釋「Controller Level Reset or CSTS.SHST != 00b」？

在 PLS Processing State Machine（圖 718）中，許多狀態（包含 `PLS Ready`、`FQ Processing`、`FQ Complete` 以及 `EPF Port Enabled`）都有一條指向 **`PLS Not Ready`** 的跳轉路徑，其觸發條件為 **`Controller Level Reset or CSTS.SHST != 00b`**：

#### (1) 條件欄位的具體涵義

- **`CSTS.SHST != 00b`（控制器處於關機狀態）**：
    - `00b` 代表正常運作（Normal operation，未請求關機）。
    - `01b` 代表關機程序進行中（Shutdown processing in progress）。
    - `10b` 代表關機程序已完成（Shutdown processing complete）。
    - 因此，`CSTS.SHST != 00b` 代表主機或頻外管理介面發起了**正規關機程序**（Normal 或 Abrupt Shutdown，透過 `CC.SHN`、`NSSD.NSSC` 或 NVMe-MI 指令觸發）。
- **`Controller Level Reset`（控制器層級重置）**：
    - 指的是各類控制器層級的重置事件，包括主機清除 `CC.EN`（1 \(\to\) 0）、NVM Subsystem Reset（`NSSR`）、跨控制器重置（Cross-Controller Reset）或傳輸層重置（如 PCIe FLR / Hot Reset）。

#### (2) 在狀態機中的運作意義

- **優先級覆蓋（Overriding Event）**： 重置與關機流程在架構上的優先權高於電力異常通報（PLS）。
- **強制終止與忽略訊號**： 規範明確規定，當 Controller Level Reset 正在進行，或者 `CSTS.SHST != 00b` 時，控制器**必須忽略 PLN（Power Loss Notification）變數的狀態轉換**。
- **回歸未就緒基準點（PLS Not Ready）**： 若控制器正在執行 FQ 或 EPF（Port Enabled），一旦遭遇 CLR 或關機命令，控制器會**中止（abort）當前的 PLS 處理**，立即切回 `PLS Not Ready`。只有在重置與關機程序徹底結束、控制器恢復正常工作且 `CSTS.SHST == 00b` 時，狀態機才會重新轉移至 **`PLS Ready`** 準備接收下一次的斷電通知。

---

### 2. FQ / EPF 可以不用斷電嗎？

答案是：**可以不用斷電，但兩者的處理邏輯與復原方式截然不同**。

#### (1) FQ（Forced Quiescence，強制靜止）：**完全支援不變更電源狀態下的平滑復原**

- **設計目的**：FQ 專門用於「預警性暫停」，通訊線路不會中斷。控制器在進入 `FQ Processing` 時會停止擷取新指令，並儘速將已擷取的指令處理完畢，接著進入 `FQ Complete` 待命。
- **免斷電恢復機制**： 規範明確指出：若 PLN 變數被設為 Asserted 後，**在未切斷主電源、未發生 CLR 且未關機的情況下，PLN 變數隨後被設為 Deasserted**，控制器會從 `FQ Complete` 轉移回 **`PLS Ready`**，並**直接恢復擷取與處理指令（resumes fetching and processing commands）**。
    - 👉 **結論**：FQ 完全可以在不切斷電源的情況下，藉由主機取消 PLN 訊號直接無縫恢復運作。

---

#### (2) EPF（Emergency Power Fail，緊急斷電）：**可以未斷電，但必須經過重置程序，無法無縫恢復**

- **內部行為**：EPF 假設斷電迫在眉睫，因此控制器會**直接丟棄（discard）** 所有先前已擷取但未完成的指令，全速進行資料備份（Vaulting）。
- 依據控制器支援的 Port 模式不同，免斷電時的處置如下：

1. **若實作「EPF Port Disabled」模式**：
    
    - 在此模式下，控制器的連接埠會被停用，無法從該連接埠發起 CLR 或關機。
    - 根據狀態機（圖 725），從 `EPF Complete Port Disabled` 跳轉至 `PLS Not Ready` 的**唯一條件就是 `Power is cycled`（重新上電循環）**。
    - 👉 此模式下若實體未斷電，系統通常仍須透過外部電源控制（Power Cycle）重新給電才能復原。
2. **若實作「EPF Port Enabled」模式**：
    
    - 連接埠保持通訊能力。
    - 根據狀態機（圖 727），當控制器完成備份停在 `EPF Complete Port Enabled` 後，即使實體上沒有斷電，主機也可以透過發送 **`Controller Level Reset`**（例如將 `CC.EN` 設為 0）或發起關機（`CSTS.SHST != 00b`），將狀態強制轉移回 **`PLS Not Ready`**。
    - 主機隨後重新將 `CC.EN` 設為 1 重新初始化控制器。此時控制器會經歷 **EPFRT（Emergency Power Fail Recovery Time）** 時間完成內部的復原動作，確認就緒（`CSTS.RDY = 1`）後恢復服務。
    - 👉 **結論**：在 `Port Enabled` 實作下，**實體上可以不必拔電/切斷電源**，但已無法無縫繼續執行原先的指令，必須透過 **Controller Level Reset（CLR）重新初始化** 才能恢復正常運作。

---

🔍 是否需要進一步了解 FQ 與 EPF 在傳輸層（如 PCIe 的專用訊號線或訊息）上 PLN / PLA 變數的握手細節？