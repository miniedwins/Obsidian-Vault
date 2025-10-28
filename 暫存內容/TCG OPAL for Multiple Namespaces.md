

## Configurable Locking for NVMe Namespaces


## Shadow MBR
主要針對 MBR Controller Table 欄位的設定，搭配 Namespace Management (SEL) 以及 NVMe Format 命令的行為做測試，並且這些欄位控制與命令會影響成功與失敗。


## Deassign Method of Operation
1️⃣ 先把所有 **Namespace Non-Global Range Locking object** 全部解除 (Deassign)  
2️⃣ 再解除 **Namespace Global Range Locking object**  
3️⃣ 最後才能執行 **Namespace Management command → Delete Namespace**

## 問題討論
### TCG Storage Interface Interactions Specification (SIIS)

### TCG_Storage_Configurable_Locking_for_NVMe_Namespaces

#### Deassign Method Operation
Q1 : 移除 Deassigning a Namespace Non-Global Range Locking object
	a. 是否會變成 Namespace Global Locking Range ?
	b. 若是變成 Namespace Global Locking Range，應該會是使用同一把 NGLR 金鑰

Q2 :  若是解除 Namespace Global Range，並且設定 NamespaceGlobalRangeKey=True
該金鑰會被保留，但是如果再使用 Assign Method 設定 Namespace Global Range，當前被設定的
Namespace Global Range 他的 ActiveKey 還會使用相同一把金鑰嗎 ?

個人解讀：

> 即使這個 Namespace Global Locking object 將來被再次 Assign，
> 它不能再用舊的金鑰（舊的可能仍能解舊資料）。  
> 所以這裡要重新產生新的 MEK 值（但不會立刻應用在媒體上）。

這樣就確保：
- 現在媒體上的資料仍可用（因為 Global Locking object 接管了那把 key）；    
- 將來重新分配這個 Namespace Locking object 時，它不會意外拿到舊金鑰

>SPEC : Configurable Locking for NVMe Namespaces and SCSI LUNs ( PAGE : 34 )



### 後續需要解決的問題
1. 如何區別回傳的錯誤 ( TCG OPAL 或是 NVMe Error )
2. 測試 CNL 需要測試軟體需要維護一個 Locking Table
3. 如何將所有的核心測試方法整理成一個 Q&A
