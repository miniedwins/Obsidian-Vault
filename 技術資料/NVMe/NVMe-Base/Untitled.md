在 NVMe Base Specification（Revision 2.3）中，**FID Supported and Effects Data Structure（Figure 267）** 是 **Feature Identifiers Supported and Effects Log Page（LID 12h）** 的核心組成單元。

該 Log Page 大小為 1,024 Bytes，包含了 256 個 Feature Identifiers（FID 00h～FFh）的支援狀態與指令影響。每個 FID 分配一個 **4 位元組（32 位元 / 1 個 Dword）** 的 **FID Supported and Effects Data Structure**，用於向主機描述該 Feature 的支援度、作用範圍（Scope）以及執行 `Set Features` 修改後對系統狀態產生的副作用（Effects）。

---

### 欄位完整定義與內容說明（Figure 267）

|位元區間|欄位名稱|縮寫|詳細功能說明|
|:--|:--|:--|:--|
|**Bit 00**|**FID Supported**|**FSUPP**|**特徵支援旗標**：• **`1`**：控制器支援此 Feature Identifier (FID)。• **`0`**：控制器不支援此 FID；此時該結構的所有其他欄位必須強制清為 `0h`。|
|**Bit 01**|**User Data Content Change**|**UDCC**|**使用者資料內容變更影響**：• **`1`**：修改此 Feature 的屬性可能會變更一個或多個 Namespace 內的使用者資料內容（例如抹除、重構或覆寫）。• **`0`**：修改此 Feature 不會影響任何 Namespace 的使用者資料。|
|**Bit 02**|**Namespace Capability Change**|**NCC**|**單一命名空間能力變更**：• **`1`**：修改此 Feature 可能會改變單一 Namespace 的功能或屬性（例如邏輯格式變更）。• **`0`**：不影響指定 Namespace 的能力。|
|**Bit 03**|**Namespace Inventory Change**|**NIC**|**命名空間清單變更**：• **`1`**：修改此 Feature 可能會改變 Namespace 的數量或同時影響多個 Namespace 的功能（例如新增、刪除 Namespace）。• **`0`**：不會改變 Namespace 的數量或跨多個 Namespace 的能力。|
|**Bit 04**|**Controller Capability Change**|**CCC**|**控制器能力變更**：• **`1`**：修改此 Feature 可能會改變控制器本身的整體能力（例如透過韌體更新或設定改變了 CAP 暫存器回報的支援特性）。• **`0`**：不會變更控制器的基本能力。|
|**Bits 18:05**|**Reserved**|—|**保留欄位**，填 `0`。|
|**Bit 19**|**UUID Selection Supported**|**USS**|**UUID 選擇支援**：• **`1`**：控制器支援在對此 FID 發送 `Get Features` 或 `Set Features` 指令時，透過 CDW14 的 UIDX 指定特定供應商自訂的 UUID。• **`0`**：不支援 UUID 選擇。|
|**Bits 31:20**|**FID Scope**|**FSP**|**特徵作用範圍**：定義修改此 Feature 會影響系統架構中的哪一層級（詳見下方細分說明）。|

---

### 二、 特徵作用範圍細分（FID Scope, FSP：Bits 31:20）

**FSP（共 12 個位元）** 定義了此 Feature 影響的實體或邏輯範圍。規格明訂：

- 若 FSP 數值為 `0h`，代表不回報 Scope。
- **若 FSP 不為零，則在 Bits 26:20 之間只能有「剛好 1 個位元」被置為 `1`**（各 Scope 彼此互斥）：

1. **Bit 20（FSP Bit 0）— Namespace Scope (NSCPE)**：
    - 設為 `1` 表示此 Feature 的修改效果僅作用於**特定的單一 Namespace**。
2. **Bit 21（FSP Bit 1）— Controller Scope (CSCPE)**：
    - 設為 `1` 表示此 Feature 僅影響**該控制器本身**。
3. **Bit 22（FSP Bit 2）— NVM Set Scope (NSETSCPE)**：
    - 設為 `1` 表示此 Feature 的修改會影響所屬的 **NVM Set**。
4. **Bit 23（FSP Bit 3）— Endurance Group Scope (EGSCPE)**：
    - 設為 `1` 表示此 Feature 的修改會影響所屬的 **Endurance Group**。
5. **Bit 24（FSP Bit 4）— Domain Scope (DSCPE)**：
    - 設為 `1` 表示此 Feature 的修改會影響單一 **Domain（電源或故障隔離網域）**。
6. **Bit 25（FSP Bit 5）— NVM Subsystem Scope (NSSCPE)**：
    - 設為 `1` 表示此 Feature 的修改會影響**整個 NVM Subsystem（子系統中所有 Controller 與 Namespace 皆受影響）**。
7. **Bit 26（FSP Bit 6）— Controller Data Queue (CDQSCP)**：
    - 設為 `1` 表示修改此 Feature 的屬性可能會影響 **Controller Data Queue（控制器資料佇列）**。
8. **Bits 31:27（FSP Bits 11:7）— Reserved**：保留位元，填 `0`。

---

### 三、 主機如何運用這些欄位？

1. **安全配置與副作用防範**：
    - 當 Host 準備下發 `Set Features` 指令時，會先查詢 LID 12h。如果發現該 FID 的 **UDCC = 1** 或 **NIC = 1**，主機端驅動程式必須在修改設定前暫停（Pause）I/O 傳輸，並在設定完成後重新列舉（Re-enumerate）Namespace 或更新快取，以防資料損毀或不一致。
2. **跨控制器與多主機協調**：
    - 如果發現某個 Feature 具有 **NVM Subsystem Scope (NSSCPE = 1)** 或 **Domain Scope (DSCPE = 1)**，主機即可知曉此修改將會影響到同一 Subsystem 下的其他 Controller，必須進行跨主機或跨路徑的協調處理。

🔍 需要我為您列出常見 Feature（如 LBA Range Type 03h、Volatile Write Cache 06h 或 Host Behavior Support 16h）在實務上回傳的標準 FSP 與 Effects 位元範例嗎？

======================================================================
這是一個非常核心且常見的盲點。關鍵在於：**Log Page（日誌頁）本身確實是「唯讀的靜態宣告/狀態報告」，但它所描述的對象（Feature）是可被修改的**。

您讀取 **LID 12h（Feature Identifiers Supported and Effects Log Page）** 時，並不是在修改 Log Page，而是**裝置在向主機（Host）「自我介紹」它內部有哪些 Feature**：

> 「我支援哪些 Feature（例如電源管理、快取開關、多重佇列）？如果主機之後發送 **`Set Features`（Opcode 09h）** 來**修改**這些 Feature 的設定值時，會對我的硬體、命名空間或資料產生什麼**副作用（Effects）**？」

---

### 一、 為什麼說「修改 Feature 的屬性」？

在 NVMe 體系中，**Feature（特徵，如 FID 01h～FFh）是 SSD 的各項運作參數**（例如：啟用揮發性寫入快取、調整電源模式、設定溫度門檻、配置主機記憶體緩衝區 HMB 等）。

1. **Host 如何「修改 Feature」？**
    - 主機下發 **`Set Features`（Opcode 09h）** 指令，把某個 Feature 的屬性改掉（例如把 FID 06h 的寫入快取從 Enable 改成 Disable，或是改變 FID 22h Configurable Device Personality）。
2. **Log Page 的角色：**
    - **LID 12h Log Page 是一張「唯讀的後果預告清單」**。
    - 每個 FID 的 4 個 Bytes 結構（FID Supported and Effects Data Structure, Figure 267），就是在告訴 Host：**「如果你透過 `Set Features` 改了這個 FID，會牽連（Impact）到系統的哪些層面？」**

---

### 二、 這些屬性修改後，會帶來什麼具體影響？（以實例說明）

在 Figure 267 中定義的各個位元（Effects & Scope），就是規格書定義的**「修改副作用與影響範圍」**：

#### 1. 影響旗標（Effects Bits: 04:01）

- **UDCC (User Data Content Change, Bit 01) — 使用者資料可能變更/抹除**：
    - **代表情況**：例如有些裝置支援進階的 **FID 22h（Configurable Device Personality, CDP）**。如果 Host 透過 `Set Features` 將裝置的 Personality 從一般模式切換為極速模式或安全性模式，SSD 內部的快閃記憶體劃分可能完全重置，導致**原本存放的使用者資料全部被抹除或無效化**。
    - **主機應對**：驅動程式看到 UDCC = 1，就知道在改這個 Feature 之前，**必須先把重要資料備份或刷入永久媒體**。
- **NCC (Namespace Capability Change, Bit 02) — 單一 Namespace 能力改變**：
    - **代表情況**：修改了特定 Namespace 的特徵（例如邏輯格式或資料保護模式支援變更）。
    - **主機應對**：設定完畢後，主機必須對該 Namespace 重新發送 `Identify Namespace` 重新辨識。
- **NIC (Namespace Inventory Change, Bit 03) — Namespace 清單或數量改變**：
    - **代表情況**：改動這個 Feature 可能會導致某些 Namespace 被自動建立、卸載或刪除（清單個數變了）。
    - **主機應對**：主機必須重新掃描（Re-scan）整個裝置的 Namespace 清單（例如發送 `Identify CNS 02h Active Namespace ID list`）。
- **CCC (Controller Capability Change, Bit 04) — 控制器整體能力改變**：
    - **代表情況**：變更了某些全域設定後，控制器的硬體能力（例如 PCIe 暫存器 CAP 回報的特性）產生了變化。
    - **主機應對**：驅動程式可能需要重新讀取控制器暫存器或重新初始化控制器。

#### 2. 作用範圍（FID Scope, Bits 31:20）

當 Host 送出 `Set Features` 改了某個參數，這個改動是**只影響自己**，還是**連隔壁的主機/控制器一起被影響**？

- **NSCPE (Bit 20) — Namespace 範圍**：只影響單一 LUN/Namespace（例如設定特定 Namespace 的寫入保護 FID 84h）。
- **CSCPE (Bit 21) — Controller 範圍**：只影響下指令的這個 Controller 本身（例如設定這台主機專屬的佇列數 FID 07h 或中斷聚集 FID 08h）。
- **NSSCPE (Bit 25) — 整個 NVM Subsystem 範圍**：這是最嚴重的範圍！表示改了這個 Feature（例如子系統安全抹除設定 FID 17h 或電源重置模式），**即使同一顆 SSD 上有其他實體埠、PF、VF 或其他主機連著，它們全部都會受到波及**。

---

### 三、 總結：主機實際上的操作流程

1. **Step 1（讀取 Log Page 預警）**：
    - 主機發送 `Get Log Page (LID 12h)`。
    - 讀出一個靜態的 1,024 Bytes 表格，確認 SSD 支援哪些 FID（FSUPP = 1），以及每個 FID 的影響位元（UDCC, NCC, NIC, CCC）與作用範圍（FSP）。
2. **Step 2（安全評估與暫停）**：
    - 主機打算下發 `Set Features` 調整設定。
    - 驅動程式查表發現該 Feature 的 **NIC = 1** 且 **NSSCPE = 1**，知道這會跨控制器變更 Namespace 清單，於是驅動程式**先暫停（Pause）所有進行中的 I/O 傳輸**。
3. **Step 3（執行修改並復原）**：
    - 主機發送 `Set Features`。
    - 指令完成後，驅動程式重新列舉（Re-enumerate）Namespace，確認狀態更新完成，再恢復正常的 I/O 讀寫。

因此，**Log Page 確實是固定的說明手冊**，它裡面的 Effects 欄位是為了**「讓主機在未來下達 `Set Features` 指令時，知道該做什麼防範措施」**。

===========================================================================

在 NVMe 規範（Base Specification）中，**NCC（Namespace Capability Change，Bit 02）** 與 **NIC（Namespace Inventory Change，Bit 03）** 是用來向主機預告「這個指令執行後，是否會對命名空間（Namespace）的能力或數量產生結構性變動」的影響旗標。

這兩個位元最常出現在 **Commands Supported and Effects (CS&E, Log Page 05h)** 以及 **FID Supported and Effects (Log Page 12h)** 中。針對您的問題，詳細解析如下：

---

### 1. 以 NCC 與 NIC 為範例，哪一個命令須要讓這兩個 Bit 為 1？

最標準且最具代表性的指令是 **`Namespace Management`（Admin Opcode 0Dh）**：

- **為什麼 NIC（Bit 03）必須為 1？**
    - 規範定義 NIC 為「**Namespace Inventory Change**」。當一個指令會**改變命名空間的數量（Adding or removing namespaces）**或一次影響多個命名空間時，此位元必須置為 `1`。
    - `Namespace Management` 支援 **Create（建立，SEL=0h）** 與 **Delete（刪除，SEL=1h）** 操作。執行後系統中的 Namespace 數量會直接增加或減少，清單隨之改變，因此 **NIC 必須為 1**。
- **為什麼 NCC（Bit 02）必須為 1？**
    - 規範定義 NCC 為「**Namespace Capability Change**」。當指令會**改變單一命名空間的功能或屬性（例如 Logical Format Change）**時，此位元必須置為 `1`。
    - 當使用 `Namespace Management (Create)` 重新配置一個新的 Namespace 時，其容量（NSZE/NCAP）、LBA 格式（FLBAS）、端到端資料保護（PI）等能力皆被重新定義；此外像 **`Format NVM`（Opcode 80h）** 在執行格式化改變 LBA 大小時，NCC 也必須為 1。

> **補充（若是 Set Features 指令）：** 若在 **FID Supported and Effects（LID 12h）** 中尋找範例，能讓 NCC/NIC 為 1 的則是 **`Set Features (FID 22h: Configurable Device Personality, CDP)`**。當主機切換裝置的 Personality 時，SSD 內部的快閃記憶體劃分可能完全重置，導致 Namespace 被重新劃分或清單重整。

---

### 2. 承第一點說明，如果硬體/韌體沒有設定為 1（誤設為 0），會發生什麼問題？

如果韌體在 CS&E 或 FID Effects 中把這兩個位元填為 `0`，裝置雖然仍能執行指令，但**主機端的驅動程式與作業系統（OS）會因為「缺乏後果預警」而引發嚴重系統異常甚至資料損毀**：

#### 問題一：主機端未暫停 I/O，導致資料存取到「幽靈」或「已刪除」的 Namespace

- **正常流程**：NVMe 規格書特別建議，當主機看到某個指令的 NCC/NIC 為 1 時，**必須在下發指令前先暫停（Pause）對該 Namespace 的所有 I/O 存取**。
- **未設為 1 的後果**：驅動程式誤以為該指令完全不影響 Namespace，於是在執行 `Namespace Management (Delete)` 時**並未暫停上層應用程式的讀寫**。這會導致進行中的 I/O 指令直接撞上正在被銷毀的 Namespace，大量爆出 `Invalid Namespace or Format`（SCT 0h, SC 0Bh）嚴重錯誤，甚至導致檔案系統崩潰或資料寫入遺失。

#### 問題二：主機端快取過期，不會主動重新列舉（Re-enumerate）

- **正常流程**：驅動程式在下發 NCC/NIC = 1 的指令完成後，會**自動重新下發 `Identify (CNS 00h / 02h)`**，重新辨識更新後的 Namespace 清單與屬性。
- **未設為 1 的後果**：
    - 主機 OS 的驅動程式仍然保留**舊的快取資訊（Stale Cache）**。
    - 例如：明明剛 Create 了一個新的 `NSID 2`，但主機驅動程式因為沒收到 NIC 預警，不知道要重新掃描 Active Namespace ID List（CNS 02h），導致**作業系統的磁碟管理員根本看不到剛建立的新硬碟**。
    - 又例如：執行格式化將 LBA Size 從 512B 改成 4KB（NCC 應為 1），若未告知主機，作業系統仍會用 512B 發送讀寫請求，造成後續所有的 LBA 存取產生嚴重的傳輸對齊與資料損壞問題。

#### 問題三：多主機 / 多路徑（Multi-path）環境無法協同保護

- 在多控制器（Dual-port / SR-IOV / NVMe-oF）共享 Namespace 的環境下，若 NIC/NCC 設為 1，其他控制器才能依據通知進行協調鎖定；若未設定，其他 Host/Controller 就無法即時同步該 Namespace 已失效或改寫的事實，造成跨路徑存取衝突。

#### 問題四：無法通過 UNH-IOL Conformance 規格合規性測試

- UNH-IOL 等官方認證測試套件在驗證 **Log Page 05h (Commands Supported and Effects)** 與 **Log Page 12h (FID Effects)** 時，會比對裝置支援的指令集與回報的 Effects 欄位；若支援 `Namespace Management` 但對應的 ACS 項目未將 NIC/NCC 置位，測試項目將直接被判定為 **FAIL**。

---

### 總結

- **指令範例**：**`Namespace Management` (Opcode 0Dh)**。
- **核心影響**：這兩個位元是作業系統的**「預警信號燈」**。如果設為 0，主機就會**「不暫停 I/O、不重新列舉 Namespace」**，最終導致應用程式 I/O 撞牆報錯、新硬碟找不到、或因格式改變而引發資料損毀。

