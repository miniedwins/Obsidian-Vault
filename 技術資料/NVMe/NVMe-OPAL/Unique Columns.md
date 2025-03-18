### **1. 唯一列的定義**

- **唯一列**：
    
    - 如果表的某一列或一組列被定義為唯一，則表中每一行在這些列中的值或值組合必須是唯一的。
        
    - 這意味著表中不能有兩行在這些列中具有相同的值或值組合。
        
- **多列唯一值**：
    
    - 如果多列被標記為參與唯一性要求，則這些列的組合值必須是唯一的。
        
    - 這稱為 **多列唯一值（Multi-Column Unique Value）**。
        

---

### **2. 唯一列的行為**

以下是唯一列的具體行為：

#### **(1) 單列唯一值**

- **定義**：
    
    - 如果表的某一列被定義為唯一，則該列中的每個值必須是唯一的。
        
- **示例**：
    
    - 表 `UserTable` 的 `UserID` 列被定義為唯一。
        
    - 數據示例：
        
        - 行 1：`{UserID=1, UserName="Alice"}`
            
        - 行 2：`{UserID=2, UserName="Bob"}`
            
    - 如果嘗試插入 `{UserID=1, UserName="Charlie"}`，則會失敗，因為 `UserID=1` 已經存在。
        

#### **(2) 多列唯一值**

- **定義**：
    
    - 如果表的多列被定義為唯一，則這些列的組合值必須是唯一的。
        
- **示例**：
    
    - 表 `OrderTable` 的 `OrderID` 和 `ProductID` 列被定義為唯一。
        
    - 數據示例：
        
        - 行 1：`{OrderID=1, ProductID=101, Quantity=2}`
            
        - 行 2：`{OrderID=1, ProductID=102, Quantity=1}`
            
    - 如果嘗試插入 `{OrderID=1, ProductID=101, Quantity=3}`，則會失敗，因為 `OrderID=1` 和 `ProductID=101` 的組合已經存在。
        

---

### **3. 唯一列的實現**

- **創建表時定義唯一列**：
    
    - 在創建表時，可以指定某一列或一組列為唯一列。
        
- **插入數據時的檢查**：
    
    - 當插入新行時，**TPer** 會檢查唯一列的值是否已經存在。
        
    - 如果違反唯一性要求，則插入操作會失敗。
        

---

### **4. 示例場景**

以下是幾個典型場景的示例：

#### **(1) 單列唯一值**

- 表名：`UserTable`
    
- 列：
    
    - `UserID`：`uinteger`（唯一）
        
    - `UserName`：`byte string`
        
- 數據示例：
    
    - 行 1：`{UserID=1, UserName="Alice"}`
        
    - 行 2：`{UserID=2, UserName="Bob"}`
        
- 插入失敗示例：
    
    - 嘗試插入 `{UserID=1, UserName="Charlie"}`，因為 `UserID=1` 已經存在。
        

#### **(2) 多列唯一值**

- 表名：`OrderTable`
    
- 列：
    
    - `OrderID`：`uinteger`
        
    - `ProductID`：`uinteger`
        
    - `Quantity`：`uinteger`
        
- 唯一列：`OrderID` 和 `ProductID`
    
- 數據示例：
    
    - 行 1：`{OrderID=1, ProductID=101, Quantity=2}`
        
    - 行 2：`{OrderID=1, ProductID=102, Quantity=1}`
        
- 插入失敗示例：
    
    - 嘗試插入 `{OrderID=1, ProductID=101, Quantity=3}`，因為 `OrderID=1` 和 `ProductID=101` 的組合已經存在。
        

---

### **5. 總結**

- **唯一列** 確保表中某一列或一組列的值或值組合是唯一的。
    
- **單列唯一值** 要求某一列中的每個值必須是唯一的。
    
- **多列唯一值** 要求多列的組合值必須是唯一的。
    
- 在插入數據時，**TPer** 會檢查唯一列的值是否已經存在，如果違反唯一性要求，則插入操作會失敗。