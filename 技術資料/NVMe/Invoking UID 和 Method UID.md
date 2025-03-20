在 **TCG（Trusted Computing Group）** 存儲協議中，**Invoking UID** 和 **Method UID** 的使用順序是為了確保正確的對象和方法調用。以下是詳細說明：

---

### 1. **Invoking UID 和 Method UID 的作用**

- **Invoking UID**：
    
    - **Invoking UID** 用於指定要調用的 **對象（Object）**，例如表格、權限或憑證。
        
- **Method UID**：
    
    - **Method UID** 用於指定要在該對象上調用的 **方法（Method）**，例如讀取、寫入或認證。
        

---

### 2. **調用順序的原因**

- **對象優先**：
    
    - 在調用方法之前，必須先確定要操作的對象。因此，**Invoking UID** 必須在 **Method UID** 之前指定。
        
- **方法依賴對象**：
    
    - 方法的執行依賴於對象的狀態和屬性。例如，讀取表格數據的方法必須知道要讀取哪個表格。
        
- **協議規範**：
    
    - TCG 存儲協議規定，**Invoking UID** 必須在 **Method UID** 之前指定，以確保調用的正確性和一致性。
        

---

### 3. **調用流程**

以下是典型的調用流程：

#### 步驟 1：指定 Invoking UID

- 主機發送 **Invoking UID**，指定要操作的對象。
    
- 例如，指定要操作的表格或權限。
    

#### 步驟 2：指定 Method UID

- 主機發送 **Method UID**，指定要在該對象上調用的方法。
    
- 例如，指定要執行的讀取、寫入或認證操作。
    

#### 步驟 3：執行方法

- TPer 根據 **Invoking UID** 和 **Method UID** 執行相應的方法，並返回結果。
    

---

### 4. **示例**

以下是一個示例，展示如何通過 **Invoking UID** 和 **Method UID** 調用方法：

#### 示例：讀取表格數據

1. **指定 Invoking UID**：
    
    - 主機發送 **Invoking UID**，指定要讀取的表格（例如 **Table_A**）。
        
2. **指定 Method UID**：
    
    - 主機發送 **Method UID**，指定要執行的讀取操作（例如 **ReadTable**）。
        
3. **執行方法**：
    
    - TPer 根據 **Invoking UID** 和 **Method UID** 讀取 **Table_A** 的數據，並返回結果。
        

---

### 5. **總結**

- **Invoking UID** 用於指定要操作的對象，**Method UID** 用於指定要調用的方法。
    
- 調用順序是 **先指定 Invoking UID，再指定 Method UID**，以確保正確的對象和方法調用。
    
- 這種順序符合 TCG 存儲協議的規範，並確保調用的正確性和一致性