
## 1. 鎖定的 LBA 範圍
- 一個 LBA（邏輯區塊地址）範圍被視為**鎖定**的條件是：
    - 對於**讀取操作**：`ReadLockEnabled = True` 且 `ReadLocked = True`。        
    - 對於**寫入操作**：`WriteLockEnabled = True` 且 `WriteLocked = True`。

## 2. 讀取/寫入指令的行為
- 如果讀取或寫入指令的目標是**連續的 LBA**，且這些 LBA 位於一個或多個鎖定的範圍內：    
    - 儲存設備**必須終止該指令**，並回傳 **"資料保護錯誤"**（Data Protection Error，如參考規範中所定義）。

## 3. 處理跨越多個 LBA 範圍的指令
如果讀取或寫入指令**跨越多個 LBA 範圍**，且**並非所有範圍都被鎖定**，其行為取決於 **Range Crossing** 的設定：

### 情況 1：Range Crossing = 0
- 如果 `Range Crossing = 0`：
    - 儲存設備**應處理資料傳輸**，即使指令跨越多個 LBA 範圍。        
### 情況 2：Range Crossing = 1
- 如果 `Range Crossing = 1`：    
    - 儲存設備**必須終止該指令**，並回傳 **"其他無效指令參數"**。

![[Pasted image 20250314055133.png]]