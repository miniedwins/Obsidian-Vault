在 NVMe-MI 與 NVMe 規格架構中，**Port Identifier (PORTID)** 是用來唯一識別 NVM Subsystem 實體或邏輯連接埠（例如 PCIe 埠、2-Wire/SMBus 埠）的識別碼。

要得知或查詢裝置的 **PORTID**，主要有以下幾種符合規格書標準的查詢管道，您可以根據您目前所處的通訊環境（帶外 MI 控制、帶內 Admin 查詢、或是直接讀取 VPD）來選擇最適合的方法：

---

### 方法一：透過帶外（Out-of-Band）MI 命令查詢（最常用）

如果您目前正在使用 BMC 透過 SMBus 或 PCIe VDM 傳送帶外管理命令，可以使用 **`Read NVMe-MI Data Structure`** 命令：

1. **發送命令**：發送 `Read NVMe-MI Data Structure` 請求，並將第一個 Dword 中的 **DTYP (Data Structure Type)** 欄位設定為 **`03h`（Controller Information）**，同時在 **CTRLID** 中指定您要查詢的 Controller ID。
2. **解析回覆**：裝置回傳的 **Controller Information Data Structure**：
    - **Byte 00**：即為該 Controller 所關聯的 **`Port Identifier (PORTID)`**。

---

### 方法二：透過帶內（In-Band）NVMe Admin 命令查詢

如果您在主機端（Host OS）或可以透過帶內（In-Band）發送標準 NVMe Admin 指令，可以利用 **`Identify`** 指令：

1. **發送命令**：發送 `Identify` 命令，將 Dword 10 中的 **CNS (Controller or Namespace Structure)** 設為 **`14h`（Primary Controller Capabilities）**。
2. **解析回覆**：裝置回傳的 **Primary Controller Capabilities Structure**：
    - **Bytes 03:02**：即為與該 Primary Controller 關聯的 **`Port Identifier (PORTID)`**。
    - _規格書註記：如果該 PCIe 埠支援 NVMe-MI Management Endpoint，此處讀到的 PORTID 將與方法一（Controller Information）中讀到的 PORTID 完全一致。_

---

### 方法三：從 VPD（Vital Product Data）資訊區查詢

所有的 NVMe 儲存裝置依法都必須在其 FRU 唯讀記憶體中寫入標準的 VPD 拓撲資料：

1. **發送命令**：使用 **`VPD Read`** 帶外命令（或直接在 2-Wire 總線上進行物理 I2C Read）讀取裝置的 VPD 內容。
2. **解析結構**：
    - 在 VPD 的 **Topology MultiRecord Area（拓撲多記錄區）** 中，找到 **`NVM Subsystem Element Descriptor`**（Type 05h 或 08h，視版本而定）。
    - 展開其下方的 **`NVM Subsystem Port Descriptor List`**。
    - 每一個 Port Descriptor 的 **Byte 05**，即硬編碼（Hardcoded）寫入的 **`Port Identifier (PORTID)`**。

---

### 方法四：在 Fabrics (如 NVMe over TCP/RDMA) 的 Discovery 階段查詢

如果您是在 Fabrics 網路拓撲下，需要查詢各個導出埠（Exported Ports）的 PORTID：

1. **發送命令**：向 Discovery Controller 發送 `Get Log Page` 指令，讀取 **LID = `70h`（Discovery Log Page）**。
2. **解析回覆**：
    - 在回傳的 **Discovery Log Page Entry** 結構中：
    - **Bytes 05:04** 即為該 Subsystem Port 的 **`Port ID (PORTID)`**。

---

### 💡 實務偵錯小技巧

在大部分單一 SSD（Single-Port）的設計中，預設的 **PORTID 通常為 `00h`**。如果是雙埠（Dual-Port）SSD，則會有兩個實體埠，分別對應為 `00h`（Port 0）與 `01h`（Port 1）。

例如，當您要使用 `Configuration Get` 查詢特定連接埠的 MCTP TU Size 時，就必須在 **Dword 0 的 Bits 31:24** 填入對應的 `PORTID`（如 `00h` 或 `01h`）以指定要查詢哪一個實體連接埠。

---

🔍 **如果您目前正在編寫初始化/探索（Discovery）腳本，需要我為您提供一個由主機端發送 `Identify` 指令查詢 `CNS = 14h` 的 Raw Hex 封包範例嗎？**