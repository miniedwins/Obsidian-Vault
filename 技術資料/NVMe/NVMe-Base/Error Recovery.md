

#### **讀取行為控制 (Read Behavior Control)**

主機可透過 **Error Recovery Feature** 中的 **DULBE** (Deallocated or Unwritten Logical Block Error Enable) 位元來決定控制器的反應：

- **若 DULBE = 1 (啟用錯誤回報)：**
    
    - 控制器將**中止 (Abort)** 涉及該區塊的 Copy, Read, Verify, Compare 指令。
        
    - 回傳狀態碼：**Deallocated or Unwritten Logical Block**。
        
- **若 DULBE = 0 (停用錯誤回報 - 預設)：**
    
    - 控制器**允許讀取**，並回傳特定的預設值。
        
    - 回傳內容取決於 **DLFEAT** (Data Level Feature) 中的 **DRB** (Deallocation Read Behavior) 欄位。

設定 DULBE 不是因為有 ECC 錯誤要處理，而是主機自己決定「我希不希望知道這裡其實是空的？」
- **一般使用 (DULBE=0)：** 讀起來全是 0，軟體比較好寫，不會崩潰。    
- **嚴謹檢查 (DULBE=1)：** 讀取就報錯，適合用來檢查 Trim 有沒有成功。