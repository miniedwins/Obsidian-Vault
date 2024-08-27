# Dataset Management



## DSM 介紹

**Dataset Management (DSM) :** 由主機來設定參數以及執行 `dsm` 命令，可以改善效能與穩定性，以及對邏輯區塊 (logic block) 執行像是 `TRIM` 的行為，但並不代表 DSM 它只能執行 `TRIM` 功能 (重要)。它有一個 `Range Definition` 結構表定義如何執行，最大可以支援 Range 0-255 (256*16 = 4096 Bytes)，每個 Range 的組成包含 Starting LBA, Length in logical blocks, Context Attributes。主機可以透過 dsm 命令，指定每個 Range Field Attributes，而控制器會根據該 Range 所指定的內容去執行 (重要)。

例如 : 主機若是要執行 `TRIM` 功能，主機發送 dsm 命令就會設定 `Attribute Deallocate (AD)` 以及將 Range Definition Data 傳給控制器，當控制器執行完畢後，那些指定的 block range 就會變成 `deallocate` or `unwritten logical block`。

**DSM 可以設定的功能有 AD, IDW, IDR**

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/nvm_command_set/dataset_management_dw11.png)

**Range Definition : 指定開始的邏輯區塊位置與長度，還有屬性 (Context Attributes)**

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/dataset_management_range_definition.png)

## 相關名詞解釋

### Deallocate

該定義代表一個邏輯區塊的狀態，如下所述 : 

* 從未被寫過的邏輯區塊 (unwritten logical lock)，對主機而言就是一個乾淨的邏輯區塊
* 該邏輯區塊 (logical block) 已經有執行過 dsm with deallocated 
* (原文) Write Zeroes Command or Sanitize command is called deallocated or unwritten logical block
  * (說明) 執行上述這兩個命令，基本上可以稱為 deallocated or unwritten logical block

> 備註 : The operation of the Deallocate function is similar to the ATA DATA SET MANAGEMENT with Trim feature

### Error Recovery

(原文) The controller shall fail Read, Verify, or Compare commands that include deallocated or unwritten blocks with a status of Deallocated or Unwritten Logical Block if that error has been enabled using the DULBE bit in the Error Recovery feature.

(說明) 待續 ...

*備註 : Legacy software may not handle an error for this case.*

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/feature/error_recovery_id_05.png)

###  DULBE

* (原文翻譯) 當主機讀取 deallocated or unwritten block，控制器根據 Deallocate Logical Block Features (Bits 2:0) 設定，當讀取到 deallocated or unwritten block，控制器應該需要回傳那一種數值，這個設定可以由 Identify Namesapce Data Structure 取得。
* (說明) 主要是說若是主機去讀取一個 deallocated or unwritten block，控制器會根據 DLFEAT 設定，然後回傳一個固定的值

回覆下列其中一種數值 : 

* `000b` : Not Reported
* `001b` : 0x00h
* `010b` : 0xFFh

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/identify_namesapce/Identify_Namespace_DLFEAT.png)



## 如何執行命令

### 檢查控制器是否支援

說明 : 檢查控制器有沒有支援 **Dataset Management** 命令，若是沒有支援，就會沒有辦法執行像是 **Trim** 功能

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/identify_controller/Identify_Controller_ONCS_Bit2.png)

執行命令 : 

~~~shell
nvme id-ctrl /dev/nvme0 | grep oncs
# oncs: 0x1e
~~~



### 確認是否支援 Deallocate

說明 : 檢查控制器有沒有支援 Deallocated or Unwritten Logical Block error for this namespace

取得方法 : 

* 查看 Namesapce Data Structure，並檢查 DLFEAT 該屬性
* nvme-cli 並沒有把 `DLFEAT` 顯示出來，因此需要發送 `admin-passthru` 命令取得 `Raw Data`
* 長度可以設定 512 bytes 即可，目的只是要確認 `Bits 2:0`

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/identify_namesapce/Identify_Namespace_NSFEAT.png)

執行命令 : 

~~~shell
nvme admin-passthru /dev/nvme0 --namespace-id=1 --opcode=0x06 --cdw10=0x00 --data-len=512 --read
~~~

執行結果 : 

~~~shell
NVMe command result:00000000
       0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
0000: b0 44 f2 1b 00 00 00 00 b0 44 f2 1b 00 00 00 00 ".D.......D......"
0010: b0 44 f2 1b 00 00 00 00 00 01 00 00 00 00 00 00 ".D.............."
0020: 00 00 ff 00 00 00 00 00 ff 00 00 00 00 00 00 00 "................"
~~~



### 檢查啟用或停用 DUBLE 

說明 : 檢查目前的控制器是否有啟用或是停用 **DUBLE**

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/feature/error_recovery_id_05.png)

~~~shell
nvme get-feature --feature-id=0x05 /dev/nvme0n1 
# get-feature:0x5 (Error Recovery), Current value:00000000
~~~



### 如何執行 TRIM 功能

可以透過下列兩種方式執行 : 

* nvme-cli dsm
* nvme-cli io-passthru



#### nvme-cli dsm

首先使用 `DD` 命令寫入資料 4096 Bytes

~~~shell
sudo dd if=/dev/urandom of=/dev/nvme0n1 bs=4096 count=1
~~~

執行 `hdexdump` 命令來確認資料有寫入

~~~shell
sudo hexdump -C -n 4096 /dev/nvme0n1
00000000  07 67 8c 23 d4 8f f1 7d  6b 16 35 c8 d8 52 60 55  |.g.#...}k.5..R`U|
00000010  f4 f8 cd 66 21 37 27 c0  bc 10 6c 2a 41 21 fa 91  |...f!7'...l*A!..|
00000020  f2 06 10 fb d9 1c 20 5e  9d 8a 6c b5 0b 9d 23 d0  |...... ^..l...#.|
00000030  f2 16 3c 20 59 bc ce c2  a7 bf c6 e6 0b bd 8f ca  |..< Y...........|
00000040  66 d6 6d e9 89 45 bc ca  d1 67 a4 54 c9 c5 31 a3  |f.m..E...g.T..1.|
00000050  9a 6f a8 53 63 cc 3b 50  d0 b5 02 3b 93 38 1f ad  |.o.Sc.;P...;.8..|
00000060  ff d5 68 4d e0 3d 93 1f  17 9e 80 06 d6 38 56 17  |..hM.=.......8V.|
00000070  d8 12 6b 64 88 6c 0e fd  98 8a 3a 69 80 81 5b 80  |..kd.l....:i..[.|
00000080  72 74 51 43 69 d0 15 0a  00 3e 0b 88 76 c5 d1 0f  |rtQCi....>..v...|
00000090  27 a3 23 49 2d 6e 2d a8  95 cc fc ca 4c de b7 71  |'.#I-n-.....L..q|
000000a0  51 17 e9 0f 9b ed 82 f2  ce 00 4b 39 ce 13 ac de  |Q.........K9....|
000000b0  5a 9f 56 3f a1 36 47 4e  86 7d b5 88 36 bf db 6b  |Z.V?.6GN.}..6..k|
000000c0  80 df 5b 28 2d 3e c7 d9  fe dd d9 fa 08 32 b3 ee  |..[(->.......2..|
000000d0  8c 5d ae f9 1f c1 07 7f  8d 92 6c f9 93 1b ff 03  |.]........l.....|
000000e0  36 f8 91 3d ff e4 81 05  8c c6 ba 3c 4c 71 b7 c6  |6..=.......<Lq..|
000000f0  96 9f f7 30 8e 56 e9 e3  ef 41 25 3e 3b 00 f2 72  |...0.V...A%>;..r|
00000100  e2 fd 5a 82 a1 bb 3c 21  af 80 ab bc d0 a3 36 c4  |..Z...<!......6.|
00000110  7f f8 2d 04 eb 21 ca c9  64 8c 2e 6c 31 28 1e 48  |..-..!..d..l1(.H|
00000120  bc 5c b0 52 53 5a df 17  fa de 24 c6 6a 9f 5b 2f  |.\.RSZ....$.j.[/|
00000130  56 48 4e df ce 5c 70 b1  ce 85 2f 96 f1 a9 50 9d  |VHN..\p.../...P.|
00000140  26 44 64 1e f5 66 c2 18  b8 17 4c 48 e1 e2 5a e7  |&Dd..f....LH..Z.|
00000150  82 71 69 fe 5f 02 73 31  f4 4d 2f 4c 8d 5a bf 3e  |.qi._.s1.M/L.Z.>|
00000160  15 9b 4d 2a df b3 0a 33  40 ff f2 c4 34 fc 43 f7  |..M*...3@...4.C.|
00000170  bb e4 2d f1 ba 1e 44 fe  b1 64 ce 8f 6c 52 66 26  |..-...D..d..lRf&|
00000180  cc ed d8 4f e6 bb a0 37  c1 44 a3 4b 91 21 69 6d  |...O...7.D.K.!im|
00000190  64 af 6b 31 97 ea 48 e1  78 b8 e0 b7 d9 71 8a cf  |d.k1..H.x....q..|
000001a0  48 f9 7c 7c b8 d5 2e c3  ca bb af de 13 4d c2 72  |H.||.........M.r|
000001b0  e2 94 44 97 18 5f 43 e0  d9 bf 11 b8 1c dc 0a 6f  |..D.._C........o|
000001c0  d2 55 7f 4b 04 2c a4 bf  cf d3 18 8d 19 22 d0 64  |.U.K.,.......".d|
000001d0  43 c7 2f b1 ca fc e1 ea  a2 8a b4 35 58 56 b5 6e  |C./........5XV.n|
000001e0  8e 1d 4a b5 83 55 14 63  02 c4 74 6a 73 96 7c ba  |..J..U.c..tjs.|.|
000001f0  db c6 29 e7 76 ec 7a 32  e8 fc 9a 5b 98 f9 e6 b5  |..).v.z2...[....|
..........
00000ff0  e4 e1 07 72 0a 77 c8 35  5b 2d 9f fc dc 57 ea c9  |...r.w.5[-...W..|
~~~

執行命令 nvme-cli dsm

~~~shell
# Starting LBA = 0
# Trim Blocks = 4
# cdw11 = Attribute Deallocate (0x04)
sudo nvme dsm --namespace-id=1 --slbs=0 --blocks=4 --cdw11=0x04 /dev/nvme0n1
NVMe DSM: success
~~~

執行 `hdexdump` 命令來檢查資料是否被清除

~~~shell
sudo hexdump -C -n 4096 /dev/nvme0n1
~~~

執行結果 : 

* 執行命令完成後，該區段的值就會變成 0x00h (00000000-000007ff)
* 總共被清除的資料 : 2048 Bytes (4 Blocks = 4 * 512)

~~~shell
00000000  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
00000800  fe 19 3b a0 1c fe 84 f3  f0 6b 2f f3 cc 5c 21 d5  |..;......k/..\!.|
00000810  23 53 4e 22 aa 65 8c ea  c8 c9 4a 82 2d 30 06 a9  |#SN".e....J.-0..|
00000820  25 ac 64 46 c0 eb a6 c2  5a ad 5a f6 e3 cb 37 44  |%.dF....Z.Z...7D|
00000830  4d d2 c1 8c a7 5b cc 69  a2 16 35 48 af 98 9b dc  |M....[.i..5H....|
00000840  99 7b 6a 06 4a 0a 23 3b  b8 00 f9 50 e7 bf 44 bf  |.{j.J.#;...P..D.|
00000850  da 27 e3 77 9a 7c 1e ca  fc 45 09 1f 4f fe 00 9d  |.'.w.|...E..O...|
00000860  59 89 93 f4 aa 3d a5 19  02 62 76 77 c6 1f 24 93  |Y....=...bvw..$.|
00000870  32 b1 ce ca 27 e0 6b d6  ab 6b ab b8 83 e2 80 be  |2...'.k..k......|
00000880  72 5b 66 64 0a f6 77 32  29 ed 6d 17 60 10 ef c7  |r[fd..w2).m.`...|
00000890  dd 2f f5 c6 8d 71 34 e1  e3 82 69 83 68 ca 33 b8  |./...q4...i.h.3.|
000008a0  91 6e 53 20 e3 7e e7 4a  29 0b 97 89 3c 4f 1c 76  |.nS .~.J)...<O.v|
000008b0  56 07 83 da f7 77 d9 c7  6b e8 c0 4a 9c e9 78 76  |V....w..k..J..xv|
000008c0  94 42 47 b5 91 27 c8 60  8a 31 34 45 08 f2 83 b0  |.BG..'.`.14E....|
000008d0  dc 83 6a 27 a4 9a 64 a5  a7 0d fe 9e 44 c6 f9 21  |..j'..d.....D..!|
000008e0  a0 28 d6 97 fe 28 0c bc  17 c2 23 49 19 64 65 b6  |.(...(....#I.de.|
000008f0  46 ef f3 53 c1 3d 4c ca  3f f7 80 07 b5 5f 97 89  |F..S.=L.?...._..|
..........
00000ff0  e4 e1 07 72 0a 77 c8 35  5b 2d 9f fc dc 57 ea c9  |...r.w.5[-...W..|
~~~



#### nvme-cli io-passthru

首先使用 fio 寫入資料，szie = 1GBytes，pattern = 0x12345678

~~~shell
sudo fio --thread --direct=1 --allow_file_creat=0 --ioengine=libaio --rw=write --bs=128k --iodepth=128 --numjobs=1 --name=nvme0n1 --filename=/dev/nvme0n1 --size=1g --verify=pattern --do_verify=0 --verify_pattern=0x12345678
~~~

根據 Range Definition 結構內容，使用 python 建立一個  trim.bin 檔案

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/dataset_management_range_definition.png)

**Sample Code**

~~~python
import array

# 根據 Range Definition 建立一個 4096 buffer size
buf = array.array("B",[0x00] * 4096)

# 根據偏移量的遞增，然後每次取資料的最低位元，寫入到 buffer size
def set_value(buf, offset, num, value):
    if num == 1:
        buf[offset] = value
    else:
        # Example: logical blocks
        # 0x00200000h = 2097152 Blocks 
        # buf[4 + 0] = 0x00
        # buf[4 + 1] = 0x00
        # buf[4 + 2] = 0x20
        # buf[4 + 3] = 0x00
        for i in xrange(num): 
            new_value = (value >> (8 * i)) & 0xff
            buf[offset+i] = new_value
    return buf

def write_file(buf, filepath):
    with open(filepath, "wb") as f:
        buf.tofile(f)

"""
+-----------------------+
offset : 從哪個偏移量開始
num : 偏移的次數	 
value : 多少個邏輯區塊
+-----------------------+
"""
        
# Length in logical blocks：offset=4 num=4 value=2097152 (Blocks)
buf = set_value(buf,4,4, 2097152)

# Staring LBA : offset=8 num=8 value=0 (Blocks)
buf = set_value(buf,8,8, 0)

write_file(buf, “trim.bin”)
~~~

查看 trim.bin 的結構內容，必須要符合 Range Definition Field，目前裡面的內容只有 `Range0`

* Context Attributes (03:00) : 0x00
* Length in logical blocks (07:04) : 0x00200000h = 2097152 Blocks = 1,073,741,824 Bytes = 1GB
* Starting LBA (15:08) : 0x00

~~~shell
edwin@edwin:~$ sudo hexdump -C -n 512 trim.bin 
00000000  00 00 00 00 00 00 20 00  00 00 00 00 00 00 00 00  |...... .........|
00000010  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
00000200
~~~

發送 nvme io-passthru，將剛剛產生的資料 `trim.bin` (Range Definition) 傳送給控制器，所以必須要帶 `--write` 命令

~~~shell
sudo nvme io-passthru /dev/nvme0 --opcode=0x09 --namespace-id=1 --cdw10=0x00 --cdw11=0x04 --input-file=trim.bin --data-len=4096 --write
~~~

然後再使用 fio 確認剛剛寫入的邏輯區塊是否被清除為 `0x00h`，如果不成功 fio 會報資料驗證的錯誤訊息

寫入的資料的開始位置是 LBA=0，所以 fio 不需要帶參數 `--offset` 去調整從哪個位置開始

~~~shell
sudo fio --thread --direct=1 --allow_file_creat=0 --ioengine=libaio --rw=read --bs=128k --iodepth=128 --numjobs=1 --name=nvme0n1 --filename=/dev/nvme0n1 --size=1g --verify=pattern --do_verify=1 --verify_pattern=0x00
~~~



