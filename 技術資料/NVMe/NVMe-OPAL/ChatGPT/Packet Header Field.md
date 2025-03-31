### **1. Packet Header Fields（包頭字段）**

#### **(1) Session（會話）**

- **定義**：
    
    - 該字段標識與該包關聯的會話號。
        
    - 會話號由兩個 **uinteger_4** 值組成：**TPer 會話號（TPerSN）** 和 **Host 會話號（HostSN）**。
        
    - **TPer 會話號** 在前，**Host 會話號** 在後。
        
- **用途**：
    
    - 用於確保通信雙方使用相同的會話號。
        

#### **(2) SeqNumber（序列號）**

- **定義**：
    
    - 這是一個遞增的計數器，從 1 開始，直到 232−1232−1。
        
    - 用於標識會話中的包號，並定義包的傳輸順序。
        
- **行為**：
    
    - 如果支持包編號，消息接收方應忽略序列號等於或小於任何已處理包的包。
        
    - 如果序列號回繞（超過 232−1232−1），會話應自動中止。
        
    - 每個通信方應維護多個序列號計數，包括最後確認的包、下一個預期的包和最後傳輸的包。
        

#### **(3) Reserved（保留）**

- **定義**：
    
    - 該字段的值是保留的。
        
    - 應設置為零，並且 **Host** 和 **TPer** 都應忽略該字段。
        

#### **(4) AckType（確認類型）**

- **定義**：
    
    - 該字段標識 **Acknowledgement（確認）** 字段的用途。
        
    - 可能的值：
        
        - `0x0001`：**Acknowledgement** 字段包含包確認（ACK）。
            
        - `0x0002`：**Acknowledgement** 字段包含包否定確認（NAK）。
            
        - `0x0000`：沒有包被確認或否定確認，**Acknowledgement** 字段應為零。
            

#### **(5) Acknowledgement（確認）**

- **定義**：
    
    - 該字段的含義由 **AckType** 字段的值決定。
        
    - 可能的情況：
        
        - 如果 **AckType** 為 `0x0001`，則該字段為接收方成功接收的最後一個包的序列號。
            
        - 如果 **AckType** 為 `0x0002`，則該字段為接收方希望發送方開始重傳的包的序列號（通常是最後一個已知良好包的序列號加一）。
            
        - 如果 **AckType** 為 `0x0000`，則該字段應為零。
            

#### **(6) Length（長度）**

- **定義**：
    
    - 該字段標識 **Payload（有效載荷）** 字段中的字節數。
        

---

### **2. Packet Payload Fields（包有效載荷字段）**

#### **(1) Data（數據）**

- **定義**：
    
    - 該字段包含一個或多個 **Subpackets（子包）** 的序列。
        

---

### **3. 示例**

假設 **TPer** 向 **Host** 發送一個包，以下是典型的包結構：

#### **(1) Packet Header**

- **Session**：`TPerSN=0x1234` + `HostSN=0x5678`
    
- **SeqNumber**：`0x0000_0001`
    
- **Reserved**：`0x0000_0000`
    
- **AckType**：`0x0001`（ACK）
    
- **Acknowledgement**：`0x0000_0000`（最後確認的包序列號）
    
- **Length**：`0x0000_0020`（有效載荷長度為 32 字節）
    

#### **(2) Packet Payload**

- **Data**：
    
    - `Subpacket 1`：方法調用 `Get`
        
    - `Subpacket 2`：方法調用 `Set`
        

---

### **4. 總結**

- **Packet Header Fields** 包含會話號、序列號、確認類型和有效載荷長度等信息。
    
- **Packet Payload Fields** 包含一個或多個 **Subpackets** 的序列。
    
- 這些字段用於確保包的順序、確認和數據傳輸的正確性。
    

如果有更多問題或需要進一步解釋，請隨時告訴我！

假設 Host向 Tper 發送一個包，典型的包結構 ?

當 **Host** 向 **TPer** 發送一個包時，典型的包結構如下：

---

### **1. Packet Header（包頭）**

#### **(1) Session（會話）**

- **定義**：
    
    - 該字段標識與該包關聯的會話號。
        
    - 會話號由兩個 **uinteger_4** 值組成：**TPer 會話號（TPerSN）** 和 **Host 會話號（HostSN）**。
        
    - **TPer 會話號** 在前，**Host 會話號** 在後。
        
- **示例**：
    
    - `TPerSN=0x1234` + `HostSN=0x5678`
        
    - 會話號：`0x12345678`
        

#### **(2) SeqNumber（序列號）**

- **定義**：
    
    - 這是一個遞增的計數器，從 1 開始，直到 232−1232−1。
        
    - 用於標識會話中的包號，並定義包的傳輸順序。
        
- **示例**：
    
    - 序列號：`0x0000_0001`
        

#### **(3) Reserved（保留）**

- **定義**：
    
    - 該字段的值是保留的。
        
    - 應設置為零，並且 **TPer** 會忽略該字段。
        
- **示例**：
    
    - 保留字段：`0x0000_0000`
        

#### **(4) AckType（確認類型）**

- **定義**：
    
    - 該字段標識 **Acknowledgement（確認）** 字段的用途。
        
    - 可能的值：
        
        - `0x0001`：**Acknowledgement** 字段包含包確認（ACK）。
            
        - `0x0002`：**Acknowledgement** 字段包含包否定確認（NAK）。
            
        - `0x0000`：沒有包被確認或否定確認，**Acknowledgement** 字段應為零。
            
- **示例**：
    
    - 確認類型：`0x0000`（沒有包被確認）
        

#### **(5) Acknowledgement（確認）**

- **定義**：
    
    - 該字段的含義由 **AckType** 字段的值決定。
        
    - 如果 **AckType** 為 `0x0000`，則該字段應為零。
        
- **示例**：
    
    - 確認字段：`0x0000_0000`
        

#### **(6) Length（長度）**

- **定義**：
    
    - 該字段標識 **Payload（有效載荷）** 字段中的字節數。
        
- **示例**：
    
    - 有效載荷長度：`0x0000_0020`（32 字節）
        

---

### **2. Packet Payload（包有效載荷）**

#### **(1) Data（數據）**

- **定義**：
    
    - 該字段包含一個或多個 **Subpackets（子包）** 的序列。
        
- **示例**：
    
    - **Subpacket 1**：方法調用 `Get`
        
        - `Call token` + `MethodID token` + `StartList token` + `EndList token`
            
    - **Subpacket 2**：方法調用 `Set`
        
        - `Call token` + `MethodID token` + `StartList token` + `EndList token`
            

---

### **3. 完整的包結構示例**

以下是 **Host** 向 **TPer** 發送的一個典型包的完整結構：

#### **(1) Packet Header**

- **Session**：`0x12345678`
    
- **SeqNumber**：`0x0000_0001`
    
- **Reserved**：`0x0000_0000`
    
- **AckType**：`0x0000`
    
- **Acknowledgement**：`0x0000_0000`
    
- **Length**：`0x0000_0020`（32 字節）
    

#### **(2) Packet Payload**

- **Data**：
    
    - **Subpacket 1**：
        
        - `Call token` + `MethodID token` + `StartList token` + `EndList token`
            
    - **Subpacket 2**：
        
        - `Call token` + `MethodID token` + `StartList token` + `EndList token`
            

---

### **4. 總結**

- **Host** 向 **TPer** 發送的包結構包括 **Packet Header** 和 **Packet Payload**。
    
- **Packet Header** 包含會話號、序列號、確認類型和有效載荷長度等信息。
    
- **Packet Payload** 包含一個或多個 **Subpackets** 的序列，用於傳遞具體的命令或數據。