### 1. **事務的提交與持久化**

事務中的更改在以下兩種情況下會被成功提交並持久化：

#### a. **方法在事務外調用**

- 如果一個方法在事務外調用並成功執行，則該方法所做的更改會 **立即提交並持久化**。
    
- 例如：
    
    - 主機調用一個方法修改表格值，該方法不在事務中。
        
    - 方法成功執行後，更改會立即生效並持久化。
        

#### b. **方法在事務內調用**

- 如果一個方法在事務內或嵌套事務內調用，則該方法所做的更改會在 **頂層事務提交時提交並持久化**。
    
- 例如：
    
    - 主機啟動一個事務，並在事務內調用多個方法修改表格值。
        
    - 當頂層事務提交時，所有更改會一次性提交並持久化。
        

---

### 2. **事務內的更改可見性**

- 在事務內，所做的更改對該事務是可見的。
    
- 例如：
    
    - 在事務內修改表格值後，調用 **Get** 方法會返回修改後的值。
        
- 這些更改只有在頂層事務提交時才會持久化。
    
- 如果事務中止，則這些更改會被 **回滾（Rollback）**。
    

---

### 3. **影響 TPer 狀態的更改**

- 如果更改影響 TPer 的其他方面（例如硬體設置），則這些更改會在相關更改成功提交時生效。
    
- 例如：
    
    - 在事務內修改媒體加密密鑰或讀寫鎖狀態，這些更改只有在事務提交時才會生效。
        
- 這意味著事務內的更改不會立即影響 TPer 的狀態，直到事務成功提交。
    

---

### 4. **事務中止的原因**

事務中止只會發生在以下兩種情況下：

#### a. **主機請求中止**

- 主機發送 **End Transaction** 令牌，並指定狀態不為 **0x00**。
    
- 例如：
    
    - 主機發送 **End Transaction** 令牌，狀態為 **0x01**，表示請求中止事務。
        

#### b. **提交時發生錯誤**

- 主機發送 **End Transaction** 令牌，狀態為 **0x00**，但 TPer 在提交事務時遇到錯誤。
    
- 例如：
    
    - TPer 在將事務提交到媒體時發生錯誤，導致事務中止。
        

---

### 5. **事務的例外情況**

- 某些更改可能不受事務回滾的影響（例如日誌記錄），並且會 **立即提交**，即使它們發生在事務內或作為方法調用的副作用。
    
- 例如：
    
    - 在事務內記錄日誌，即使事務中止，日誌記錄也會立即提交。
        

---

### 6. **總結**

- 事務中的更改在事務外調用方法時會立即提交，或在事務提交時一次性提交。
    
- 事務內的更改對該事務是可見的，但在事務提交前不會持久化。
    
- 如果事務中止，則所有更改會被回滾。
    
- 事務中止的原因包括主機請求中止和提交時發生錯誤。
    
- 某些更改（例如日誌記錄）不受事務回滾的影響，會立即提交。

============================================================
### **「Inside」與「Outside」的差別**

這段文字主要描述 **變更（Changes）何時被成功提交（Committed）並持久化（Persistent）** 的兩種情況：

1. **Outside of a transaction（在交易外執行）**
2. **Inside of a transaction（在交易內執行）**

---

## **1. Outside of a transaction（交易外）**

當某個方法（Method）**在交易之外** 被執行時：

- **該方法執行成功後，變更會立即提交並持久化（Commit and Persistent）。**
- **不需要額外的 Commit 指令**，TPer 會在該方法執行完畢後，直接將變更應用到系統中。

### **舉例：設定使用者密碼**

假設主機執行如下指令：

plaintext

複製編輯

`SetPassword(User1, "NewPassword")`

如果這個 `SetPassword` 方法是在交易（Transaction）之外執行的：

- **變更會立即生效**（新密碼馬上變成有效）。
- **這次變更不需要再執行 Commit**，因為 TPer 會自動處理。

✅ **優點**：變更即時生效，適用於單一、不影響整體系統的設定變更。  
❌ **缺點**：如果發生錯誤，無法回滾（Rollback）。

---

## **2. Inside of a transaction（交易內）**

當某個方法是在 **交易（Transaction）內** 執行時：

- **變更不會立即生效**，而是**暫存**起來。
- 只有當**最上層的交易（Top-level Transaction）執行 Commit 時，所有變更才會正式提交並持久化**。

這種方式允許主機執行**一系列操作**，等到所有變更都確認沒問題後，再**一次性提交**。  
如果中途發生錯誤，可以使用**Rollback** 來取消變更。

### **舉例：批量設定使用者**

假設我們有一組交易：

plaintext

複製編輯

`BeginTransaction()     CreateUser(User1)     SetPassword(User1, "NewPassword")     AssignPermissions(User1, "Read/Write") CommitTransaction()`

如果 `CommitTransaction()` 沒有執行，或者執行失敗：

- `User1` 不會被建立。
- 密碼不會變更。
- 權限設定也不會生效。
- **TPer 不會應用這些變更，確保系統一致性**。

只有當 `CommitTransaction()` 成功後：

- `User1` 才真正被建立。
- `NewPassword` 變更才生效。
- `Read/Write` 權限才會套用。

✅ **優點**：允許批量操作，確保變更一致性，可以用 Rollback 取消未完成變更。  
❌ **缺點**：變更不會即時生效，必須確保 `CommitTransaction()` 成功執行。

---

## **總結**

|**模式**|**變更生效時間**|**是否需要 Commit()**|**是否可以 Rollback()**|**適用場景**|
|---|---|---|---|---|
|**Outside of a transaction**|立即|不需要|❌ 不行|單一變更，影響範圍小|
|**Inside of a transaction**|Commit 時|需要|✅ 可以|批量變更，確保一致性|

**簡單來說：**

- **Outside**：單次變更，成功後立即生效。
- **Inside**：一組變更，等 `Commit` 成功後才生效。

=============================================================

在 **TCG（Trusted Computing Group）** 存儲協議中，判斷一個方法是 **inside**（在事務內）還是 **outside**（在事務外）取決於該方法是否在 **事務上下文（Transaction Context）** 中執行。以下是詳細說明：

---

### 1. **事務的開始與結束**

- **開始事務**：
    
    - 主機通過發送 **Start Transaction** 命令來開始一個事務。
        
    - 從此時起，所有後續的命令都被視為在事務內執行，直到事務結束。
        
- **結束事務**：
    
    - 主機通過發送 **End Transaction** 命令來結束事務。
        
    - 事務結束後，後續的命令被視為在事務外執行。
        

---

### 2. **判斷方法是否在事務內**

- **在事務內（Inside Transaction）**：
    
    - 如果一個方法在 **Start Transaction** 和 **End Transaction** 之間執行，則該方法被視為在事務內。
        
    - 例如：
        
        plaintext
        
        复制
        
        Start Transaction
        Method A
        Method B
        End Transaction
        
        - **Method A** 和 **Method B** 都在事務內執行。
            
- **在事務外（Outside Transaction）**：
    
    - 如果一個方法在 **Start Transaction** 之前或 **End Transaction** 之後執行，則該方法被視為在事務外。
        
    - 例如：
        
        plaintext
        
        复制
        
        Method A
        Start Transaction
        Method B
        End Transaction
        Method C
        
        - **Method A** 和 **Method C** 在事務外執行，**Method B** 在事務內執行。
            

---

### 3. **事務的嵌套**

- **嵌套事務**：
    
    - TCG 存儲協議支持嵌套事務，即一個事務內可以包含另一個事務。
        
    - 在嵌套事務中，所有方法都被視為在事務內執行，直到最外層事務結束。
        
- 例如：
    
    plaintext
    
    复制
    
    Start Transaction (Level 1)
    Method A
    Start Transaction (Level 2)
    Method B
    End Transaction (Level 2)
    Method C
    End Transaction (Level 1)
    
    - **Method A**、**Method B** 和 **Method C** 都在事務內執行。
        

---

### 4. **事務的提交與回滾**

- **提交事務**：
    
    - 當最外層事務提交時，所有在事務內執行的更改會被一次性提交並持久化。
        
- **回滾事務**：
    
    - 如果事務中止，則所有在事務內執行的更改會被回滾。
        

---

### 5. **如何確認方法是否在事務內**

- **追蹤事務狀態**：
    
    - 主機需要追蹤當前的事務狀態（例如是否在事務內、事務的嵌套層次）。
        
- **檢查命令順序**：
    
    - 通過檢查命令的順序，可以判斷一個方法是否在事務內執行。
        
- **使用日誌記錄**：
    
    - 在調試或開發過程中，可以使用日誌記錄來追蹤事務的開始和結束，以及方法的執行順序。
        

---

### 6. **示例**

以下是一個示例，展示如何判斷方法是否在事務內：

#### 示例：

plaintext

复制

Method X (Outside Transaction)
Start Transaction
Method Y (Inside Transaction)
Method Z (Inside Transaction)
End Transaction
Method W (Outside Transaction)

- **Method X** 和 **Method W** 在事務外執行。
    
- **Method Y** 和 **Method Z** 在事務內執行。
    

---

### 7. **總結**

- 判斷一個方法是 **inside** 還是 **outside** 事務，取決於該方法是否在 **Start Transaction** 和 **End Transaction** 之間執行。
    
- 主機需要追蹤事務狀態，並檢查命令的順序來確認方法是否在事務內。
    
- 嵌套事務中的方法也被視為在事務內執行，直到最外層事務結束。