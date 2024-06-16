# Hot Reset ( In-band Reset )

這是一種帶內訊號 ( In-Band ) 機制，透過軟體設定 `Secondary Bus Reset Bit` 可以讓 PCIe 設備重置回到初始狀態，該位元設定的位置在 `Bridge Control configuration register`，重置已配置的鏈路和關聯的下游設備 ( Downsteam )。

![image.png](https://raw.githubusercontent.com/miniedwins/images/main/obsidian/pcie20240616123757.png)

將該位元 `Secondary Bus Reset Bit` 設定為 `1` 然後再設定為 `0`，即可以觸發 `Hot Reset` 動作。

![image.png](https://raw.githubusercontent.com/miniedwins/images/main/obsidian/pcie20240615205607.png)

Switch 接受到來自上游埠 ( Upstream Port ) hot reset，它會廣播給下游所有的 PCIe 裝置。當下游所有的裝置收到 hot reset，會自動進行 Reset 動作。

![image.png](https://raw.githubusercontent.com/miniedwins/images/main/obsidian/pcie20240616123302.png)

此時下游 PCIe 裝置的 LTSSM 會經歷幾個階段 `Recovery -> Hot Reset -> Detect` 狀態，最後開始進行鏈路訓練 ( Link Training )。

![image.png](https://raw.githubusercontent.com/miniedwins/images/main/obsidian/pcie20240615205048.png)

當下游所有設備重置後，這些 PCIe 裝置的狀態 hardware logic, port states and configuration registers (expect sticky registers) 都會回到它們的初始狀態 ( Default Conditions )。

另外一種 `Hot Reset` 方式，僅限操作在下游阜 ( Downstream Port )，透過軟體設定 `Link Disable Bit`，該位元設定的位置在  `Link Control Register`，此時被設定的下游阜狀態也會回到 `Recovery LTSSM` ，並且開始發送 `TS1 with the disable bit set` 給上游阜 ( Upstream Port )。

![image.png](https://raw.githubusercontent.com/miniedwins/images/main/obsidian/pcie20240616162800.png)

當上游阜收到 `TS1s with the Disabled bit set`，Physical Layer signals LinkUp=0 (false)，以及所有的 Lanes 會處於在 `Electrical Idle`，在經過 2ms 時間後，上游阜會回到 `Detect` 狀態，而下游阜會保持在 `Disable LTSSM` 狀態，直到退出這個狀態 ( 例如 : Clearing the Link Disable bit )。因此連結將保持停用 ( Disabled ) 狀態，在此之前都不會嘗試鏈路訓練 ( Linking Training )。

# Function Level Reset（FLR）
