## 概要說明

從未被寫過的邏輯區塊 (unwritten logical lock)，對主機而言就是一個乾淨的邏輯區塊該定義可以被稱為  **deallocated / unwritten Logic Block**。一旦該 LBA 被寫入下控制器就不再視為 deallocated。

## 哪些命令可以變成 deallocated

- **Dataset Management** ( Trim/Deallocate )。        
- **Write Zeroes** ( 寫入零 )。        
- **Sanitize** ( 物理清除 )。





> **參考：**
> **Error Recovery ：** [Error Recovery](../Error%20Recovery.md)