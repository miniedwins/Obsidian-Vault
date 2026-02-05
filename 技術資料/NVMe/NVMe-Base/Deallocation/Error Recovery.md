## 概要說明

主機可透過 **Error Recovery Feature** 中的 **DULBE** (Deallocated or Unwritten Logical Block Error Enable) 位元來決定，當讀取到 **deallocated block** 的時候，控制器是否要回報錯誤訊息 (Deallocated or Unwritten Logical Block Error)。

## DULBE 模式說明

**參數定義：**
- **若 DULBE = 1 ( 啟用錯誤回報 )：**    
    - 控制器將**中止 (Abort)** 涉及該區塊的 Copy, Read, Verify, Compare 指令。      
    - 回傳狀態碼：**Deallocated or Unwritten Logical Block**。
        
- **若 DULBE = 0 ( 停用錯誤回報 - 預設 )：**    
    - 控制器**允許讀取**，並回傳特定的預設值。        
    - 回傳內容取決於 **DLFEAT** (Data Level Feature) 中的 **DRB** 欄位。

> **參考：**
> - **DRB :** [Deallocation Read Behavior](Deallocation%20Read%20Behavior.md)
> - **Deallocation :** [Deallocated or Unwritten Logical Blocks](Deallocated%20or%20Unwritten%20Logical%20Blocks.md)