# Telemetry



## Telemetry 介紹

Telemetry log 主要讓開發商收集內部資料去改善產品功能與穩定性。Telemetry 資料的收集方式可以透過兩種方法取得 initiated by the host or by the controller，資料會存放在 `Telemetry Host-Initiated` and `Telemetry Controller-Initiated` log page，因此我們可以透過 `get-log` 命令方式取得 telemetry 資料。由於要收集資料的方法與內容是由開發商所指定，所以無法得知資料內容的格式。

Telemetry data 定義兩個資料結構，`Host-Initiated` 以及 `Controller-Initiated` 彼此之間相互獨立，描述不同 log data 資訊，所以分開是很合理的。資料結構前 512 Bytes 代表 Header 資訊內容 (可由 get-log page 命令取得)，而之後都是表示 `data log`，這些都是由 Data Blocks (ex : Telemetry Host-Initiated Data Block 1...n) 所組成的，每一個 block 空間大小為 512 Bytes。

`Data Blocks` 範圍分成三個 Telemetry Data Areas small (Area 1) / medium (Area 2) / largest (Area 3)，每個 Phrase Area 它們的 Blocks 範圍不一樣 ，但是開始的位置都是在 Telemetry Data Block 1，當這三個 Phrase Blocks 空間已滿的時候，就會覆蓋先前的舊資訊，此時 Data Generation Number will increase 1。

下列範例圖示，也就是前面說提到的 `Phrease Area`， 每個 Data Area 有不同的 Block Number 範圍，這些都是由廠商所自訂，包含需要收集什麼資料也是由開發商所指定。Data Area 1, Data Area 2, Data Area 3 都有相同 Telemetry Data (Block 1 to Block 65 )，Data Area 2 and Data Area 3 都有相同 Telemetry Data (Block 65 to Block 1000 )，Data Area 3 則擁有所有完整的 Telemetry Data。

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/telemetry_data_areas.png)



## 如何執行命令

### 檢查控制器是否支援 

說明 : 確認控制器是否有支援 telemetry feature。

Controller Attributes (CTRATT) :

* 261 Bytes : Bit 3
  * 1 : Support
  * 0 : Don't Support

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/identify_controller/Identify_Controller_LPA.png)

~~~shell
nvme id-ctrl | grep lpa
~~~



### 讀取 Initialed Header (Ctrl)

說明 : 讀取標頭檔的訊息可以得知每個 `Phrase` 所指定儲存的 `Block` 範圍，可以通過指定的範圍將取得 log data 並儲存成檔案，提供原廠分析。因此我們可以透過 get-log 命令，先取得標頭檔內容，了解每個 Phrase Block size。

我們以取得 `Ctrl-Initialed log` 標頭檔為範例，說明如下 : 

透過  get-log 命令取得 Ctrl-Initialed log 標頭檔，`--lpo=0` 代表開始位置，`--log-len` 取得長度為 512 Bytes

~~~shell
nvme get-log /dev/nvme0 --log-id=0x08 --lpo=0 --log-len=512 -b > telemetry_ctrl_header_log
~~~

使用  hexdump 指定讀取 512 Bytes 資料內容

~~~shell
hexdump -C -n 512 telemetry_ctrl_header_log
~~~

目前我們測試使用 Sample，但讀取到的 Data Area 1,2,3 都是一樣的 block number size，看起來應該沒有做好每個 Area 指定的 Block size 範圍，或許並不算是大問題。 

~~~shell
00000000  08 00 00 00 00 0b 6f ec  9f 33 9f 33 9f 33 00 00  |......o..3.3.3..|
00000010  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
00000170  00 00 00 00 00 00 00 00  00 00 00 00 00 00 01 01  |................|
00000180  50 61 39 34 46 46 42 43  41 32 33 42 37 38 30 31  |Pa94FFBCA23B7801|
00000190  36 31 34 32 37 31 43 4d  5a 30 43 38 56 51 fa 00  |614271CMZ0C8VQ..|
000001a0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
000001b0  00 00 00 00 00 00 00 00  d8 d6 00 00 d0 84 00 00  |................|
000001c0  00 00 00 00 0a 00 00 00  00 00 00 00 00 00 00 00  |................|
000001d0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
000001e0  00 00 00 00 00 00 00 00  c0 03 00 00 01 00 00 00  |................|
000001f0  20 00 08 0b 00 00 00 00  31 30 39 31 61 66 36 63  | .......1091af6c|
00000200
~~~

根據該資料結構來看 Log Identifier : 0x08，OUI Identifier : 0xec6f0b，Data Area 1, 2, 3 block size 皆為 0x339f。

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/log_page/log_page_telemetry_controller_initiated.png)



### 如何取得 telemetry log page

使用 nvme-cli **(version >= 1.6)** 有兩種下載方法，如下所述 : 

* telemetry-log : 可以下載 `Host-Initialed log`，但是無法下載 `Ctrl-Initialed log`
* get-log : 需要自行調整偏移量以及下載大小才能夠將所有的資料取得

接下來示範下載 Host-Initialed 以及 Ctrl-Initialed 並且取得 Data Area 3 log ，範例如下 :

#### Host-Initialed 

說明 : nvme-cli 已經幫我們處理好偏移量以及下載大小的問題，所以很簡單就可以拿到。

執行方式 : 使用 telemetry-log 命令指定 `data-area=3`

~~~shell
nvme telemetry-log /dev/nvme0 --data-area=3 --output-file=telemetry_log.bin
~~~

#### Ctrl-Initialed

說明 : 讀取標頭檔案所描述的 data block 容量，在依據取得的容量給腳本執行。

執行方式 : 撰寫 Shell 腳本，並使用 get-log 命令取得 telemetry-log

*備註 : 該方法可以下載 Host-Initialed & Ctrl-Initialed*

~~~shell
# Host-Initialed 標頭檔內容
00000000  08 00 00 00 00 0b 6f ec  9f 33 9f 33 9f 33 00 00  |......o..3.3.3..|
00000010  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
00000170  00 00 00 00 00 00 00 00  00 00 00 00 00 00 01 01  |................|
00000180  50 61 39 34 46 46 42 43  41 32 33 42 37 38 30 31  |Pa94FFBCA23B7801|
00000190  36 31 34 32 37 31 43 4d  5a 30 43 38 56 51 fa 00  |614271CMZ0C8VQ..|
000001a0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
000001b0  00 00 00 00 00 00 00 00  d8 d6 00 00 d0 84 00 00  |................|
000001c0  00 00 00 00 0a 00 00 00  00 00 00 00 00 00 00 00  |................|
000001d0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
000001e0  00 00 00 00 00 00 00 00  c0 03 00 00 01 00 00 00  |................|
000001f0  20 00 08 0b 00 00 00 00  31 30 39 31 61 66 36 63  | .......1091af6c|
00000200
~~~

結果說明 : 

從標頭檔得知該 Block size : `0x339f` (13215 Decimal) 只要將該值換算成多少個 Bytes 即可得知需要取得 log 容量大小，每個 data block 單位是 512 Byes，所以總 log page 大小容量為 : (13215 * 512 ) + 512 = 6,766,592 Bytes。

因為需要下載較大資料量，所以要將資料分成一段一段的方式取得，這邊我們定義最大下載資料量為 4096 bytes，然後透過 offset 的方式偏移起始位置，以遞增偏移量的方式將所有資料下載完畢。

**Sample Code**

~~~shell
DEVICE_NAME="/dev/nvme0"
CTRL_LOG_FILE="telemetry_ctrl_log.bin"
MAX_TRANSFER_SIZE=4096

trans_offset=0
remain_bytes=0
blk_count_bytes=6766592

while [ $trans_offset -lt $blk_count_bytes ]
do
	# 計算剩餘下載空間大小
	remain_bytes=$(echo "${blk_count_bytes}-${trans_offset}" | bc)	
	
	# 4096 bytes 為下載資料大小，直到剩餘空間小於 4096 bytes
	if [ $remain_bytes -lt $MAX_TRANSFER_SIZE ]; then
		chunk_size=$remain_bytes
	else
		chunk_size=${MAX_TRANSFER_SIZE}
	fi
	
	# 將取得 telemetry log 資料遞增寫入到 CTRL_LOG_FILE
	nvme get-log $DEVICE_NAME --log-id=0x8 --lpo=$trans_offset --log-len=$chunk_size -b >> $CTRL_LOG_FILE

	# 計算目前已經下載多少 bytes 大小 
	trans_offset=$(echo "${trans_offset}+${chunk_size}" | bc)
	
	echo -en "Trans_bytes = $trans_offset\r"
done
~~~

以下是描述偏移量 (offset) 動作行為 :  offset 會一直遞增然後到最後，直到 remain_bytes < MAX_TRANSFER_SIZE

(1) offset=0,chunk_size=4096, remain_bytes=6766592

(2) offset=4096, chunk_size=4096,  remain_bytes=6762496

(3) offset=8192, chunk_size=4096, remain_bytes=6758400

(n - 1) ..... End
