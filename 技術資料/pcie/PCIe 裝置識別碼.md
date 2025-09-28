## 1. **Vendor ID (廠商代號)**

- 由 **PCI-SIG 分配的 16-bit 代號**。
    
- 每一家製造 PCI/PCIe 裝置的公司都有唯一的 Vendor ID。
    
- 例如：
    
    - Intel → `0x8086`
        
    - NVIDIA → `0x10DE`
        
    - AMD → `0x1002`
        

👉 用來識別這個硬體是誰生產的。

---

## 2. **Device ID (裝置代號)**

- 同樣是 **16-bit**，但由 **該 Vendor 自己分配**。
    
- 一個 Vendor 底下可能有很多產品（顯示卡、網卡、SSD 控制器…）。
    
- 例如 NVIDIA (`0x10DE`)：
    
    - `0x1B80` → GTX 1080
        
    - `0x1C82` → GTX 1050
        

👉 Vendor ID + Device ID 就能唯一識別一顆 PCIe 裝置的型號。

---

## 3. **Subsystem Vendor ID (次系統廠商代號)**

- 也是 **16-bit**，由 PCI-SIG 分配。
    
- 代表這塊卡片是由哪家公司製造或整合的（通常是 OEM / 板卡廠）。
    
- 例如：
    
    - NVIDIA 提供 GPU 晶片，但最終顯卡可能是 ASUS、MSI、Gigabyte 出貨。
        
    - Subsystem Vendor ID 就會對應 ASUS (`0x1043`)、MSI (`0x1462`) 等等。
        

👉 區分「晶片廠商」和「卡片廠商」。

---

## 4. **Subsystem Device ID (次系統裝置代號)**

- 與 Subsystem Vendor ID 配合使用。
    
- 由 OEM（如 ASUS/MSI）自行定義，對應他們的產品型號。
    
- 例如 ASUS 可能用不同 Subsystem Device ID 區分「ROG Strix 1080」和「TUF 1080」。
    

👉 幫助驅動程式或工具知道這張卡的 OEM 版本與型號。

---

## 5. **Class Code (裝置類別代碼)**

- **24-bit** 欄位，用來描述裝置大類型。
    
- 定義在 PCI-SIG 規範中。
    
- 例如：
    
    - `0x0106` → SATA Controller
        
    - `0x0200` → Ethernet Controller
        
    - `0x0300` → VGA-Compatible Controller (顯示卡)
        

👉 即使 Vendor/Device 不明，也能依 Class Code 指派「泛用驅動」。

---

## 6. **Revision ID (修訂版本號)**

- **8-bit**，由 Vendor 自行定義。
    
- 區分同一晶片的不同版本（Bug Fix、Stepping）。

## 7. **如何組合**

一般我們識別 PCIe 裝置會看：

```shell
`Vendor ID + Device ID + Subsystem Vendor ID + Subsystem Device ID + Revision ID`
```

Linux 下可用 `lspci -nn` 查看，例如：

```shell
`01:00.0 VGA compatible controller [0300]:  NVIDIA Corporation GP104 [GeForce GTX 1080] [10de:1b80]  Subsystem: ASUSTeK Computer Inc. Device [1043:8597]`

```

- `10de:1b80` → NVIDIA GTX 1080
- `1043:8597` → ASUS 子廠商定義

---

✅ 簡單比喻：

- **Vendor ID** = 晶片原廠（Intel / NVIDIA / AMD）
    
- **Device ID** = 晶片型號（GTX 1080）
    
- **Subsystem Vendor ID** = OEM 廠商（ASUS / MSI）
    
- **Subsystem Device ID** = OEM 型號（ROG Strix GTX 1080）