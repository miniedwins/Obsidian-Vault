## RevertSP

### 🧩 原文分析：

#### 🔸 第一段：

> If a namespace is associated with a Namespace Global Range Locking object when the RevertSP method is invoked,  
> then the media encryption key of that namespace is eradicated, regardless of whether the KeepGlobalRangeKey parameter is set to TRUE or FALSE.

📖 意思是：

- 若 Namespace 在執行 `RevertSP()` 時，仍「連結著」它自己的 **Namespace Global Range Locking object**，
    
- 那麼這個 Namespace 的媒體加密金鑰 **一定會被清除（eradicated）**。
    
- 即使你設定 `KeepGlobalRangeKey=TRUE`，也沒用。
    

💡 換句話說：

> `RevertSP` 不會保留 Namespace Global Range 的 key，只有在 namespace 已經「解除關聯（deassign）」的情況下，才有機會保留。

---

#### 🔸 第二段：

> If the invoker of the RevertSP method wishes to keep the keys associated with Namespace Global Range Locking objects,  
> the Deassign method should be invoked on those Namespace Global Range Locking objects prior to invoking the RevertSP method.

📖 意思是：

- 若你想要「保留 Namespace Global Range 的加密金鑰」，
    
- 你**必須先呼叫 `Deassign()`**，把 Namespace 從它的 Namespace Global Range Locking object 解除關聯，
    
- 然後再執行 `RevertSP()`。
    

---

#### 🔸 第三段：

> If the Deassign method is successfully invoked on a Namespace Global Range Locking object before the RevertSP method is invoked,  
> then the media encryption key of that namespace/LUN would be associated with the Global Range Locking object at time of RevertSP method invocation.

📖 意思是：

- 當你成功 `Deassign()` 後，
    
    - 該 Namespace 原本的 media key（屬於 Namespace Global Range Locking object）
        
    - 會被「交還」給 **Global Range Locking object** 管理。
        
- 這樣在 `RevertSP()` 執行時，該 Namespace 的 key 不會被清除，  
    因為它現在屬於 Global Range Locking object。
    

---

### 🔐 整體邏輯圖（簡化理解）

|狀態|動作|結果|
|---|---|---|
|Namespace still linked to Namespace Global Range LO|`RevertSP()`|🔥 該 Namespace 的 media key 被清除（eradicated）|
|Namespace **Deassigned** 回 Global Range LO|`RevertSP()`|✅ key 保留（因為屬於 Global Range LO）|

### 🔹 第一段

> Upon successful invocation of the RevertSP method, the method SHALL increment the Unused Key Count by the number of Namespace Non-Global Range Locking objects when the method was invoked.

意思是：

- 當你執行 `RevertSP()` 成功後，
    
- **TPer 會把 “Namespace Non-Global Range Locking objects” 的數量加回 Unused Key Count。**
    

💡 為什麼？

- 因為 `RevertSP` 會「解除所有 Namespace Non-Global Range Locking objects」。
    
- 這些 Locking objects 原本各自佔用一把 key（在 Assign 時 Unused Key Count 減 1）。
    
- 當你 revert（重置）時，它們都被清除、釋放出來，  
    所以要把那幾把 key **加回 pool** → 也就是「Unused Key Count +N」。
    

🧠 換句話說：

> RevertSP = 釋放所有 Non-Global Range 的金鑰佔用。

---

### 🔹 第二段

> If the RevertSP method is invoked with the KeepGlobalRangeKey parameter set to TRUE, then the TPer SHALL:  
> a) continue to use the media encryption key for each namespace/LUN that was associated with the Global Range Locking object; and  
> b) eradicate the media encryption key associated with the K_AES_* object indicated by the ActiveKey column value of each Non-Global Locking object.

意思是：

- 若 `KeepGlobalRangeKey=TRUE`：
    
    - (a) Global Range Locking object 的 key 保留，不清除；
        
    - (b) 但所有 Non-Global（包含 Namespace Global Range 和 Namespace Non-Global Range）的 key 都要被清除。
        

🧠 所以：

> Unused Key Count 加回來的是「被清掉的 Non-Global Range keys」。

---

### 🔹 第三段

> The Unused Key Count SHALL NOT be otherwise affected by the RevertSP method invocation, i.e. the Unused Key Count should not be returned to its OFS values.

意思是：

- 除了上述的「加回 Non-Global Range key 數量」之外，
    
    - `RevertSP` 不應該重設 Unused Key Count 為出廠（OFS, Original Factory Setting）值。
        
- 換句話說：
    
    - 不會「歸零」或「回復初始出廠值」，
        
    - 只會針對被釋放的 Non-Global Range key 做 **增量回補**。