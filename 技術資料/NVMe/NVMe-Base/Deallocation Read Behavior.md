
## DRB 是什麼
Deallocation Read Behavior（DRB）欄位用來表示，當主機讀取一個已經被 [Deallocated](Deallocated.md) 的 logical block 時，控制器應該要回傳 logical block 的資料內容以及其中的 metadata（不包含 protection information）。

![](assets/Deallocation%20Read%20Behavior/file-20260113104059992.png)

>資訊來源 :   Identify Namespace Data Structure, NVM Command Set