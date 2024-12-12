**參數** : `bssplit`
**說明** : 
- 使用不同大小的 I/O 來模擬真實場景中的數據讀寫操作，並為每個數據塊大小指定一個比例。  
- 所有比例相加必須等於 100%。
**語法格式**：
- `bssplit=<blocksize>/<percentage>:<blocksize>/<percentage>:...`
- **`blocksize`**：指定 I/O 的大小（例如：`4k`, `128k`, `1024k`）。
- **`percentage`**：指定該 I/O 大小的比例（例如：`80%`, `10%`）。
**範例** :
- 模擬如下比例的隨機寫操作：
	- 80% 的 I/O 使用 4k
	- 10% 的 I/O 使用 128k
	- 10% 的 I/O 使用 1024k
```shell
$ fio --filename=/dev/sdx --name=test --ioengine=libaio --iodepth=32 --size=100% -- bssplit=4k/80:128k/10:1024k/10 --rw=randwrite
```