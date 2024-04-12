# 端對端資料保護

## 內容說明

端到端資料保護將資料的完整性保護範圍從SSD內部延伸到外部鏈路，以防止靜默錯誤產生——通過對邏輯塊資料（Logical Block Data，通常指使用者資料）新增額外的PI（Protection Information，保護資訊，如CRC），使其作為資料的中繼資料 (Metadata) 被一同傳輸，主機端和NVM控製器都可以在接收到資料後，根據PI的內容對資料完整性進行校驗，以確定這些資料是否真的可用。

端到端資料保護的關鍵就在於 PI（Protection Information）作為中繼資料時的傳輸與校驗，中繼資料有DIF和DIX兩種方式，經過T10組織的相關工作已經實現了標準化。簡單來說，DIF即中繼資料與使用者資料（LBA Data）連續存放；而 DIX格式則是中繼資料與使用者資料單獨存放；可以根據應用場景的需求。
## 中繼資料 (Metadata)

- 中繼資料內容存放的是 PI 資訊，經常使用在傳遞 PI 資訊。
- 它會被做為端對端資料保護的傳輸的格式，並且分為 DIF & DIX。

DIF :  中繼資料與使用者資料（LBA Data）連續存放
![[metadata_contiguous.png]]

DIX : 中繼資料與使用者資料個別單獨存放
![[medata_as_separate.png]]

## PI 資訊（Protection Information）
 
下列內容是參考 SPEC 1.4.C ，NVMe 2.x 有更進一步加強端對端資料保護功能。
### PI 內容結構

 - Guard Field
	 - 基於邏輯區塊資料計算得出的 `CRC` 校驗資訊。
- Application Tag
	- 由主機端應用指定，無需 `NVM` 控製器處理。
- Reference Tag
	- 應用在寫入 `邏輯區塊資料` 與 `邏輯位址` 相關聯，例如：寫入資料的邏輯位址是 `0x1234`	      則 nvm write 參數所設定的欄位 (Reference Tag) 就會存放寫入的邏輯位址 `0x1234`。
	- 防止資料被誤用或傳輸亂序情況發生。
### PI 存放中繼資料的位置

- PI 位於 Metadata 開頭 （First of Metadata）
- PI 位於 Metadata 結尾 （Last of Metadata）

根據上述 PI 在中繼資料的位置，對於資料保護的範圍會有所不同，也就是計算校驗資訊（CRC）
- 若是 PI 位於 Metadata 開頭
	- Medata == PI，則校驗資訊只需要計算（邏輯區塊資料）即可。
- 若是 PI 位於 Metadata 結尾
	- Medata > PI，則校驗資訊則是需要計算（邏輯區塊資料 + 元資料）但是不包含 PI 資訊。  

### PI 類型 (檢查方式)

另外，端到端資料保護中有不同的 TYPE 1 / 2 / 3，在進行LBA格式化設定就需要指定哪一種類型，代表了不同的 Reference Tag 設定和 PI 檢查方式，如下說明 : 

- TYPE 1： 
	- Reference Tag 隨著LBA增加遞增
	-  Host 必須保證 ILBRT 和 ELBRT 與 LBA 的最後 4 個Bytes相等。 
- TYPE 2：
	- Reference Tag 隨著LBA增加遞增
	- SSD 檢查 PI 的方式與 TYPE 1 相同，允許 Host 指定任意 ILBRT 和 ELBRT。 
- TYPE 3：
	- Reference Tag 保持不變，SSD 不會檢查 ILBRT 和 ELBRT。 
# 如何使用端對端資料保護功能

- 建立 PI 資訊的方法有兩種
	- (1) 主機端建立PI 資訊，連同（LBA 資料 + 中繼資料）傳遞給控制器。
	- (2) 控制器收到主機端 LBA 資料，然後由控制器建立 PI 資訊。
	- 以上都需要透過`PRACT` 設定。
## 啟用端對端資料保護

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
-p（PI在中繼資料中的位置 ：last/first）
-m（DIX/DIF）

$ nvme format /dev/nvme0n1 -n 1 -l 1 -i 1 -m 1 -p 0 -f
```
## 端對端資料保護範例

### (1) MD 8B + PI 8B

#### 控制器收到主機寫入請求並且產生 PI 資訊

當主機端發出寫入請求命令，控制器收到命令後會在 `LBA Data` 後面加入 PI 資訊，最後寫入 NAND。

![[nvme_write_pi_md_eq8_pract_1.png]]

首先主機端使用 DD 命令建立寫入的檔案。

```
dd if=/dev/urandom of=512B.bin bs=512 count=1
```

使用 nvm write 命令入到 SSD，還需要設定端對端資料參數 `PRINFO` 以及 `ILBRT`，若是沒有上述這兩個參數設定會造成寫入失敗。

這裡設定寫入的 LBA=0x12，並且 PI 資訊需要透過控制器幫我們產生，因此設定 `PRACT=0`，而 PRCHK
表示是否要檢查 PI 資訊，也可以個別選擇檢查 PI 裡的內容結構，這個範例設定 `PRCHK=111b` 所有內容都檢查。另外 ILBRT 需要設定相同寫入位址 0x12，這個參數代表的就是 PI 結構裡的 `Reference Tag`。

```
$ nvme write /dev/nvme0n1 -s 0x12 -z 512 -d 512B.bin --prinfo=0xf --ref-tag=0x12
```

![[nvm_write_prinfo_field.png]]
#### 控制器收到主機讀取請求

當控制器收到主機端的讀取命令請求，主機端可以設定是否需要回傳 PI 資訊或是回傳 `LBA Data`。在這個範例中我們只要求控制器回傳 LBA 資料即可。

![[nvme_read_pi_md_eq8_pract_1.png]]

使用 nvm read 命令讀取 `LBA=0x12` 位址的資料，ILBRT 指定相同位址 `--ref-tag=0x12`，並且設定 `PRACT=0`，代表控制器只回傳 `LBA Data`，然後設定 `PRCHK=111b` 檢查 PI 所有的資訊內容是否正常。

由於 `PRACT` 設定不需要回傳 PI 資訊，因此讀取檔案大小只需要設定 512 Bytes。

```
$ nvme read /dev/nvme0n1 -s 0x12 -z 512 -d data_read.bin --prinfo=0x7 --ref-tag=0x12
```

接下來透過 `xxd` 命令可以查看控制器回傳後的 LBA 資料。

```
$ xxd -l 512 read_data.bin
00000000: 050e 3304 6ba0 fdd2 4914 6ca9 d871 c843  ..3.k...I.l..q.C
00000010: 15cd 4af1 b7be 14a3 124a c58c 8129 1799  ..J......J...)..
...
000001e0: 231d 00a9 3802 f120 ccb7 a9e0 3ee3 f9ad  #...8.. ....>...
000001f0: 5ef3 7c75 7308 4acf cfc8 b1d3 925c c81e  ^.|us.J......\..
```

若是要控制器回傳 PI 資訊，可以設定 `PRACT=1`，然後相同設定 `PRCHK=111b` 檢查 PI 所有的資訊內容。

由於 `PRACT` 設定需要回傳 PI 資訊，因此讀取檔案大小需要更改成 520 Bytes（512B + 8PI）。

```
$ nvme read /dev/nvme0n1 -s 0x12 -z 520 -d data_read.bin --prinfo=0xf --ref-tag=0x12
```

透過 `xxd` 命令可以查看控制器回傳後的（LBA 資料 + PI 資訊）。

PI 資訊內容 = `3593 0000 0000 0012`

```
$ xxd -l 520 read_data.bin
00000000: 050e 3304 6ba0 fdd2 4914 6ca9 d871 c843  ..3.k...I.l..q.C
00000010: 15cd 4af1 b7be 14a3 124a c58c 8129 1799  ..J......J...)..
...
000001e0: 231d 00a9 3802 f120 ccb7 a9e0 3ee3 f9ad  #...8.. ....>...
000001f0: 5ef3 7c75 7308 4acf cfc8 b1d3 925c c81e  ^.|us.J......\..
00000200: 3593 0000 0000 0012                      5.......
```

### (2) MD 64B + PI 8B

# PI first byte of Metadata

PI = 8Bytes (f15f 0000 0000 0012)

```

```

# PI last byte of Metadata

```
nvme format /dev/nvme0n1 -n 1 -l 4 -i 1 -m 1 -p 0 -f
nvme write /dev/nvme0n1 -s 0x12 -z 4096 -d 4k.bin --prinfo=0xf --ref-tag=0x12
nvme read /dev/nvme0n1 -s 0x12 -z 4160 -d read_4k_64PI.bin --prinfo=0x7 --ref-tag=0x12
```

Last PI = 8Bytes (6300 0000 0000 0012)

```
00000000: 8338 2be5 4476 9f4b c7d6 0f94 cec5 2348  .8+.Dv.K......#H
00000010: 681c 48b2 576e e137 8b97 d0ed 6e9c 3927  h.H.Wn.7....n.9'
00000020: 5415 05eb 7044 954f ff57 44c8 b6c9 0242  T...pD.O.WD....B
...
00001000: f3ee 00f0 f3ee 00f0 c3e2 00f0 f3ee 00f0  ................
00001010: f3ee 00f0 54ff 00f0 3632 00f0 de31 00f0  ....T...62...1..
00001020: a5fe 00f0 87e9 00f0 f3ee 00f0 f3ee 00f0  ................
00001030: f3ee 00f0 f3ee 00f0 6300 0000 0000 0012  ........c.......
```


