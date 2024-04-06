# 資料保護說明

端到端資料保護將資料的完整性保護範圍從SSD內部延伸到外部鏈路，以防止靜默錯誤產生——通過對邏輯塊資料（Logical Block Data，通常指使用者資料）新增額外的PI（Protection Information，保護資訊，如CRC），使其作為資料的中繼資料 (Metadata) 被一同傳輸，主機端和NVM控製器都可以在接收到資料後，根據PI的內容對資料完整性進行校驗，以確定這些資料是否真的可用。

端到端資料保護的關鍵就在於PI（Protection Information）作為中繼資料時的傳輸與校驗，中繼資料有DIF和DIX兩種方式，經過T10組織的相關工作已經實現了標準化。簡單來說，DIF即中繼資料與使用者資料（LBA Data）連續存放；而 DIX格式則是中繼資料與使用者資料單獨存放；可以根據應用場景的需求。
# 中繼資料 (Metadata)

 - 中繼資料內容存放的是 PI 資訊，經常使用在傳遞 PI 資訊
 - 它會被做為端對端資料保護的傳輸的格式，並且分為兩種 : 
	 - DIF :  中繼資料與使用者資料（LBA Data）連續存放![[metadata_contiguous.png]]
	
	- DIX : 中繼資料與使用者資料個別單獨存放![[medata_as_separate.png]]

# 端對端資料保護 (Protection Information)
 
- PI 資料格式（Protection Information Format）
	- **Guard Field**
	    - 基於邏輯區塊資料計算得出的 `CRC` 校驗資訊。
	- **Application Tag**
	    - 由主機端應用指定，無需 `NVM` 控製器處理。
	- **Reference Tag**
	    - 應用在寫入 `邏輯區塊資料` 與 `邏輯位址` 相關聯，例如：寫入資料的邏輯位址是 `0x1234`
	      則 nvm write 參數所設定的欄位 (Reference Tag) 就會存放寫入的邏輯位址 `0x1234`。
	    - 防止資料被誤用或傳輸亂序情況發生。

- 根據規範 PI 在中繼資料的位置
	- PI 位於 Metadata 開頭 （First of Metadata）
	- PI 位於 Metadata 結尾 （Last of Metadata）

根據上述 PI 在中繼資料的位置，對於資料保護的範圍會有所不同，也就是計算校驗資訊 （CRC）
- 若是 PI 位於 Metadata 開頭
	- Medata == PI，則校驗資訊只需要計算 （邏輯區塊資料）即可。
- 若是 PI 位於 Metadata 結尾
	- Medata > PI，則校驗資訊則是需要計算 （邏輯區塊資料 + 元資料） 但是不包含 PI 資訊。  

另外，端到端資料保護中有不同的 TYPE 1 / 2 / 3，在進行LBA格式化設定就需要指定哪一種類型，代表了不同的 Reference Tag 設定和 PI 檢查方式，如下說明 : 

- TYPE 1： 
	- Reference Tag 隨著LBA增加遞增
	-  Host 必須保證 ILBRT 和 ELBRT 與 LBA 的最後4個Bytes相等。 
- TYPE 2：
	- Reference Tag 隨著LBA增加遞增
	- SSD 檢查 PI 的方式與 TYPE 1 相同，允許 Host 指定任意 ILBRT 和 ELBRT。 
- TYPE 3：
	- Reference Tag 保持不變，SSD 不會檢查 ILBRT 和 ELBRT。 
# 如何使用端對端資料保護功能

首先列出當前所控制器支援 `Metadata Size` 以及 `Data Size`，可以看到支援許多 `LBA Format`，因此我們可以針對控制器所支援的 LBA 格式設定。

```
$ nvme id-ns /dev/nvme0n1 -H
LBA Format  0 : Metadata Size: 0   bytes - Data Size: 512 bytes - Relative Performance: 0 Best 
LBA Format  1 : Metadata Size: 8   bytes - Data Size: 512 bytes - Relative Performance: 0 Best (in use)
LBA Format  2 : Metadata Size: 0   bytes - Data Size: 4096 bytes - Relative Performance: 0 Best 
LBA Format  3 : Metadata Size: 8   bytes - Data Size: 4096 bytes - Relative Performance: 0 Best 
LBA Format  4 : Metadata Size: 64  bytes - Data Size: 4096 bytes - Relative Performance: 0 Best
```

這裡範例設定 Sector Size = 512B + 8B（8B為 PI 資訊大小），並且將 8 位元組大小的 PI 資訊放在中繼資料的開頭，然後採用 `DIF` 標準將中繼資料位於 LBA 的結尾。

```
-l（LBA Format 格式）
-i（Protection Info Type ：off/1/2/3）
-p（PI在中繼資料中的位置 ：last/off）
-m（DIX/DIF）

$ nvme format /dev/nvme0n1 -n 1 -l 1 -i 1 -m 1 -p 1 
```

## 如何建立 PI 資訊並且寫入到 NAND

- 建立 PI 資訊的方法有兩種
	- 主機端建立 PI 資訊，連同（LBA 資料 + 中繼資料） 傳遞給控制器。
	- 控制器收到主機端 LBA 資料，然後由控制器建立 PI 資訊。
	- 以上都需要透過`PRACT` 設定。

## 如何從控制器讀取 LBA 資料或是 PI 資訊

```
dd if=/dev/urandom of=512B.bin bs=512 count=1
```

- PRACT（PI資訊產生的機制）
  - Bit3=1 (控制器生成PI並將其寫入NAND)
  - Bit3=0 (控制器取得上層應用下發的PI訊息，將檢查PI資訊並寫入NAND)

- PRCHK（控制器收到包時檢查的PI資訊）
  - Bit2=1，控制器收到packet時，檢查 CRC
  - Bit1=1，控制器在收到packet時，檢查 App Tag
  - Bit0=1，控制器在收到packet時，檢查 Reference Tagca

```
$ nvme write /dev/nvme0n1 -s 0x12 -z 512 -d 512B.bin --prinfo=0xf --ref-tag=0x12
```

- PRACT（讀取資料時控制器是否回傳PI資訊）
  - Bit3=1 (控制器不向 host 傳回 PI 資訊；只回傳 data block)
  - Bit3=0 (控制器檢查 PI 資訊, 向 host 傳回 PI 資訊以及 data block)
    
- PRCHK（控制器收到包時檢查的PI資訊）
  - Bit2=1，控制器收到packet時，檢查 CRC
  - Bit1=1，控制器在收到packet時，檢查 App Tag
  - Bit0=1，控制器在收到packet時，檢查 Reference Tagca

PI = 8 Bytes
Logic Block Data = 512 Bytes
Data = (Logic Block Data) + (PI) = 512 + 8 = 520

```
$ nvme read /dev/nvme0n1 -s 0x12 -z 520 -d data_read_520B.bin --prinfo=0x7 --ref-tag=0x12
```

// TODO

```
$ xxd -l 520 read_data_with_pi.bin
00000000: 050e 3304 6ba0 fdd2 4914 6ca9 d871 c843  ..3.k...I.l..q.C
00000010: 15cd 4af1 b7be 14a3 124a c58c 8129 1799  ..J......J...)..
...
000001e0: 231d 00a9 3802 f120 ccb7 a9e0 3ee3 f9ad  #...8.. ....>...
000001f0: 5ef3 7c75 7308 4acf cfc8 b1d3 925c c81e  ^.|us.J......\..
00000200: 3593 0000 0000 0012                      5.......
```

$ nvme write /dev/nvme0n1 -s 0x12 -z 520 -y 8 -d data_with_pi.bin --prinfo=0x7 --ref-tag=0x12

=================================================
     
nlbaf   : 4
flbas   : 0x11
  [6:5] : 0	Most significant 2 bits of Current LBA Format Selected
  [4:4] : 0x1	Metadata Transferred at End of Data LBA
  [3:0] : 0x1	Least significant 4 bits of Current LBA Format Selected


mc      : 0x3
  [1:1] : 0x1	Metadata Pointer Supported
  [0:0] : 0x1	Metadata as Part of Extended Data LBA Supported


dpc     : 0x1b
  [4:4] : 0x1	Protection Information Transferred as Last Bytes of Metadata Supported
  [3:3] : 0x1	Protection Information Transferred as First Bytes of Metadata Supported
  [2:2] : 0	Protection Information Type 3 Not Supported
  [1:1] : 0x1	Protection Information Type 2 Supported
  [0:0] : 0x1	Protection Information Type 1 Supported


dps     : 0x9
  [3:3] : 0x1	Protection Information is Transferred as First Bytes of Metadata
  [2:0] : 0x1	Protection Information Type 1 Enabled


```
LBA Format  0 : Metadata Size: 0   bytes - Data Size: 512 bytes - Relative Performance: 0 Best 
LBA Format  1 : Metadata Size: 8   bytes - Data Size: 512 bytes - Relative Performance: 0 Best (in use)
LBA Format  2 : Metadata Size: 0   bytes - Data Size: 4096 bytes - Relative Performance: 0 Best 
LBA Format  3 : Metadata Size: 8   bytes - Data Size: 4096 bytes - Relative Performance: 0 Best 
LBA Format  4 : Metadata Size: 64  bytes - Data Size: 4096 bytes - Relative Performance: 0 Best 
```

================================================

# PI first byte of Metadata

LBA Format = 4k
Metadata Size = 64Bytes
PI = 8Bytes (f15f 0000 0000 0012)

```
00000000: 8338 2be5 4476 9f4b c7d6 0f94 cec5 2348  .8+.Dv.K......#H
00000010: 681c 48b2 576e e137 8b97 d0ed 6e9c 3927  h.H.Wn.7....n.9'
...
00001000: f15f 0000 0000 0012 c3e2 00f0 f3ee 00f0  ._..............
00001010: f3ee 00f0 54ff 00f0 3632 00f0 de31 00f0  ....T...62...1..
00001020: a5fe 00f0 87e9 00f0 f3ee 00f0 f3ee 00f0  ................
00001030: f3ee 00f0 f3ee 00f0 57ef 00f0 53ff 00f0  ........W...S...
```

# PI last byte of Metadata

LBA Format = 4k
Metadata Size = 64Bytes
Fist PI = 8Bytes (f15f 0000 0000 0012)
Last PI = 8Bytes (1bb7 0000 0000 0012)

```
00000000: 8338 2be5 4476 9f4b c7d6 0f94 cec5 2348  .8+.Dv.K......#H
00000010: 681c 48b2 576e e137 8b97 d0ed 6e9c 3927  h.H.Wn.7....n.9'
...
00001000: f15f 0000 0000 0012 c3e2 00f0 f3ee 00f0  ._..............
00001010: f3ee 00f0 54ff 00f0 3632 00f0 de31 00f0  ....T...62...1..
00001020: a5fe 00f0 87e9 00f0 f3ee 00f0 f3ee 00f0  ................
00001030: f3ee 00f0 f3ee 00f0 1bb7 0000 0000 0012  ................
```


