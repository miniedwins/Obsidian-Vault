## 概要說明

從未被寫過的邏輯區塊 (unwritten logical lock)，對主機而言就是一個乾淨的邏輯區塊該定義可以被稱為  **deallocated / unwritten Logic Block**。一旦資料被寫入 LBA，控制器就不再視為 deallocated。

## 哪些命令可以變成 deallocated block

- **Dataset Management** ( Trim/Deallocate )。        
- **Write Zeroes** ( 寫入零 )。        
- **Sanitize** ( 物理清除 )。

## 主機讀取 deallocated block 行為的影響

因為當區塊被解除配置 (Deallocated/Trimmed) 後，在控制器的映射表 (L2P Table) 中該 LBA 會標記為「未映射 (Unmapped)」。控制器看到未映射，**根本不會去讀物理 Flash**，而是直接由邏輯層「無中生有」變出 00 或 FF 給你。既然沒讀 Flash，就不會有 ECC 錯誤。

因此還要額外設定 `DULBE` ( Deallocated or Unwritten Logical Block Error )，該欄位設定位於 **Error Recovery ( Feature Id: 05h )** 用來決定當主機讀取「deallocated block 」時，控制器回傳給主機讀取報錯還是資料 00 或是 FF ( 根據 **DRB** 欄位設定 )。

**補充說明 :** 
控制器會根據 **DRB ( Deallocation Read Behavior )** 欄位來決定回傳的是 00 或是 FF 資料。

> **參考：**
> **Error Recovery ：** [Error Recovery](Error%20Recovery.md)
> **Deallocation Read Behavior ：** [Deallocation Read Behavior](Deallocation%20Read%20Behavior.md)