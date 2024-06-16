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

當訊號 `PERST#` 傳遞給 `Component or Adapter Card`，PCIe 裝置就會使用訊號作為 `Fundamental Reset`。若是不支援 `PERST#` 訊號，當主電源開啟後，PCIe 裝置需要自我自動進行 `Fundamental Reset` 或是偵測到電壓後也會進行 Reset（當裝置發現供電超過其標準電壓時，也必須要觸發 Reset）。

> 注意 : Conventional Reset ( cold, warm, or hot ) 都必須要回到初始狀態，除了暫存器 `sticky bits`。

## Fundamental Reset

### Cold Reset

主電源 ( Main Power ) 開啟或是重啟電源 ( Power Cycle )，都會導致 Cold Reset。

例如 :  Intel IO 控制器中心 (ICH) 晶片可以根據系統電源的狀態產生 PERST# 訊號，這表示主電源已打開且穩定。如果電源關閉會造成 PERST# Assert and Dessert 然而導致 Cold Reset。
### Warm Reset

不用移除裝置或是主電源 ( 保持電源不變 )，例如 : 改變系統的電源管理狀態，可能會觸發 Warm Reset。 
但是 PCIe 協議並沒有規範相關定義。
## Non-Fundamental Reset

### Hot Reset ( In-band Reset )

這是一種帶內訊號 ( In-Band ) 機制，透過軟體設定 `Secondary Bus Reset Bit` 可以讓 PCIe 設備重置回到初始狀態，該位元設定的位置在 `Bridge Control configuration register`，重置已配置的鏈路和關聯的下游設備 ( Downsteam )。

![image.png](https://raw.githubusercontent.com/miniedwins/images/main/obsidian/pcie20240616123757.png)

將該位元 `Secondary Bus Reset Bit` 設定為 `1` 然後再設定為 `0`，即可以觸發 `Hot Reset` 動作。

![image.png](https://raw.githubusercontent.com/miniedwins/images/main/obsidian/pcie20240615205607.png)

Switch 接受到來自上游埠 ( Upstream Port ) hot reset，它會廣播給下游所有的 PCIe 裝置。當下游所有的裝置收到 hot reset，會自動進行 Reset 動作。

![image.png](https://raw.githubusercontent.com/miniedwins/images/main/obsidian/pcie20240616123302.png)

此時 PCIe 裝置的 LTSSM 會經歷幾個階段 `Recovery -> Hot Reset -> Detect` 狀態，然後開始進行 `Link Training`。

![image.png](https://raw.githubusercontent.com/miniedwins/images/main/obsidian/pcie20240615205048.png)

當下游所有設備重置後，這些 PCIe 裝置的狀態 hardware logic, port states and configuration registers (expect sticky registers) 都會回到它們的初始狀態 ( Default Conditions )。

另外一種也可以透過軟體 `Disable a Link`
### Function Level Reset（FLR）
