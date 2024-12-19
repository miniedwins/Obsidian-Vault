## 概要說明

在 PCI Express（PCIe）設備中，**Class Code** 是一個三位元的數字碼，描述設備的類型與用途，並協助操作系統進行硬體分類與驅動程式的載入。
## **Class Code 結構**

Class Code 包括三個主要部分，通常用 24 位元表示（Hex 格式）：

- **Base Class (高位 8 位元)**：表示設備的主要分類（例如，網路控制器、顯示卡）。
- **Sub-Class (中間 8 位元)**：更詳細地描述設備類型。
- **Programming Interface (低位 8 位元)**：定義設備支援的程式介面或特定的功能模式。
## **NVMe 範例**

假設一個 PCIe 設備的 Class Code 是 `0x010802`：

- **Base Class** = `01h` → Mass storage controller
- **Sub-Class** = `08h` → Non-Volatile memory controller
- **Programming Interface** = `02h` → NVM Express
## Reference 

- The PCI ID Repository : 	- https://admin.pci-ids.ucw.cz/read/PD
