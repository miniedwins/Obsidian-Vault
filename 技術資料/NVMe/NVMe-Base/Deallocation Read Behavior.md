
## DRB 是什麼
Deallocation Read Behavior（DRB）欄位用來表示，當主機讀取一個已經被 [Deallocated](Deallocated.md) 的邏輯區塊 ( Logic Block )，控制器應該要回傳的什麼樣的資料內容以及其中的 Metadata（不包含 Protection Information）。

![](assets/Deallocation%20Read%20Behavior/file-20260113142243475.png)

>資訊來源 :   Identify Namespace Data Structure, NVM Command Set