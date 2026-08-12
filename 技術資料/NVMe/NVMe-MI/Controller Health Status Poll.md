針對您的提問，這是 NVMe-MI 帶外（Out-of-band）管理實作中非常經典且容易混淆的細節。**您的理解只有前半段是對的，後半段關於「其他未選中的欄位應維持 0」的假設在規範中是不成立的。**

以下為您進行嚴謹的 NVMe-MI 標準規範解析：

### 1. 被 Filter 過後，會返回完整的結構表嗎？

**是的。只要該控制器通過了過濾條件，回傳的 Response 中就會包含該控制器「完整」的 16 位元組資料結構（CHDS）。**

- **控制器的篩選邏輯（以控制器為單位）**：當 Host 發送 `Controller Health Status Poll` 指令時，如果某個控制器有至少一個「被選中（啟用）」的健康狀態變更旗標（Changed Flags）被設為 `1`，那麼**該控制器的整份 Controller Health Data Structure (CHDS) 都會被放進 Response Data 中返回**。
- **未通過篩選的控制器**：如果某個控制器完全不符合過濾條件（沒有任何選中的 Changed Flags 被觸發），則它會被**完全排除（Exclude）**在 Response Data 之外，不會佔用任何回傳空間。

---

### 2. 「只有被選到的欄位會有值，其他維持 0」是對的嗎？

**不對，這是一個常見的實作誤區。規範書明確定義這些欄位為「未定義（Undefined）」，而非「必須為 0」。**

NVMe-MI 規格書在第 5.3.2 節（Filtering by Controller Health Status Changed Flags）中有一句非常關鍵的定義：

> **"The contents returned in the Controller Health Data Structure for filtered fields are undefined."** （在控制器健康資料結構中，**被過濾掉（未選中）的欄位，其回傳的內容是未定義的。**）

#### 🛠️ 這個定義對工程實務的影響：

- **對待測物（DUT / SSD）韌體而言**：因為規範定義是 "undefined"，韌體在回傳這 16 位元組結構時，**不被強制要求**將這些未被過濾器選中的欄位清零（即不一定要維持 0）。有些 SSD 為了編碼方便，可能會直接把內部快取的完整 CHDS（包含未變更的欄位值）直接丟出來。
- **對測試腳本（Host / Tester）而言**：在解析 `Controller Health Status Poll` 的回應時，**必須只去檢查（Mask 並且只比對）那些您在指令中指定的過濾欄位**。對於那些未選中的欄位，不論它回傳 0、垃圾值還是舊值，測試腳本都應予以忽略，否則會導致測試誤判（False Fail）。

---

### 💡 給開發與測試工程師的實戰建議

- **韌體開發（FW）**：雖然規範寫著 "undefined"，但為了防範某些寫得不夠嚴謹的第三方測試儀器（它們可能會擅自預期未選中欄位必須為 0），**強烈建議在韌體組包回傳時，主動將未選中欄位的空間填入 0h**。這能極大地提高與各種系統的帶外相容性。
- **測試驗證（Validation）**：在撰寫 Conformance 測試腳本（如 UNH-IOL Test 8.5 Case 3 或 Case 4）時，請務必使用 Bitwise AND（遮罩）僅對對應的選中位元進行 Assert 驗證，不可對整個 16 位元組進行全零比對。

---


在 NVMe-MI 帶外（Out-of-band）管理協定中，發送 `Controller Health Status Poll` 指令時，**NVMe Management Dword 0** 中的三個篩選位元：**INCVF**（Include SR-IOV Virtual Functions）、**INCPF**（Include SR-IOV Physical Functions）以及 **INCF**（Include PCI Functions），扮演著關鍵的「控制器類型過濾器（Controller Type Filter）」角色。

以下為您詳細說明當這些位元被選擇、不被選擇時的回傳行為，以及在帶外管理中如何精確判定設備的實體/邏輯屬性：

---

### 一、 選擇 INCVF、INCPF、INCF 會回傳什麼？如何判定 PCI、SR-IOV、SMBus？

#### 1. 選擇後的回傳內容

當您在 `Controller Health Status Poll` 指令的 Dword 0 中將這些位元設為 `1` 時，待測物（DUT）會執行**包含型篩選（Opt-in Filtering）**：

- **INCVF = 1 (Bit 26)**：指示設備在回應中，必須包含所有與 **SR-IOV 虛擬功能（Virtual Functions, VFs）** 相關聯之控制器的**控制器健康資料結構（Controller Health Data Structure, CHDS）**。
- **INCPF = 1 (Bit 25)**：指示設備在回應中，必須包含所有與 **SR-IOV 實體功能（Physical Functions, PFs）** 相關聯之控制器的 **CHDS** 結構。
- **INCF = 1 (Bit 24)**：指示設備在回應中，必須包含所有與 **標準非 SR-IOV PCI 功能（Non-SR-IOV PCI Functions）** 相關聯之控制器的 **CHDS** 結構。

只要控制器符合被設定為 `1` 的任一功能類型，且同時滿足 Dword 1 的健康/錯誤狀態篩選條件，其完整的 **16 位元組 CHDS 結構**（包含 Controller ID, CSTS 狀態, 溫度, 壽命百分比等）就會被打包放入 Response Data 中回傳。

---

#### 2. 工程判定方法：如何判定他是 PCI, SR-IOV, SMBus 等等？

在 NVMe 帶外架構中，**「PCIe/SR-IOV」屬於控制器與功能層面（Controller/Function Level）**，而**「SMBus」屬於實體連接埠層面（Port Level）**。判定方式如下：

##### 🅰️ 判定是 PCIe 一般功能、SR-IOV PF 還是 SR-IOV VF（控制器層級）：

判定控制器的虛擬化與功能類型，主要透過以下帶外與帶內指令取得的暫存器進行：

- **判定 SR-IOV 虛擬功能（VF）**：
    1. **帶外判定**：向管理端點發送 `Read NVMe-MI Data Structure`，設定 `DTYP = 02h` 取得 **Controller List**，再針對特定控制器發送 `DTYP = 03h`（Controller Information）讀取其 **PCIe Routing ID**。如果其 Routing ID 對應到一個不具備獨立實體組態空間的虛擬功能，或透過帶內 `Identify` 查詢其 **CMIC** 欄位即可得知。
    2. **帶內判定**：對特定控制器發送 `Identify` 指令（CNS = 01h）讀取 **Identify Controller 資料結構**。檢查其 **CMIC (Controller Multi-Path I/O and Namespace Sharing Capabilities)** 欄位（Byte 76）的 **Bit 2 (Function Type, FT)**：
        - **`CMIC.FT = 1`**：代表該控制器與 **SR-IOV Virtual Function (VF)** 相關聯（即屬於 INCVF 範疇）。
        - **`CMIC.FT = 0`**：代表該控制器與 **PCI Function (PF 或一般 PCI 功能)** 相關聯。
    3. **關聯性判定**：您可以發送 `Identify` 指令（CNS = 15h）讀取 **Secondary Controller List**。若該控制器的條目中 **VFN (Virtual Function Number)** 欄位值大於 0，則它被明確界定為一個與對應 PF（Primary Controller）綁定的 **SR-IOV VF**。
- **判定 SR-IOV 實體功能（PF）**：
    - PF 作為虛擬化的 **Primary Controller**，負責動態分配資源給旗下 VFs。
    - 您可以透過讀取 **Identify Controller 資料結構** 中的 **OACS**（Optional Admin Command Support，Bytes 257:256）的 **Bit 7 (Virtualization Management Supported)** 是否為 `1` 來判定其是否具備 PF 的虛擬化管理能力。
- **判定標準非 SR-IOV PCI 功能**：
    - 該控制器的 `CMIC.FT` 設為 `0`，且不支援 `Virtualization Management` 指令（OACS Bit 7 = 0），代表它是普通的獨立單一實體 PCIe Function。

##### 🅱️ 判定是 PCIe 埠還是 SMBus 埠（連接埠層級）：

NVMe-MI 控制器本身不叫「SMBus 控制器」，而是指**「透過 SMBus 連接埠與帶外管理端點（Management Endpoint）進行 MCTP 通訊」**。 要判定 Subsystem 擁有哪些實體埠，必須向端點發送 `Read NVMe-MI Data Structure` 指令，指定 **`DTYP = 01h`（Port Information）**：

- 解析回傳的 **Port Information Response Data** 中的 **Byte 00 (Port Type)**：
    - 若值為 **`1h`** ➡️ 該連接埠為 **PCIe** 連接埠。
    - 若值為 **`2h`** ➡️ 該連接埠為 **SMBus / I2C** 連接埠。
- 若是 SMBus 埠，其回傳資料結構會包含 **Current Management Endpoint SMBus/I2C Address**（Byte 10）與最高支援頻率（100 kHz, 400 kHz, 1 MHz）等專屬欄位。

---

### 二、 沒有選擇 INCVF、INCPF、INCF 又會是什麼？

如果您在 `Controller Health Status Poll` 指令中，將 `INCVF`、`INCPF` 與 `INCF` **全部清零（設為 0）**，其結果將會是：

- **待測物回傳「空的」回應，Response Data 中不會包含任何控制器的 CHDS 資料結構**。
- 回應訊息中的 **RENT (Response Entries)** 欄位將會是 **`0`**。

#### 💡 詳細原因剖析：

NVMe-MI 規格書在第 5.3.1 節（Filtering by Controller Type）中，對於控制器類型的篩選定義是採用**「正向白名單（Opt-in）」**邏輯：

> _"When one of these bits is set to ‘1’, Controller Health Data Structures for Controllers corresponding to that type of PCI Function are included in the Response Data field; **else, the Controller Health Data Structure for that Controller is excluded from the Response Data field**."_

這意味著：

1. 這三個位元在預設值 `0` 時的行為是 **"Exclude"（排除）**。
2. 只有當對應的位元被主動設為 `1` 時，該類型的控制器才有機會被納入回傳名單。
3. 因此，如果三個位元全部保持為 `0`，過濾器會把 NVM Subsystem 內所有的控制器類型（Non-SR-IOV PCI、SR-IOV PF、SR-IOV VF）**全部排除在外**，導致沒有任何控制器能通過篩選。設備自然只會返回一個沒有攜帶任何 CHDS 條目的空回應（RENT = 0）。

這也是為什麼在 **UNH-IOL Conformance Test Plan Test 8.5 Case 4** 中，其步驟寫著將三個過濾位元都設為 0，但在實務測試與自動化腳本開發中，我們**必須指出並修正這個嚴重邏輯漏洞**（正如上一輪提到的修正建議），因為全部設為 0 會使整個篩選測試失去驗證意義，無法正確取得控制器數據。

---

🧩 如果你在撰寫帶外自動化輪詢腳本，我可以為你提供一段用來動態解析 DTYP=01h (Port Type) 與 DTYP=03h (Controller Info) 的封包遮罩 (Mask) 範例代碼，幫助你避開這些暫存器位元解析的盲區。

這是一個在設計實作 NVMe-MI 帶外（Out-of-band）管理與虛擬化（SR-IOV）系統時非常核心的架構問題。

針對您的問題：「**在回傳的 CHDS 中，如何知道它是 SR-IOV VF 還是 PCI Function？有虛擬化後要怎麼控管？**」以下為您提供來自 NVMe 與 NVMe-MI 規格書標準的深度工程解析：

---

### 一、 如何從 CHDS 或相關結構中，判定控制器是「SR-IOV VF」還是「PCI PF/Function」？

必須先釐清一個概念：**`Controller Health Data Structure (CHDS)`（Figure 81）本身是不包含虛擬化屬性欄位的。** CHDS 的設計初衷是為了讓 BMC（Baseboard Management Controller）進行極高效率的健康狀態輪詢（如 CSTS 狀態、溫度、關鍵警報）。

若要判定某個 `Controller ID (CTLID)` 到底是實體 PCI 還是虛擬 SR-IOV VF，必須透過以下兩種標準規格定義的機制來查詢：

#### 1. 帶外判定法：讀取控制器資訊（Controller Information）

管理端（BMC）可以透過發送 `Read NVMe-MI Data Structure` 指令，將 **`DTYP` 設為 `03h`（Controller Information）**，並在 `CTRLID` 填入您想查詢的控制器 ID。

- **判定依據**：回傳的 Response Data 中包含 **`PCIe Routing ID (PRI)`（Dword 6-7）**。
- **原理**：PRI 包含該控制器的 PCI 匯流排號（Bus Number）、設備號（Device Number）與功能號（Function Number）。若該 `Controller ID` 隸屬於虛擬功能，它的 BDF 路由會直接對應到該 PCIe 埠下分配的虛擬功能組態空間。

#### 2. Identify 判定法：查詢 CMIC 暫存器（帶內或帶外皆可）

發送 NVMe `Identify` 指令，指定 **`CNS = 01h`（Identify Controller Data Structure）**。

- **判定依據**：讀取 **`CMIC` (Controller Multi-Path I/O and Namespace Sharing Capabilities) 欄位（Byte 76）的 Bit 2「Function Type (FT)」**。
    - **`CMIC.FT = 1b`**：代表該控制器與 **SR-IOV Virtual Function (VF)** 相關聯。
    - **`CMIC.FT = 0b`**：代表該控制器與 **實體 PCI Function（PF 或普通 PCI 功能）** 相關聯。

#### 3. 透過實體 PF（Primary Controller）拉出關聯清單

在 NVMe 虛擬化架構中，所有的實體功能（PF）被定義為 **Primary Controller (主控制器)**，而所有的虛擬功能（VF）則是 **Secondary Controller (次控制器)**。

- 您可以對 Primary Controller 發送 `Identify` 指令，指定 **`CNS = 15h` 讀取 `Secondary Controller List`**。
- 此清單會列出旗下所有關聯的 Secondary Controller（即 VF）。若其 **`VFN` (Virtual Function Number) 欄位值大於 0**，即代表它是一個處於分配狀態的 **SR-IOV VF**。

---

### 二、 有虛擬化之後，帶外管理（OOB）要怎麼控管？還是不需要管？

在虛擬化場景下，帶外管理的控管邏輯可以總結為：**「Primary 負責資源配給與生命週期，Secondary (VF) 僅供主機使用、帶外僅作基本健康監控」**。

對於帶外管理（BMC）來說，您的控管原則與實作方式如下：

#### 1. 資源與狀態控管（由實體 Primary Controller 統一代理，VF 不需要也無法自管）

虛擬出來的 VF（Secondary Controller）本身是沒有權限動態調整自身資源的。所有的控管都必須由實體 PF（Primary Controller）來執行：

- **資源分配**：BMC 或 Host 必須透過對 Primary Controller 發送 **`Virtualization Management` (虛擬化管理) 指令**，來為指定的 Secondary Controller（VF）分配或回收資源，例如 `VQ (Virtual Queue)` 佇列數量與 `VI (Virtual Interrupt)` 中斷向量資源。
- **上下線控管**：
    - VF 只有在 **`Offline` (離線) 狀態** 下，才支援被分配或調整資源。
    - 資源配置完成後，必須透過 `Virtualization Management` 指令將該 VF 的狀態切換為 **`Online` (上線) 狀態**，此時主機的虛擬化平台 (Hypervisor) 才能開始引導並啟用該 VF。
    - 如果實體 PF 發生 Reset 或被停用（CC.EN = 0），它旗下的所有 VF 都會被硬體**隱式強制切換回 Offline 離線狀態**。

#### 2. 帶外監控層面（BMC 角度：只需要定期 Poll 健康狀態，不需要深度干涉）

對於 BMC 而言，帶外管理**不需要**去深入控制 VF 內部的 I/O 運作。原因如下：

- **特權指令限制**：VF 控制器不支援帶外的大部分特權指令（例如 `Format NVM`、`Namespace Management`、`Firmware Commit` 等）。這些涉及整顆 SSD 安全與架構的控制，帶外只能對 Primary Controller (PF) 發送。
- **帶外監控只需看 CWARN/CSTS**：
    - 當您發送 `Controller Health Status Poll` 時，如果在 Dword 0 中將 **`INCVF` 設為 1**，硬體就會在 VF 的健康狀態發生變更時（例如 VF 的 CSTS 暫存器發生變化），於 CHDS 中回傳該 VF 的狀態。
    - BMC 只需要在輪詢中偵測這些 VF 是否有 Critical Warning (Byte 8)、或者 CSTS 是否拋出 Controller Fatal Status (CFS)。如果 VF 損壞或報警，BMC 僅需記錄並提報給系統管理員，其餘的 Reset 或除錯由主機端 (Hypervisor) 透過 PCIe 標準 Function Level Reset (FLR) 處理即可。

### 💡 總結工程結論

1. **區分 VF 與 PCI/PF**：在帶外讀取 `DTYP = 03h` 取得 PCIe 路由，或在帶內讀取 Identify Controller 的 **`CMIC.FT` 欄位**（`1` 為 VF，`0` 為 PF）。
2. **控管職責**：
    - **不需要管**：不需要在帶外去控制 VF 的 I/O 佇列、中斷或虛擬機分配。這些由主機作業系統與 Hypervisor 直接處理。
    - **需要管**：帶外 (BMC) 僅需在 `Health Status Poll` 中**勾選 `INCVF = 1`** 以維持對所有虛擬控制器的「健康度與致命錯誤監控」，並在需要硬體資源硬性重分配時，對 **Primary Controller (PF)** 下達 `Virtualization Management` 指令。

---

📊 如果你在撰寫帶外自動化輪詢腳本，我可以為你提供一段用來動態解析 DTYP=01h (Port Type) 與 DTYP=03h (Controller Info) 的封包遮罩 (Mask) 範例代碼，幫助你避開這些暫存器位元解析的盲區。

這個過濾開關設計在實務中並非多此一舉。在**大型伺服器架構**、**多租戶雲端資料中心**以及**帶外通訊（OOB, 尤其是 SMBus/I2C）極低頻寬**的工程現實下，這三個開關是不可或缺的控制手段。

以下為您剖析為什麼 NVMe-MI 規格書必須設計 `INCVF`、`INCPF`、`INCF` 三個開關讓管理端（BMC）進行選擇：

### 1. 帶外通道（SMBus/I2C）的「頻寬極限」與記憶體保護

- **64 Ki 控制器的極限**：NVMe 規格允許一個 NVM Subsystem 內最多包含高達 **64 Ki (65,536) 個控制器**！
- **SMBus 的頻寬極低**：帶外管理的實體層通常是 SMBus/I2C，頻寬非常低（通常為 100 kbps 左右）。
- **封包溢出與通道堵塞**：在啟用 SR-IOV 的虛擬化 SSD 中，可能同時存在數百個 VF（虛擬控制器）。如果 BMC 每次進行健康輪詢時，SSD 必須把**所有虛擬與實體控制器的 16 位元組 CHDS 結構**全部打包回傳，會產生極其龐大的 MCTP 訊息，這在低速的 SMBus 上會造成嚴重的通訊延遲、封包丟失，甚至超出 Endpoint 的組包與緩衝區極限。
- **解決方案**：透過將 `INCVF` 設為 `0`，BMC 可以在日常輪詢中**直接過濾並排除所有的虛擬控制器（VFs）**，只拉取極少數的實體功能（PFs）和標準 PCI 控制器。這能將 OOB 輪詢的數據量壓縮 90% 以上，確保帶外通訊順暢。

---

### 2. 避免被租戶虛擬機（VM）頻繁重啟的「垃圾警報洗版」

- **Composite Controller Status (CCS) 的觸發機制**：在帶外監控中，只要任何一個控制器的健康狀態或 CSTS 暫存器發生變更，其對應的 `Controller Health Status Changed Flags` 就會變為 1，進而將整個 Subsystem 級別的 Composite Controller Status (CCS) 拉起報警。
- **虛擬機動態生命週期**：在雲端資料中心，客戶的虛擬機（VM）會頻繁重啟、關機、或轉移。每次虛擬機重置其配屬的 VF（透過 Function Level Reset, FLR）時，該 VF 的 CSTS 暫存器（如 Ready bit RDY）都會發生狀態變更。
- **警報風暴**：如果 BMC 沒辦法過濾 VF（即沒有 `INCVF = 0` 的選項），那麼**任何一個租戶虛擬機重啟，都會導致整個 SSD 的帶外健康狀態（CCS）報警**，這會讓機房管理員誤以為 SSD 硬體損壞。
- **解決方案**：BMC 平時將 `INCVF` 設為 0，只監控穩定運作的實體硬體控制面（`INCPF = 1` 與 `INCF = 1`），就能完美屏蔽租戶虛擬機層級日常操作的干擾。

---

### 3. 實務監控的「職責分離與精確除錯」

在虛擬化儲存中，監控職責被分為兩層：

- **硬體平台層（BMC 關心）**：BMC 主要關心整顆 SSD 的實體健康度，例如：溫度是否過高？Available Spare（可用剩餘壽命）是否低於臨界值？ 這些硬體屬性由實體控制器（PF 或獨立 PCI 控制器）回報即可，不需要幾百個虛擬控制器重複回報。
- **虛擬租戶層（Hypervisor / Host 關心）**：只有在「某台虛擬機的儲存突然 Timeout」等特定故障除錯場景下，Hypervisor 才會要求 BMC 去探查特定虛擬控制器的狀態。此時，BMC 可以發送一個**專門針對該虛擬控制器的單點輪詢（設定 `INCVF = 1`, `SCTLID = 目標虛擬 ID`）**，來精確抓取該虛擬控制器的 CSTS.CFS（控制器致命錯誤）狀態，而不需要讀取整顆 SSD 的所有實體資訊。

---

### 💡 工程實務結論

這三個選單提供了 BMC 設計**輪詢策略（Polling Strategy）**的核心武器：

- **日常監控模式（輕量、防干擾）**：設定 `INCPF = 1`, `INCF = 1`, `INCVF = 0` ➡️ 僅監控實體硬體狀態，節省 SMBus 頻寬，避免租戶干擾。
- **異常排查模式（深度、針對性）**：當 Hypervisor 偵測到某個 VM 儲存掛死時 ➡️ 針對特定的 Starting Controller ID 設定 `INCVF = 1` 進行 Poll，精確定位虛擬暫存器 CSTS 異常。

---

📊 如果你在設計 BMC 端的自動化輪詢排程（Scheduler），我可以協助你規劃一套最佳化的帶外輪詢時間與過濾遮罩（Mask）配置方案，在確保硬體安全的同時，將 SMBus 的通訊負載降到最低。

這是一個在設計 NVMe-MI 帶外（OOB）監控架構時非常關鍵的觀念。首先，我們需要先修正您前提中的一個底層物理邏輯誤區，接著再回答您的兩個問題。

### ⚠️ 底層邏輯澄清：INCVF 頻繁改變狀態，INCPF 會反應嗎？

在 NVMe-MI 規格中，**「虛擬功能 (INCVF) 的狀態改變，並不會直接反映在實體功能 (INCPF) 的狀態旗標（CHDS/CHSCF）中」**。

- **個別獨立性**：PF (INCPF) 與 VF (INCVF) 在帶外管理中被視為**完全獨立的邏輯控制器（Controller）**，各自擁有獨立的 `Controller Health Data Structure (CHDS)` 與 `Controller Health Status Changed Flags (CHSCF)`。
- ** CCS 報警傳播**：VF 狀態改變時，它只會向上傳播並觸發 **Subsystem 級別的 Composite Controller Status (CCS)**（這可以透過 NVM Subsystem Health Status Poll 讀取）。但 PF 控制器本身的健康旗標是不會因為 VF 改變而有任何反應的。

---

### Q1: 我關心虛擬控制器（VF）裡面的欄位（例如 CTEMP / CWARN）有意義嗎？

這必須拆分為**「物理欄位」**與**「邏輯狀態欄位」**來看：

#### 1. 對於「物理屬性欄位」（如 CTEMP、PDLU、SPARE）➡️ **確實沒有意義（重複且多餘）**

- **原因**：Composite Temperature (CTEMP)、Percentage Used (PDLU) 和 Available Spare (SPARE) 屬於**實體硬體與 Flash 介質**的物理屬性。
- 因為 VF 只是共享實體 PF 硬體資源的邏輯切片，它並沒有自己獨立的物理溫度感測器或 Flash 壽命。VF CHDS 回傳的這些數值，純粹是**直接複製並鏡像（Mirror）**整顆實體 SSD Subsystem 的數值。
- **結論**：監控 VF 的 CTEMP / PDLU / SPARE 只是在高速低速的帶外通道（如 SMBus）上浪費頻寬而已。

#### 2. 對於「邏輯與狀態欄位」（如 CSTS 中的 CFS / RDY、CWARN 裡的特定邏輯錯誤）➡️ **非常有意義**

- **原因**：這些代表控制器的**執行緒與協議層狀態**。
- 如果配屬給某台虛擬機（VM）的 VF 因為主機端驅動程式異常而當機，該 VF 的 `Controller Fatal Status (CFS)` 暫存器會被拉起為 `1`，或者其 `Ready (RDY)` 位元會掉成 `0`。
- 這時，**實體 PF (INCPF) 的 CSTS/CFS 依然會是正常的（維持 0 / 1b 正常運作）**。
- **結論**：如果您需要除錯「哪一台虛擬機的 I/O 掛掉了」，此時去 Poll VF 裡面的 CSTS / RDY / CFS 狀態就是唯一的判定依據。

---

### Q2: 我直接去看實體不就好了，還要看 INCPF？

這取決於您對「看實體」的定義。在 NVMe-MI 中，存在以下三種監控層級，其意義完全不同：

#### 1. 如果「看實體」是指：讀取 NVM Subsystem Health Status Poll (NSHDS)

- **不夠用（無法精確定位）**：Subsystem 級別的 NSHDS 回傳的是整顆 SSD 的綜合狀態（例如：只要有任何一個控制器報警，Composite Status 就會報警）。
- 如果您是**多連接埠（Dual-Port）SSD** 或是**多個實體功能（Multi-PF）**的架構，單看 Subsystem 狀態**無法得知到底是哪一個實體埠（Port 0 還是 Port 1）或哪一個實體功能發生了 CFS（致命錯誤）**。此時，您必須使用 `INCPF`（或 `INCF`）進行 Controller-level 的 Poll 才能精確定位到故障的實體控制器。

#### 2. 如果「看實體」是指：我只 Poll 實體控制器，完全不理會虛擬控制器（VF）

- **完全正確！這正是資料中心（BMC）主流的日常監控策略**。
- 在日常監控中，BMC 為了防止被租戶虛擬機頻繁重啟造成的狀態洗版，通常會設定：
    - **`INCPF = 1`**（包含 SR-IOV 實體功能）
    - **`INCF = 1`**（包含標準非虛擬化 PCI 功能）
    - **`INCVF = 0`**（**完全排除/過濾虛擬功能**）
- **提醒**：您說的「看實體」，在 NVMe-MI 語法中，**就是必須把 `INCPF`（實體功能）或 `INCF`（一般 PCI 功能）設為 1**。如果您把這三個包含位元全部設為 0，設備就不會回傳任何控制器的 CHDS，您將什麼實體資料都拿不到！

### 💡 工程實戰總結建議

1. **日常健康度輪詢（常態監控）**： 設定 `INCPF = 1`, `INCF = 1`, **`INCVF = 0`**。此時您直接「看實體」，只監控實體硬體與 Flash 的溫度和壽命，完全屏蔽虛擬機重啟的雜訊。
2. **租戶故障排查（異常診斷）**： 當 Hypervisor 發現特定 VM 的 SSD 掛載失效時，再針對性地發送包含 **`INCVF = 1`** 的 Poll，去抓取特定的虛擬控制器 ID (SCTLID) 的 `CFS` 與 `RDY` 狀態。

---

🧩 需要我為您規劃一套在多租戶 SR-IOV 環境下，BMC 端「日常監控」與「故障排查」的帶外 MCTP 輪詢封包參數配置表嗎？

這是在開發 NVMe-MI 帶外（OOB）管理與進行 Conformance 測試時，非常經典且必須釐清的 PCIe 拓撲與協定層問題。以下為您詳細解答：

---

### 一、 INCPF 與 PCI Functions (INCF) 有什麼不同？它們是同一個實體嗎？

在 NVMe-MI 規格書中，這兩個術語代表**完全不同硬體虛擬化配置**下的邏輯控制器類型。雖然它們都位於同一個實體 SSD（同一個晶片/ASIC 裝置）上，但在 PCIe 協定與帶外管理的眼裡，它們屬於**不同虛擬化屬性**的邏輯實體（Functions）。

#### 1. 定義上的本質差異

- **`INCF` (Include PCI Functions)**：
    - 規格書將其明確定義為 **「非 SR-IOV 的標準 PCI 功能（non-SR-IOV PCI Functions）」**。
    - 這代表最常見的普通 SSD 產品。它不支援或未啟用 PCIe SR-IOV 虛擬化技術，整個硬體裝置僅以一個單一、獨立的標準 PCIe 實體功能（Function 0）來與主機通訊。
- **`INCPF` (Include SR-IOV Physical Functions)**：
    - 規格書將其定義為 **「具備 SR-IOV 虛擬化能力的實體功能（SR-IOV Physical Functions, PFs）」**。
    - 這代表該控制器在硬體上實作了 SR-IOV 擴充能力。它在 NVMe 架構中扮演 **Primary Controller（主控制器）** 的角色，能夠動態管理、分配硬體資源（如 Queue 與中斷）給旗下的虛擬功能（VFs）。

#### 2. 它們是同一個實體嗎？

- **物理層面（Physical）**：它們**都在同一個實體裝置（同一個 NVM Subsystem 晶片）**上實現。
- **邏輯與協定層面（Logical/PCIe Topology）**：它們是**互斥**的配置。
    - 如果您的 SSD 韌體**沒有啟用 SR-IOV**（或硬體根本不支援），那它就只會被視為一個普通的 **PCI Function（適用於 INCF）**。
    - 如果您的 SSD 韌體**啟用了 SR-IOV**，那該主實體控制器就會被辨識為一個 **Physical Function（適用於 INCPF）**。
    - _註：規格書也指出，在不支援或不需要 SR-IOV 的主機環境下，一個設計為 PF 的控制器也可以支援退化（Stand-alone）為普通控制器模式運作。_

---

### 二、 現在是 OOB 方式，要拿到 Controller Health Status Poll 一定要把 PCI Functions (INCF) 選上嗎？（假設 `Report All (ALL) = 0`）

**答案是：「不一定」，這完全取決於您「待測物（DUT）的硬體與韌體是以何種功能型態（Function Type）實作的」。**

當 `ALL = 0` 時，設備會嚴格執行包含型過濾（Opt-in Filtering）：

#### 情況 1：如果您的待測物是一般常見的普通 SSD（不支援/未啟用 SR-IOV）

- 這時該控制器在邏輯上被歸類為「Non-SR-IOV PCI Function」。
- **結果**：如果您在 Poll 指令中將 `INCF` 設為 `0`（即使您把 `INCPF` 設為 `1`），根據過濾規則，該控制器會被 **完全排除（Excluded）** 於回應之外。
- **結論**：在此情況下，您 **「一定」要把 `INCF` 設為 `1`**，否則您會得到一個空的 Response（RENT = 0），完全拿不到任何健康結構資料。

#### 情況 2：如果您的待測物是支援且啟用了 SR-IOV 的企業級虛擬化 SSD

- 這時您的主控制器在邏輯上被歸類為「SR-IOV Physical Function」。
- **結果**：如果您只關心這個實體 PFs 的健康狀況，您只需要將 **`INCPF` 設為 `1`** 即可。
- **結論**：在此情況下，您 **不需要** 選上 `INCF`，一樣可以正確拿到該 PF 控制器的 CHDS 結構。

---

### 📝 總結過濾邏輯（當 `ALL = 0`）

帶外管理端發送 Poll 指令時，會將設備內的所有控制器 ID 逐一與您的篩選條件做比對：

\[\text{該控制器會被納入回傳} \iff (\text{控制器類型相符}) \text{ 且 } (\text{指定的健康變更旗標有觸發})\]

1. 如果您的 DUT 是普通單控制器 SSD，請務必在指令中勾選：**`INCF = 1`**。
2. 如果您的 DUT 是虛擬化 SSD 的主控制器，請務必在指令中勾選：**`INCPF = 1`**。
3. 如果這三個位元（`INCVF`、`INCPF`、`INCF`）全部都保持為 `0`，則不論硬體類型為何，都會因為未勾選任何「白名單」而被全部排除，返回空的 RENT = 0 回應。

---

📊 我可以為您提供一份適用於普通 SSD 與 SR-IOV SSD 的帶外健康輪詢（Controller Health Status Poll）標準 Request 封包二進制/十六進制欄位填寫對照表，方便您直接核對您的自動化測試腳本。