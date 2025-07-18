
## NVM Subsystem Reset

## Controller Level Reset

## Management Endpoint Reset

## 🔹**觸發條件**

- 根據 MCTP Base 規範或各個 transport binding（如 SMBus/I2C、PCIe）規定情境。
    
- 如果 Management Endpoint 與 PCIe port 綁定，**當 PCIe port 發生 conventional reset（例如 PERST#）時，會一併觸發 Management Endpoint Reset**。
    

## 🔹**行為與影響**

1. **狀態恢復：**
    
    - 被 reset 的 Management Endpoint 必須回復至「預設狀態」。
        
2. **命令中止：**
    
    - 該 Endpoint 上所有正在進行中的命令都會被強制中止。
        
3. **影響範圍：**
    
    - Reset 僅限影響被觸發的那個 Management Endpoint：
        
        - 不應影響同一 NVM Subsystem 中其他的 Management Endpoints。
            
        - 也不應影響其他 NVM Subsystem 元件。
            
4. **版本差異備註：**
    
    - 在 MCTP v1.1 或更早版本中，若 PCIe Management Endpoint 被 reset：
        
        - 其他 SMBus/I2C 或 PCIe Endpoint 上的 MCTP 訪問可能會暫時不被支援（即可能會一起受到影響）。

## SMBus Reset

### 🔹 1. **基本定義與觸發條件**

- **依 SMBus 規範建議**：  
    所有 SMBus/I²C 元件應支援當 **時鐘（SCL）為低電位** 且超過 `tTIMEOUT,MIN`（由 SMBus Spec 定義）時自動觸發 SMBus Reset。
    
- **某些 Form Factor（例如 M.2）**：  
    可能還會有額外定義的 **外部 SMBus Reset 機制（例如硬體線路）**，若支援此機制，則：
    
    - 所有 **NVM Subsystem 上的 SMBus/I²C 元件都必須同步被 Reset**。
        
    - 並需根據所使用的 form factor，**轉換成對應的 Reset 行為（例如通知 Expansion Connector）**。
        

---

### 🔹 2. **Reset 發生時的 I²C 傳輸行為**

- 如果一個 SMBus/I²C 元件正在傳送 **Response Message**（也就是一個資料封包），
    
    - **該裝置應立即產生一個 STOP 條件**（依 SMBus Spec 定義）。
        
    - STOP 可以發生在「目前正在傳送的資料位元組之後」或「之中」。
        
- Reset 發生後：
    
    - 該 NVM Subsystem 在 SMBus 上應該保持 **靜默（Idle）**，即使有其他主控器發出地址呼叫也不應回應。
        
    - 在 SMBus Reset **解除（de-assertion）後 10ms 內**，該 Subsystem 應該準備好接收新的 START 條件。
        

---

### 🔹 3. **Reset 對 ARP 位址的影響**

- **SMBus Reset 不會重設 ARP 指派位址（即動態位址）**。
    
- 如果需要重新指派位址：
    
    - 管理控制器（Management Controller）應該主動發送 **ARP Reset**。
        

---

### 🔹 4. **Command Slot 的行為**

- 每一個 **SMBus/I²C Management Endpoint 中的 Command Slot** 應該視 SMBus Reset 為一種：
    
    > **隱式的 Abort Control Primitive**（參考 §4.2.1.3）
    
    也就是：
    
    - 中止所有目前執行的命令。
        
    - 不需要傳送任何 **Abort Control Primitive 的 Response Message**（因為這是隱式的，不需要明確回應）。