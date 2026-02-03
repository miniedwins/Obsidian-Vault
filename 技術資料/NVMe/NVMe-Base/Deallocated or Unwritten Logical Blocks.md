## 概要說明

從未被寫過的邏輯區塊 (unwritten logical lock)，對主機而言就是一個乾淨的邏輯區塊該定義可以被稱為 **deallocated / unwritten logic block**。一旦資料被寫入 LBA，控制器就不再視為 deallocated。

## 哪些命令可以變成 Deallocated Block

- **Dataset Management** (Trim/Deallocate)。        
- **Write Zeroes** (寫入零)。        
- **Sanitize** (物理清除)。

## 主機讀取 Deallocated Block 行為的影響

因為當區塊被解除配置 (Deallocated/Trimmed) 後，在控制器的映射表 (L2P Table) 中該 LBA 會標記為「未映射 (Unmapped)」。控制器看到未映射，**並不會去讀取物理 Flash**，而是直接由邏輯層「無中生有」變出 00 或 FF 給你。既然沒讀 Flash，也就不會拋出 ECC 錯誤。

另外還需要設定 `DULBE` (Deallocated or Unwritten Logical Block Error)，該欄位定義在 **Error Recovery ( Feature Id: 05h )**，它是用來決定當主機讀取「deallocated block」時，控制器回報錯誤 (Deallocated or Unwritten Logical Block error) 還是資料 `0x00` 或是 `0xFF` (根據 **DRB** 欄位設定)。

若是當控制器在設定 `DULBE=1` 並且邏輯區塊是 `deallocated block` 會拒絕如下命令:  
Abort Commands : Copy, Read, Verify, or Compare commands

**補充說明 :** 
- 控制器會根據 **Error Recovery** 設定是否要回報錯。
- 控制器會根據 **DRB ( Deallocation Read Behavior )** 欄位來決定回傳的是 00 或是 FF 資料。

> **參考：**
> **Error Recovery ：** [Error Recovery](Error%20Recovery.md)
> **Deallocation Read Behavior ：** [Deallocation Read Behavior](Deallocation%20Read%20Behavior.md)