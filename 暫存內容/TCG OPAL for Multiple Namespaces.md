

## Configurable Locking for NVMe Namespaces


## Shadow MBR
主要針對 MBR Controller Table 欄位的設定，搭配 Namespace Management (SEL) 以及 NVMe Format 命令的行為做測試，並且這些欄位控制與命令會影響成功與失敗。



## 問題討論
### TCG Storage Interface Interactions Specification (SIIS)

### TCG_Storage_Configurable_Locking_for_NVMe_Namespaces

#### Deassign Method Operation
Q1 : 移除 Deassigning a Namespace Non-Global Range Locking object
	a. 是否會變成 Namespace Global Locking Range ?
	b. 若是變成 Namespace Global Locking Range，應該會是使用同一把 NGLR 金鑰
