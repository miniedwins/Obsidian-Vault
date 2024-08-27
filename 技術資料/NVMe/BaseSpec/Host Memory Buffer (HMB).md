- 系統會分配一段記憶體空間給控制器使用，該記憶體內容無法被系統修改。
- 第一次配置 `HMB` 記憶體空間，`Memory Return Bit` 設定為 `0`。
- 使用期間內，控制器需要確保資料內容沒有遺失。
- 經過重置或是關機等事件，系統會要求控制器釋放記憶體空間，並且回收已配置的記憶體空間。
- 休眠 (D3Cold)
	- 進入休眠
		- 無法保留 `HMB`。 
	- 系統恢復
		- 應該要分配先前所設定的記憶體位址。
		- `Memory Return Bit` 設定為 `1`。
## 檢查是否支援 HMB 

可以從 `Identify Controller Data Structure` 取得 `HMPRE` 屬性
- HMPRE = 0 (不支援)
- HMPRE = non-zone (支援)

![[identify_ctrl_hmpre.png]]
## 取得 HMB 資訊 

- nvme-cli 執行後會顯示兩個資訊內容
	- `Completion Queue Entry Dword 0`
	- `Attributes Data Structure`

```
$ nvme get-feature -f 0x0d /dev/nvme0 -l 64
get-feature:0x0d (Host Memory Buffer), Current value:0x00000001
       0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
0000: 00 40 00 00 00 70 88 12 01 00 00 00 10 00 00 00 ".@...p.........."
0010: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
0020: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
0030: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
```
### Completion Queue Entry Dword 0

可以從 `CQ Entry` 得到目前 `HMB` 狀態是否開啟或是關閉，目前 `value=0x01` 代表 Enable。

```
get-feature:0x0d (Host Memory Buffer), Current value:0x00000001
```

![[nvme_hmb_cq_entry_dword0.png]]
### Attributes Data Structure

另外則是 `HMB` 資料結構，描述所使用的容量大小以及作業系統所配置給控制器使用的記憶體位址。

```
       0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
0000: 00 40 00 00 00 70 88 12 01 00 00 00 10 00 00 00 ".@...p.........."
```
![[nvme_hmb_attributes_data_structure.png]]

- HSIZE : `0x00004000h`
	- 計算使用的 HMB 大小需要取得 `MPS` 設定
	- 目前取得 MPS=0，Page Size 使用的大小為 4K
	- Host Memory Buffer Size  =  16384 * 4k = 64MB

![[nvme_cc_memory_page_size.png]]

作業系統分配的記憶體位址，分別為一個是高位址 (HMDALU) 一個是低位址 (HMDAL)
 - HMDAL : `0x12887000`
 - HMDALU : `0x00000001`
 - 完整的記憶體位置 : `0x0000000112887000`

![[hmb_cdw13_14.png]]

這個參數是描述 Host 提供給控制器可以使用主機的記憶體範圍，分配支援資源給控制器所使用，因此 Host 不能去修改這些記憶體範圍的內容，除非該記憶體被回收。

- HMDLEC : `0x00000010` 

![[hmb_descriptor_list.png]]
## Enable HMB

- 記憶體空間是由系統分配，若是關閉後想要再開啟需要手動設定。  
	- 指定先前系統所配置的位址 `0x0000000112887000`。
	- 由於是配置先前所指派的記憶體空間，`Mmemory Return Bit` 需要設定為 `1`。

**注意 : 記憶體是系統分配的，不能隨意指定一個記憶體位址。**

![[hmb_cdw11.png]]

```
$ nvme admin-passthru --opcode=0x09 --cdw10=0x0d --cdw11=0x01 --cdw12=0x00004000 --cdw13=0x12887000 --cdw14=0x00000001 --cdw15=0x10 /dev/nvme0

Admin Command Set Features is Success and result: 0x00000000
```
## Disable HMB

一旦取消 HMB，控制器無法再使用 `Host Memory Buffer` 任何資料，直到再一次的 Enable。

```
$ nvme set-feature -f 0x0d --value=0x00 /dev/nvme0
set-feature:0x0d (Host Memory Buffer), value:00000000, cdw12:00000000, save:0
```