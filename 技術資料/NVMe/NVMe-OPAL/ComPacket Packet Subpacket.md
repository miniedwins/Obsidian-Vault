### **1. ComPacket**

- **定義**：
    
    - **ComPacket** 是通信的主要單位，作為接口命令的有效載荷（Payload）傳輸。
        
    - 每個接口命令的有效載荷只能包含一個 **ComPacket**。
        
    - **ComPacket** 不能跨越多個接口命令。
        
- **內容**：
    
    - **ComPacket** 可以包含零個或多個 **Packets**。
        

---

### **2. Packet**

- **定義**：
    
    - **Packet** 與特定的會話（Session）相關聯。
        
    - 每個 **Packet** 可以包含零個或多個 **Subpackets**。
        
- **內容**：
    
    - **Packet** 包含會話 ID 和其他與會話相關的信息。
        

---

### **3. Subpacket**

- **定義**：
    
    - **Subpacket** 是 **Packet** 的組成部分。
        
    - 每個 **Subpacket** 可以包含零個或多個 **Tokens**。
        
- **內容**：
    
    - **Subpacket** 包含實際的數據或命令，例如方法調用（Method Calls）或方法結果（Method Results）。
        

---

### **4. Tokens**

- **定義**：
    
    - **Tokens** 是 **Subpacket** 的組成部分，用於表示數據或命令的具體內容。
        
    - **Tokens** 可以跨越多個 **Subpackets** 和多個 **Packets**。
        
- **內容**：
    
    - **Tokens** 可以是整數、字節序列、列表、命名值等。
        

---

### **5. 結構關係**

以下是 **ComPacket**、**Packet**、**Subpacket** 和 **Tokens** 之間的結構關係：

#### **(1) ComPacket**

- 包含零個或多個 **Packets**。
    
- 不能跨越多個接口命令。
    

#### **(2) Packet**

- 包含零個或多個 **Subpackets**。
    
- 與特定的會話相關聯。
    

#### **(3) Subpacket**

- 包含零個或多個 **Tokens**。
    
- 不能跨越多個 **Packets**。
    

#### **(4) Tokens**

- 可以跨越多個 **Subpackets** 和多個 **Packets**。
    

---

### **6. 示例**

假設您需要傳遞一個包含多個方法調用的 **ComPacket**，以下是典型的結構：

#### **(1) ComPacket**

- 包含兩個 **Packets**：
    
    - **Packet 1**：會話 ID = 1
        
    - **Packet 2**：會話 ID = 2
        

#### **(2) Packet 1**

- 包含兩個 **Subpackets**：
    
    - **Subpacket 1**：方法調用 `Get`
        
    - **Subpacket 2**：方法調用 `Set`
        

#### **(3) Subpacket 1**

- 包含多個 **Tokens**：
    
    - `Call token` + `MethodID token` + `StartList token` + `EndList token`
        

#### **(4) Subpacket 2**

- 包含多個 **Tokens**：
    
    - `Call token` + `MethodID token` + `StartList token` + `EndList token`
        

---

### **7. 總結**

- **ComPacket** 是通信的主要單位，包含零個或多個 **Packets**。
    
- **Packet** 與特定的會話相關聯，包含零個或多個 **Subpackets**。
    
- **Subpacket** 包含零個或多個 **Tokens**，並且不能跨越多個 **Packets**。
    
- **Tokens** 可以跨越多個 **Subpackets** 和多個 **Packets**。