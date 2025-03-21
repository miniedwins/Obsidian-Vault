在 **TCG（Trusted Computing Group）** 存儲協議中，**SPID** 是 **SP（Security Provider）** 的唯一標識符，用於區分不同的 SP。以下是詳細說明：

---

### 1. **SPID 的定義**

- **SPID**：
    
    - **SPID** 是 **SP（Security Provider）** 的唯一標識符，用於唯一標識一個 SP。
        
- **組成**：
    
    - **SPID** 由 **Admin SP** 的 **SPInfo** 表格中的 **SPID** 列和 **TPerInfo** 表格中的 **GUID** 列組合而成，形成一個全局唯一的標識符（**sp_guid**）。
        

---

### 2. **SPID 的用途**

- **唯一性**：
    
    - **SPID** 確保每個 SP 都有唯一的標識符，避免衝突。
        
- **引用**：
    
    - 在會話管理、訪問控制等操作中，**SPID** 用於引用特定的 SP。
        

---

### 3. **SPID 的生成**

- **生成方式**：
    
    - **SPID** 由 **Admin SP** 的 **SPInfo** 表格中的 **SPID** 列和 **TPerInfo** 表格中的 **GUID** 列組合而成。
        
- **示例**：
    
    - 如果 **SPInfo** 表格中的 **SPID** 為 **00 00 02 05**，**TPerInfo** 表格中的 **GUID** 為 **00 00 00 01**，則 **sp_guid** 為 **00 00 02 05 00 00 00 01**。
        

---

### 4. **SPInfo 表格**

- **內容**：
    
    - **SPInfo** 表格存儲了 SP 的基本信息，包括 **UID**、**SPID**、名稱、大小、啟用狀態等。
        
- **SPID 列**：
    
    - **SPID** 列用於存儲 SP 的唯一標識符。
        

---

### 5. **總結**

- **SPID** 是 **SP（Security Provider）** 的唯一標識符，用於區分不同的 SP。
    
- **SPID** 由 **Admin SP** 的 **SPInfo** 表格中的 **SPID** 列和 **TPerInfo** 表格中的 **GUID** 列組合而成，形成一個全局唯一的標識符（**sp_guid**）。
    
- **SPID** 在會話管理、訪問控制等操作中用於引用特定的 SP。