# Conventional Reset

一般發生在整個系統重新啟動，也可以針對某一個 PCIe 裝置進行 Reset。

**Conventional Reset** 主要分為下列幾種，如下所示 : 

- **Fundamental Reset**
	- [[Cold Reset]]
	- [[Warm Rset]]
- **Non-Fundamental Reset**
	- [[Hot Reset]]
	- [[Function Level Reset]]

主要由系統使用 auxiliary signal `PERST#` 初始化 PCIe 裝置，重新初始化所有的暫存器狀態 `hardware logic`、`port status` 以及 `configuration registers` 都會被重置。不過這裡要注意的是暫存器 `sticky bits` 無法透過 `Fundamental Reset` 清除，若是要將 `sticky bits`清除，則需要完整的將電源 (main power) 以及輔助電源 (Vaux) 移除。

當訊號 `PERST#` 傳遞給 `Component or Adapter Card`，PCIe 裝置就會使用訊號作為 `Fundamental Reset`。若是不支援 `PERST#` 訊號，當主電源開啟後，PCIe 裝置需要自我自動進行 `Fundamental Reset` 或是偵測到電壓後也會進行 Reset（當裝置發現供電超過其標準電壓時，也必須要觸發 Reset）。

> 注意 : Conventional Reset ( cold, warm, or hot ) 都必須要回到初始狀態，除了暫存器 `sticky bits`。