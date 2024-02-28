## 取得 HMB 資訊 

nvme-cli 執行後顯示兩個資訊內容，如下 :
- Completion Queue Entry Dword 0
- Attributes Data Structure

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

可以從 `CQ Entry` 得到目前 HMB 是否開啟或是關閉，顯示的 `Current value:0x01`，代表 Enable。

![[nvme_hmb_cq_entry_dword0.png]]

Attributes Data Structure



## 開啟 HMB

經過休眠或是 `D3Hot` 等行為，則是需要重新通知控制器使用剛剛所使用的  `Memory Address`，這個時候的記憶位置的內容並不會是 `Undefined Content`。 

```
$ nvme admin-passthru --opcode=0x09 --cdw10=0x0d --cdw11=0x01 --cdw12=0x00004000 --cdw13=0x12887000 --cdw14=0x00000001 --cdw15=0x10 /dev/nvme0
Admin Command Set Features is Success and result: 0x00000000
```

## 取消 HMB

```
$ nvme set-feature -f 0x0d --value=0x00 /dev/nvme0
set-feature:0x0d (Host Memory Buffer), value:00000000, cdw12:00000000, save:0
```


