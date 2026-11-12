
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

===========================================================================

根據 **NVM Express Base Specification Revision 2.3（Section 8.2.5 Power Loss Signaling）** 的狀態機定義與處理流程，針對這兩個問題的詳細解答如下：

---

### 1. PLN Assert 後，FQ / EPF 還在進行中，若此時 PLN Deasserted，會回到 `PLS Not Ready` 還是 `PLS Ready`？

答案取決於控制器目前處於 **FQ** 還是 **EPF** 模式：

#### (1) 若處於 FQ（Forced Quiescence，強制靜止）

- **不會立即中斷當前處理**：在狀態機中，`FQ Processing` 狀態**沒有**因為「PLN Deasserted」而直接跳轉的邊界條件。控制器會繼續把當前處理完畢，並先轉移至 **`FQ Complete`**。
- **最終回到 `PLS Ready`**：
    - 當控制器進入 `FQ Complete` 後，轉移條件中明確規範：當 **`PLN variable is set to Deasserted`** 時，狀態機會直接跳轉至 **`PLS Ready`**。
    - 規範同時指出：若 PLN 變數被設為 Asserted 後又被設為 Deasserted，且中間沒有發生斷電、Controller Level Reset 或關機，控制器會直接恢復指令的擷取與處理。
    - 👉 **結論**：FQ 進行中即使 PLN 提前 Deasserted，控制器完成 FQ processing 進入 `FQ Complete` 後，會**回到 `PLS Ready`**（不會回到 `PLS Not Ready`，除非中間有發起 Controller Level Reset 或關機流程）。

#### (2) 若處於 EPF（Emergency Power Fail，緊急斷電）

- **PLN Deasserted 在 EPF 狀態機中被完全忽略**：
    - 不論是 `EPF Processing Port Disabled` 還是 `EPF Processing Port Enabled`，狀態機中**完全沒有**因為「PLN Deasserted」而跳轉的路徑。控制器一旦觸發 EPF，就會丟棄已擷取的指令並執行緊急 Vaulting，直到進入 `EPF Complete`。
- **進入 `EPF Complete` 後的跳轉路徑**：
    - **Port Disabled 模式**：從 `EPF Complete Port Disabled` 跳出的唯一條件是 **`Power is cycled`（重新上電循環）**，這會強制轉移到 **`PLS Not Ready`**。
    - **Port Enabled 模式**：從 `EPF Complete Port Enabled` 跳出的唯一條件是 **`Controller Level Reset or CSTS.SHST != 00b`**，這也會強制轉移到 **`PLS Not Ready`**。
- 👉 **結論**：EPF 模式下，**絕對不會因為 PLN Deasserted 而自動回到 `PLS Ready`**。它必須在備份完成後，透過重置（CLR）或斷電重啟（Power Cycle）進入 **`PLS Not Ready`**，重新初始化後才有可能再度達到 `PLS Ready`。

---

### 2. 當 FQ / EPF 完成後，PLA 拉回 Deasserted，此時 PLN 應該也要 Deasserted，這段時間要多久？

針對 PLA 拉回 Deasserted 到主機端將 PLN 拉回 Deasserted 的時間間隔，NVMe 規範的定義如下：

1. **NVMe Base Specification 未規定固定超時時間（No fixed timeout in Base Spec）**：
    
    - 在 Base 規範架構中，**PLN 是由主機/傳輸層（Transport）或實體平台電源監控晶片驅動的輸入變數**，而 **PLA 則是控制器通知主機的輸出變數**。
    - 規範定義了控制器端所需的時間上限：
        - **FQVT（Forced Quiescence Vault Time）**：控制器從 PLN Assert 到完成 FQ 處理的最糟時間。
        - **EPFVT（Emergency Power Fail Vault Time）**：控制器完成 EPF 緊急備份的最糟時間。
    - 控制器在完成處理後，會自動將 PLA 設為 `Deasserted` 並進入 Complete 狀態。但規範**並未**對「主機端何時必須把 PLN 拉回 Deasserted」訂定強制秒數限制（例如 X 毫秒內必須 Deassert）。
2. **該時間長短由兩種實際系統情境與傳輸層規範決定**：
    
    - **情境 A：實際發生斷電（Normal Power Loss）**：
        - 主機/平台在偵測到供電異常並觸發 PLN 後，主機**根本不會**把 PLN 拉回 Deasserted。
        - 系統後備電源（Hold-up cap / 儲能電容）只需維持供電大於 **FQVT / EPFVT**，待控制器將 PLA 變數拉為 Deasserted 代表資料保存完畢後，主電源便直接中斷斷電（Power Removed）。
    - **情境 B：虛警、預警解除或工程測試（Power Loss Warning Cancelled / False Alarm）**：
        - 若主機確認電源已穩定不需斷電：
            - 在 **FQ** 機制下，SSD 此時停在 `FQ Complete` 處於暫停服務狀態。**主機越快將 PLN Deasserted，控制器就能越快自動返回 `PLS Ready` 並恢復處理 I/O 指令**。
            - 在 **EPF** 機制下，由於必須依靠主機發送 Controller Level Reset 才能復原，因此 PLN 只要在發起 Reset 之前或隨 Reset 一同解除即可。
    - **傳輸層與硬體規格定義**：
        - 具體的訊號握手機制（如 PCIe 專用 Sideband 針腳或 In-band 訊息之 PLN/PLA 延遲與濾波要求），由各傳輸層規範（例如 _NVMe over PCIe Transport Specification_）以及伺服器平台的硬體 CPLD / BMC 電源管理時序邏輯自訂。

---

🔍 是否需要進一步了解 PCIe Transport Specification 中針對 PLN/PLA 硬體 Pin 腳（如 `PERST#` 或專用 Sideband）的電氣與時序定義？

===========================================================================
在 **NVMe Base Specification Revision 2.3** 與 **NVMe over PCIe Transport Specification Revision 1.4** 規範中，針對 PLN（Power Loss Notification）與 PLA（Power Loss Acknowledge）的握手時序與時間規範說明如下：

---

### 1. 發生 PLN Assert 多久後，PLA 需要 Assert？

- **規範的動作時序（Step 1 即刻拉起）**： 在 NVMe Base 規範中，當控制器處於 `PLS Ready` 狀態且偵測到 PLN 變數由 Deasserted 轉為 Asserted 時，狀態機會立即切換至 `FQ Processing` 或 `EPF Processing` 狀態。規範明訂控制器在進入處理狀態時，**所執行的第一動（Action 1）就是立即將 PLA 變數設為 Asserted**（`Asserted-FQ` 或 `Asserted-EPF-Enabled` / `Asserted-EPF-Disabled`）。
- **具體數值規範**：
    - **NVMe 協定層**：NVMe 規範**並未定義一個獨立的「PLN 到 PLA Assert 延遲暫存器欄位」**，而是以狀態機行為規範「進入處理即刻設置（in sequence step 1）」。
    - **實體/傳輸層（PCIe M.2 / Sideband 訊號）**： 在 PCIe 傳輸層中，實體接腳 `PLN#` 訊號觸發後會映射至控制器的 PLN 變數。若為多控制器（Multi-Controller）子系統，規範要求子系統必須確保在最後一次 `PLN#` 觸發後，所有控制器都必須先 Assert 其 PLA 變數後，才能再轉為 Deassert。實體電氣反應時間（如側帶訊號防彈跳與內部邏輯觸發延遲）通常由具體硬體介面規範（如 PCI-SIG M.2 或平台硬體規格）定義，通常在**微秒級（\(\mu s\)）**內即完成拉起回應。

---

### 2. PLA 需要在多少時間內拉回 Deasserted？以及 PLN 確定 PLA 拉回後，PLN 多少時間要 Deasserted？

#### (1) PLA 需要在多少時間內拉回 Deasserted？

PLA 保持在 Asserted 的時間，代表控制器執行**電力中斷前置處理與資料保存（Vaulting）**的耗時。當控制器處理完成並進入 `FQ Complete` 或 `EPF Complete` 狀態時，才會將 PLA 變數設回 **Deasserted**。

這段時間的**最糟時間上限（Worst-case time limit）**是由控制器在 **Identify Controller 的 Power State Descriptor（PSD，電源狀態描述元）** 中明確宣告的：

- **FQ 模式**：耗時上限為 **`FQVT`（Forced Quiescence Vault Time）** 搭配 **`FQVTS`（時間尺度單位）**。
- **EPF 模式**：耗時上限為 **`EPFVT`（Emergency Power Fail Vault Time）** 搭配 **`EPFVTS`（時間尺度單位）**。
- **時間單位**：時間尺度依 `FQVTS` / `EPFVTS` 可表示為 1 微秒、10 微秒、100 微秒、1 毫秒、10 毫秒、100 毫秒至 1 秒等單位。
- **結論**：控制器保證在不超過該電源狀態所回報的 **`FQVT`** 或 **`EPFVT`** 時間內，完成處理並將 PLA 拉回 Deasserted。

---

#### (2) 確定 PLA 拉回後，PLN 多少時間要 Deasserted？

NVMe 規範**並未對主機端訂定強制超時時間（No timeout defined for host PLN deassertion）**，其行為取決於系統當前所處的情境：

1. **真實斷電情境（Actual Power Loss）**：
    - 主機與伺服器電源管理模組在偵測到 PLA 拉回 Deasserted 後，代表 SSD 內部快取已成功刷入非揮發性媒體（Vaulting 完成）。此時**主機「不會」將 PLN Deasserted**，而是直接由電容放電完畢或由電源供應器切斷主電源（Main Power Removed）。
2. **虛警或警報解除情境（False Alarm / Cancelled Warning）**：
    - 若主機確定供電恢復穩定、無需斷電：
        - 控制器在 PLA 拉回 Deasserted 後，會停留在 **`FQ Complete`** 狀態待命。
        - 規範定義從 `FQ Complete` 轉移回正常 `PLS Ready` 的唯一條件即為 **`PLN variable is set to Deasserted`**。
        - 因此，**主機端越快解除 PLN（Deasserted），控制器就能越快自動返回 `PLS Ready` 並恢復指令的擷取與執行**。主機何時將 PLN 解除，完全由主機端平台電源監控晶片（如 CPLD/BMC）確認電源穩定後的控制時序決定。

---

🔍 是否需要進一步查詢 PSD 資料結構中 FQVT / EPFVT 的位元定義，或是多控制器子系統（Dual-port / Multi-controller）在處理 PLA 訊號聚合時的詳細握手要求？