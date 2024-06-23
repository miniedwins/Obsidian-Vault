# Hot Reset ( In-band Reset )

這是一種帶內訊號 ( In-Band ) 機制，透過軟體設定 `Secondary Bus Reset Bit` 可以讓 PCIe 設備重置回到初始狀態，該位元設定的位置在 `Bridge Control configuration register`，重置已配置的鏈路和關聯的下游設備 ( Downsteam )。

![image.png](https://raw.githubusercontent.com/miniedwins/images/main/obsidian/pcie20240616123757.png)

將該位元 `Secondary Bus Reset Bit` 設定為 `1` 然後再設定為 `0`，即可以觸發 `Hot Reset` 動作。

![image.png](https://raw.githubusercontent.com/miniedwins/images/main/obsidian/pcie20240615205607.png)

若是 Switch 接受到來自上游埠 ( Upstream Port ) hot reset，它會廣播給下游所有的 PCIe 裝置。當下游所有的裝置收到 hot reset，會自動進行 Reset 動作。

![image.png](https://raw.githubusercontent.com/miniedwins/images/main/obsidian/pcie20240616123302.png)

此時下游 PCIe 裝置的 LTSSM 會經歷幾個階段 `Recovery -> Hot Reset -> Detect` 狀態，最後開始進行鏈路訓練 ( Link Training )。

當下游所有設備重置後，這些 PCIe 裝置的狀態 hardware logic, port states and configuration registers (expect sticky registers) 都會回到它們的初始狀態 ( Default Conditions )。

![image.png](https://raw.githubusercontent.com/miniedwins/images/main/obsidian/pcie20240615205048.png)

另外一種 `Hot Reset` 方式，僅限操作在下游埠 ( Downstream Port )，透過軟體設定 `Link Disable Bit`，該位元設定的位置在  `Link Control Register`。此時被設定的下游阜狀態也會回到 `Recovery LTSSM` ，並且開始發送 `TS1 with the disable bit set` 給上游阜 ( Upstream Port )。

當上游阜收到 `TS1s with the Disabled bit set`，Physical Layer signals LinkUp=0 (false)，以及所有的 Lanes 會處於在 `Electrical Idle`，在經過 2ms 時間後，上游埠會回到 `Detect` 狀態，而下游埠會保持在 `Disable LTSSM` 狀態，直到退出這個狀態 ( 例如 : Clearing the Link Disable bit )。因此下游埠連結將會一直保持停用 ( Disabled ) 狀態，並且在此之前都不會嘗試鏈路訓練 ( Linking Training )。

![image.png](https://raw.githubusercontent.com/miniedwins/images/main/obsidian/pcie20240616162800.png)

# Function Level Reset（FLR）

FLR 可讓軟體重置有多個功能設備 ( Multi Function Device ) 中的其中一個功能，並且不影響所有人共享的鏈路狀態 ( Link Status )。然而 FLR 功能並非必需支援，不過 SPEC 強烈建議廠商需要實作這項功能。

FLR 會把對應 Function 的內部狀態的暫存器重設，但以下暫存器不會受到影響 : 
- Sticky-type registers ( ROS, RWS, RW1CS )
- Registers defined as type HwInit
- These other fields or registers

為了避免發生問題，SPEC 所建議的基本事項 : 
- 為了防止資料損壞，需要停止所有 PCI Express 和外部 I/O（非 PCI Express）。 
- 不得保留任何軟體可讀狀態，其中可能包含先前所留下的秘密資訊 ( 例如 : Memory 需要被清除 )。
- 由於 FLR 是由 `Configuration write` 所完成，因此 Function 必須要回傳一個完成 ( Completion ) TLP 封包，然後才開始進行初始化。
- FLR 需要在 100ms 內完成

FLR 執行過程中 :
- Device Function 不能被使用。
- 任何一個請求 ( Request ) 封包抵達，則允許默默丟棄該請求，並且不記錄或將其標記為錯誤。
- 一個來自完成 ( Completionple ) 封包，則會允許將當作意外完成 `UC` ( Unexpected Completion ) 進行處理，或是默默地丟棄，並且不其記錄或標記為意外完成。
- 初始化過程中，如果收到 `Configuration Request`，Function 必需要回覆 `CRS` ( Configuration Request Retry Status )  Completion Status。

Reste 退出後 : 
- Reset 狀態退出後，必須在 20ms 內開始 Link Training。
- 系統軟體啟動 FLR 至少要等待 100ms 完成重置，然後才能嘗試發送 `Configuration Requests`。
- 如果軟體等待 100ms 開始發送  Configuration Request，但是 Device 初始化尚未完成，因此 Device需要回覆 `CRS` ( Configuration Request Retry Status )  Completion Status。

系統需要在執行前會檢查 `Device Capacity Register Bit28`  是否設定為 `1` 來確認有無支援 FLR。

![image.png](https://raw.githubusercontent.com/miniedwins/images/main/obsidian/pcie20240622184929.png)

如果支援 FLR，那麼軟體就可以通過 `Device Control Register Bit15` 來進行 `Function Reset`。

![image.png](https://raw.githubusercontent.com/miniedwins/images/main/obsidian/pcie20240622190428.png)

只要將 `Initiate Function Level Reset` 設定為 `1`，即可觸發 FLR 功能。

![image.png](https://raw.githubusercontent.com/miniedwins/images/main/obsidian/pcie20240622190547.png)
