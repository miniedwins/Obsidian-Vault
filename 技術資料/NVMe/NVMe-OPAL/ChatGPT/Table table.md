### **1. Table table（表表）的定義**

- **Table table** 是一個特殊的 **Object Table（對象表）**，用於存儲所有表的元數據。
    
- 每個表在 **Table table** 中都有一個對應的行，該行是一個 **表描述符對象（Table Descriptor Object）**，存儲了與該表相關的元數據。
    

---

### **2. 表描述符對象（Table Descriptor Object）**

- **表描述符對象** 是 **Table table** 中的一行，包含以下信息：
    
    - **UID**：表的唯一標識符。
        
    - **TableName**：表的名稱。
        
    - 其他元數據：例如表的列定義、訪問控制信息等。
        

---

### **3. 表的 UID**

- **表的 UID**：
    
    - 每個表都有一個唯一的 **UID**，用於標識該表。
        
    - 這個 **UID** 是從 **Table table** 中該表的 **UID** 派生出來的。
        
- **示例**：
    
    - 假設 **Table table** 中有一行：
        
        - `{UID=0xABCD, TableName="UserTable"}`
            
    - 則表 `UserTable` 的 **UID** 為 `0xABCD`。
        

---

### **4. Table table 的結構**

以下是 **Table table** 的典型結構：

#### **(1) 列定義**

- **UID**：表的唯一標識符。
    
- **TableName**：表的名稱。
    
- 其他元數據列：例如列定義、訪問控制信息等。
    

#### **(2) 數據示例**

- 行 1：`{UID=0xABCD, TableName="UserTable"}`
    
- 行 2：`{UID=0xEF01, TableName="LogTable"}`
    

---

### **5. 使用場景**

以下是 **Table table** 的典型使用場景：

#### **(1) 創建新表**

- 當創建一個新表時，**TPer** 會在 **Table table** 中創建一個新的表描述符對象。
    
- 示例：
    
    - 創建表 `UserTable`，並在 **Table table** 中添加一行：
        
        - `{UID=0xABCD, TableName="UserTable"}`
            

#### **(2) 查詢表信息**

- 主機可以查詢 **Table table** 以獲取所有表的信息。
    
- 示例：
    
    - 查詢 **Table table**，獲取所有表的名稱和 **UID**。
        

#### **(3) 刪除表**

- 當刪除一個表時，**TPer** 會從 **Table table** 中刪除對應的表描述符對象。
    
- 示例：
    
    - 刪除表 `UserTable`，並從 **Table table** 中刪除對應的行。
        

---

### **6. 總結**

- **Table table** 是一個特殊的 **Object Table**，用於存儲所有表的元數據。
    
- 每個表在 **Table table** 中都有一個對應的表描述符對象，包含表的 **UID**、名稱和其他元數據。
    
- 表的 **UID** 是從 **Table table** 中該表的 **UID** 派生出來的，用於唯一標識該表。