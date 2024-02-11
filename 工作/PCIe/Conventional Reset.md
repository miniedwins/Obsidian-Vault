- Fundamental Reset
	- Cold Reset : 
		- 主電源 (main power) 開啟或是重啟電源，都會導致 `Cold Reset`
	- Warm Reset : 主電源保持不變，改變系統的電源狀態下，進而觸發裝置 `Warm Reset`
		- PCIe Spec 沒有規範下列作法
			- 如何觸發 `Warm Reset`
			- PCIe 裝置如何自行觸發 `Warm Reset`
	- Hot Reset
		- 
## Fundamental Reset

一般發生在整個系統重新啟動，但也可以針對單一個裝置執行
**備註 : 目前暫時未看到如何對單一個裝置執行 `Fundamental Reset`**

- 主要由硬體控制並且重置整個裝置回到所有的初始狀態，包含以下 : 
	- hardware logic
	- port status
	- configuration registers

這裡要注意的是除了暫存器 `sticky bits`，無法透過 `Fundamental Reset` 清除
若是要將 `sticky bits`清除，則需要完整的將電源 (main power) 以及輔助電源 (Vaux) 移除
