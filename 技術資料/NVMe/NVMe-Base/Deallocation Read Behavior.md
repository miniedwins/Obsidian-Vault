
## DRB 是什麼
Deallocation Read Behavior（DRB）欄位用來表示，當主機讀取一個已經被 deallocation block 邏輯區塊，控制器應該要回傳的什麼樣的資料內容以及其中的 Metadata（不包含 Protection Information）。

![](assets/Deallocation%20Read%20Behavior/file-20260113142243475.png)

**參數定義：**
- 位於 Identify – Namespace Data Structure, NVM Command Set
- Bits 02:00 –  Deallocation Read Behavior