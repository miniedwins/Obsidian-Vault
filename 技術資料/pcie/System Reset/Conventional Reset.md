# Conventional Reset

Conventional Reset 主要分為下列幾種，如下所示 : 

- PCI Express Conventional Reset
	- Fundamental Reset
		- Cold Reset
		- Warm Reset
	- Non-Fundamental Reset
		- Hot Reset
		- Function Level Reset (FLR)

一般發生在整個系統重新啟動，主要由系統使用 auxiliary signal `PERST#` 初始化 PCIe 裝置，接下來這些暫存器狀態 `hardware logic`、`port status` 以及 `configuration registers` 都會被重置。不過這裡要注意的是暫存器 `sticky bits` 無法透過 `Fundamental Reset` 清除，若是要將 `sticky bits`清除，則需要完整的將電源 (main power) 以及輔助電源 (Vaux) 移除。

當訊號 `PERST#` 傳遞給 `Component or Adapter Card`，就會使用訊號作為 `Fundamental Reset`。若是不支援 `PERST#` 訊號，當主電源開啟後，PCIe 裝置需要自行觸發 `Fundamental Reset`。

> 注意 : Conventional Reset (cold, warm, or hot) 都必須要回到初始狀態，除了暫存器 `sticky bits`。

## Fundamental Reset

### Cold Reset

主電源 (main power) 開啟或是重啟電源，都會導致 Cold Reset。

### Warm Reset

不用移除裝置或是主電源，只要重新對裝置供電，稱之為 Warm Reset。
  
PCIe Spec 沒有規範 Warm Reset 執行方法 : 
- 系統如何產生 Warm Reset
- PCIe 裝置如何自行觸發 Warm Reset。
## Non-Fundamental Reset

### Hot Reset

這是一種 `In-Band` 機制，軟體設定讓鏈結電路進入到 `Electrical Idle` 並且 Disabling Link，造成下游 Downstream 裝置觸發 `Hot Reset`。
### Function Level Reset（FLR）
