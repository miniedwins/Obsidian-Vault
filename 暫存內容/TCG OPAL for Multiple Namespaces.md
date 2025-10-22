

## Configurable Locking for NVMe Namespaces


## Shadow MBR
主要針對 MBR Controller Table 欄位的設定，搭配 Namespace Management (SEL) 以及 NVMe Format 命令的行為做測試，並且這些欄位控制與命令會影響成功與失敗。



## 問題討論
### TCG Storage Interface Interactions Specification (SIIS)

#### 6.7.1.2.2 Non-Global Range Locking object Interactions
If no namespace exists, then attempts to modify non-Global Range Locking objects SHALL fail with a status of INVALID_PARAMETER. Other operations on non-Global Range Locking objects (e.g., Get, Next) SHALL operate as indicated in the applicable SSC specification.

Q1 : 如果不存在 NS，先前所指定的 Locking Range 是控制器是否需要刪除 ?
A1 : 從上述說明來看，刪除既有的 NS，曾經設定的 Locking Range 應該會保留，不被控制器刪除。

Q2 : 如果 NS 不存在，是否可以設定 Locking Range ?
A2 : 