規範原文：

> The Global Range is either Read Unlocked or Write Unlocked at the time of invocation of RevertSP

意思是：

- 在呼叫 `RevertSP` 時，**Global Range 只要不是完全被鎖住**就行。
    
- 也就是：
    
    - **Read Unlocked = true**（可讀，不論能不能寫）
        
    - 或 **Write Unlocked = true**（可寫，不論能不能讀）
        
    - 兩者只要有一個成立，就符合條件。

### 為什麼只要求其中一個？

因為 `RevertSP` 本身不是一個「I/O 存取命令」，它主要重置 SP 設定。  
只要能保證 **主機至少有一個存取通道（讀或寫）是打開的**，就能進行 Reset 動作並且後續操作磁碟。

如果兩個都鎖（read-locked & write-locked），即使保留了 `GlobalRangeKey`，你還是完全無法存取資料，測試就會 **FAIL**。