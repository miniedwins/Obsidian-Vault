在 NVMe 與 NVMe-MI 規範架構下，**NVMe Controller（控制器）** 與 **Enclosure Services Process（ESP，機櫃服務進程）** 之間的溝通主要建立在**「帶內通道隧道化（In-Band Tunneling）」**的標準協定架構之上；而控制器與 ESP 在晶片/韌體底層的實體介面，規格則定義為**實作自訂（Vendor Specific / Outside of Scope）**。

---

### 一、 協定層級：In-Band Tunneling 通訊機制

在標準軟體與韌體協定層面，Host 與 NVMe Controller 溝通機櫃資訊時，使用的是 **NVMe Admin 指令集** 來隧道化（Tunnel）傳遞 NVMe-MI 的機櫃指令：

1. **下達控制（Host \(\rightarrow\) Controller \(\rightarrow\) ESP）**：
    - Host 向 NVMe Controller 的 Admin Submission Queue 發送 **`NVMe-MI Send`（Opcode `1Dh`）** 指令。
    - 該指令內部封裝了 NVMe-MI Command Set 中的 **`SES Send`（Opcode `09h`）**。
    - 控制器解析該指令後，將其包含的 SES-3 Control Diagnostic Page（控制診斷頁面，例如指定開關哪顆 LED、調整風扇轉速）交付給 ESP 執行。
2. **讀取狀態（ESP \(\rightarrow\) Controller \(\rightarrow\) Host）**：
    - Host 向 NVMe Controller 發送 **`NVMe-MI Receive`（Opcode `1Eh`）** 指令。
    - 該指令內部封裝了 **`SES Receive`（Opcode `08h`）**。
    - 控制器向 ESP 要求對應的 SES-3 Status Diagnostic Page（例如機櫃溫度、電源供應器狀態、磁碟槽 Slot 狀態），並由控制器將資料填入 Host 的 Data Buffer 回傳。

---

### 二、 系統架構中的控制器角色：Administrative Controller

在具備 Enclosure 管理的大型儲存系統中，NVMe 規範特別定義了一種 **Administrative Controller（管理控制器）**：

- **專責機櫃管理**：Administrative Controller 不支援 I/O Queue，也不掛載任何 Namespace（無法進行一般的讀寫）。
- **核心使命**：主要用來實作 `NVMe-MI Send` 與 `NVMe-MI Receive`，專門作為管理介面負責與內部的 ESP 溝通，進行整個 NVMe Enclosure 的監控與元件控制。
- （一般的 I/O Controller 若在 `Identify Controller` 的 `OACS` 欄位宣告支援 `NVMe-MI Send/Receive Supported`，亦可兼具此溝通功能。）

---

### 三、 內部傳輸介面：標準範圍與實作自訂（Vendor Specific）

在 NVMe-MI 規格書（_NVM Express Management Interface Specification_）中，清楚劃分了標準化介面與內部實作的邊界：

```
[ Host 軟體 / 帶內管理代理 ]
           │
           │  (PCIe / NVMe Admin Queue: NVMe-MI Send / Receive)
           ▼
┌──────────────────────────────────────────────┐
│ NVMe Controller                              │
│   ├── Admin Queue & NVMe Processing Engine   │
│   └── Controller Management Interface (CMI)  │
└──────────────────────┬───────────────────────┘
                       │
                       │  內部通訊通道 (規格定義為 Vendor Specific)
                       ▼
┌──────────────────────────────────────────────┐
│ Enclosure Services Process (ESP)             │
│   └── 管理風扇、電源、LED、感測器、Slot 等硬體元件  │
└──────────────────────────────────────────────┘
```

1. **規格標準化部分**：
    - NVMe-MI 規範定義了每個 Controller 都必須具備 **Controller Management Interface（CMI）**，用以處理管理命令。
    - 規範定義了 SES-3 診斷頁面與 NVMe-MI 封包資料的一對一映射關係（Byte 0 對齊 Byte 0）。
2. **規格未規範部分（廠商內部設計）**：
    - 規範明確指出：_「NVMe Enclosure 連接埠、NVM Subsystem、NVMe Controller 與 ESP 之間的內部對應關係屬於廠商自訂（Vendor Specific）且不在本規格範圍內。」_
    - **實務上的常見內部通訊實作方式**：
        - **共享記憶體 / 內部 IPC**：若 NVMe Controller SoC 本身就內嵌了 ESP 運行的微處理器（MCU），Controller 與 ESP 通常透過晶片內部的共用 RAM（Shared Memory）或暫存器旗標進行 Inter-Process Communication。
        - **專屬內部硬體匯流排**：若 ESP 是獨立的基板管理晶片或 CPLD/FPGA，NVMe Controller 晶片會透過內部的 I2C/SMBus、SPI 或專屬 UART/GPIO 訊號線與 ESP 進行通信。
        - **子機櫃通訊（Subenclosure）**：若機櫃包含多個 Subenclosure，Primary Subenclosure 的 ESP 亦可透過 Vendor Specific Interface 向 Secondary Subenclosure 收集資料並合併為單一 SES 頁面。

---

### 總結

Host 軟體透過 NVMe Controller 的 Admin Queue 提交 **`NVMe-MI Send` 與 `NVMe-MI Receive`**，以帶內隧道化方式傳送 **`SES Send` 與 `SES Receive`**；NVMe Controller 收到後，由內部的 **Controller Management Interface (CMI)** 解析，並透過**廠商自訂的內部通道（如內部 IPC 或硬體匯流排）**交付給 **ESP** 執行具體的機櫃管理動作。

==========================================================================

**不是的，NVMe-MI SES 完全支援 Out-of-Band，而且在規格中對「NVMe Enclosure（機櫃）」是強制支援（Mandatory）的！**

之所以會產生這個疑問，通常是因為混淆了 **「Out-of-Band 原生發送」** 與 **「In-Band 隧道化（Tunneling）」** 的溝通路徑。

---

### 一、 兩者的溝通路徑差異

#### 1. Out-of-Band（帶外：BMC 發送）

- **通道**：BMC 透過 MCTP（實體層為 SMBus/I2C 或 PCIe VDM）直連 **Management Endpoint (ME)**。
- **傳輸方式**：`SES Send`（Opcode `09h`）與 `SES Receive`（Opcode `08h`）本身就是 **Management Interface Command Set**（NVMe-MI Message Type = `01h`）的原生命令。
- **封裝方式**：BMC **直接發送** NVMe-MI Command Request Message 給 Management Endpoint，**完全不需要透過 NVMe Controller，也不需要封裝成 NVMe Admin 指令**。
- _(注：在此模式下，若資料大於單一訊息上限，規格強制規定必須透過 **MEB** 來輔助傳輸)。_

#### 2. In-Band（帶內：主機 OS / Host 軟體發送）

- **通道**：Host 軟體透過 PCIe 匯流排直連 **NVMe Controller 的 Admin Queue**。
- **傳輸方式**：Host 軟體無法直接接觸 Management Endpoint，因此必須透過 NVMe Base Spec 定義的 **`NVMe-MI Send`（Admin Opcode `1Dh`）** 與 **`NVMe-MI Receive`（Admin Opcode `1Eh`）** 指令。
- **封裝方式**：將原本的 `SES Send` / `SES Receive`「**隧道化（Tunneling）封裝**」在 Admin SQE / CQE 內部進行傳遞。

---

### 二、 規格書支援矩陣對照（Figure 60 vs Figure 61）

在 NVMe-MI 規範中，指令支援依「裝置型態」與「傳輸機制」明確區分：

|裝置類型|指令|Out-of-Band (BMC 直接發送)|In-Band Tunneling (Host 透過 1Dh/1Eh)|
|:--|:--|:--|:--|
|**NVMe Enclosure***(機櫃環境)*|**SES Receive** (08h)**SES Send** (09h)|**Mandatory（強制支援）**直接走 MCTP 封包傳送。|**Mandatory（強制支援）**透過 `NVMe-MI Send/Receive` 隧道化傳送。|
|**NVMe Storage Device***(一般純 SSD)*|**SES Receive** (08h)**SES Send** (09h)|**Prohibited（禁止支援）**純 SSD 無機櫃元件可供管理。|**Prohibited（禁止支援）**純 SSD 不處理機櫃 SES 指令。|

> **特別說明**：在 Out-of-Band 模式下，`NVMe-MI Send (1Dh)` 與 `NVMe-MI Receive (1Eh)` 這兩個 Admin 指令反而被列為 **Prohibited（禁止）**。因為在帶外環境下，BMC 本身就能直接下發原生的 NVMe-MI Command，不需要多此一舉透過 Admin 指令來包裝自己。

---

### 總結

- **NVMe-MI SES 深度支援 Out-of-Band**。
- BMC 在帶外發送 SES 時，是直接發送 **Message Type = 01h (NVMe-MI Command)** 的 `SES Send / SES Receive` 封包給 Management Endpoint，**不經過** NVMe Controller 的 Admin Queue。
- 前一題提到的「NVMe Controller 透過 CMI/內部通道交給 ESP」，那是特指 **In-Band 主機端透過 1Dh/1Eh 隧道化下發** 時的硬體內部處理路徑。