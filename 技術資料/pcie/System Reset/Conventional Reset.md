# Conventional Reset

一般發生在整個系統重新啟動，也可以針對某一個 PCIe 裝置進行 Reset。

Conventional Reset 主要分為下列幾種，如下所示 : 

- PCI Express Conventional Reset
	- Fundamental Reset
		- Cold Reset
		- Warm Reset
	- Non-Fundamental Reset
		- Hot Reset
		- Function Level Reset (FLR)

主要由系統使用 auxiliary signal `PERST#` 初始化 PCIe 裝置，重新初始化所有的暫存器狀態 `hardware logic`、`port status` 以及 `configuration registers` 都會被重置。不過這裡要注意的是暫存器 `sticky bits` 無法透過 `Fundamental Reset` 清除，若是要將 `sticky bits`清除，則需要完整的將電源 (main power) 以及輔助電源 (Vaux) 移除。

當訊號 `PERST#` 傳遞給 `Component or Adapter Card`，就會使用訊號作為 `Fundamental Reset`。若是不支援 `PERST#` 訊號，當主電源開啟後，PCIe 裝置需要自動進行 `Fundamental Reset` 或是偵測到電壓後也會進行 Reset（當裝置發現供電超過其標準電壓時，也必須要觸發 Reset）

> 注意 : Conventional Reset ( cold, warm, or hot ) 都必須要回到初始狀態，除了暫存器 `sticky bits`。

## Fundamental Reset

### Cold Reset

主電源 ( Main Power ) 開啟或是重啟電源 ( Power Cycle )，都會導致 Cold Reset。

例如 : 從開啟電源到穩定，IO Controller Hub (ICH) 晶片可能會產生 PERST#，

A central resource device such as a chipset in the PCI Express system provides
this reset. For example, the IO Controller Hub (ICH) chip in Figure 18‐1 on page
836 may generate PERST# based on the status of the system power supply
‘POWERGOOD’ signal, since this indicates that the main power is turned on
and stable. If power is cycled off, POWERGOOD toggles and causes PERST# to
assert and deassert., resulting in a Cold Reset.
### Warm Reset

不用移除裝置或是主電源 ( 保持電源不變 )，例如 : 改變系統的電源管理狀態，可能會觸發 Warm Reset。 
但是 PCIe 協議並沒有規範相關定義。
## Non-Fundamental Reset

### Hot Reset

這是一種帶內訊號 ( In-Band ) 機制，橋接器 (Bridge) 又或者是軟體可以設定它們的 `Configuration Space`，重置已配置的鏈路和關聯的下游 (Downsteam) 設備。

### Function Level Reset（FLR）
