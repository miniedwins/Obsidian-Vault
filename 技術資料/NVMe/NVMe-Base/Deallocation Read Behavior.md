
## DRB 是什麼
Deallocation Read Behavior（DRB）欄位用來指示，當主機讀取一個已被 [Deallocated](Deallocated.md)Deallocated.md)Deallocated 的 logical block時，這個欄位用來表示控制器應回傳該 logical block 的資料內容以及其中的 metadata（不包含 protection information）。

![](assets/Deallocation%20Read%20Behavior/file-20260113104059992.png)

>資訊來源 :  Identify – Identify Namespace Data Structure, NVM Command Set