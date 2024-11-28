## **概要說明**

**Host Memory Buffer (HMB)** 是 NVMe 協議引入的一項功能，旨在使用主機的系統內存作為控制器的資料緩存區域（如 Flash Translation Layer，FTL）或用作資料緩存， 當主機或控制器需要訪問頻繁數據時，可以通過 HMB 加快響應速度。
## 運作流程

### 1. 記憶體分配

主機通過 **Set Features 命令 ( Host Memory Buffer )** 開啟 `EHM`，並且配置記憶體容量大小 `HSIZE` 以及記憶體位址 `HMDLLA and HMDLUA`。主機首次配置 HMB，需要將 **Memory Return Bit** 設置為 `0`，表示分配的新記憶體空間。

![[Pasted image 20241129061806.png]]
### 2. 記憶體釋放與回收

當發生重置、關機等事件時，系統會使用 **Set Features 命令 ( Host Memory Buffer )**，關閉 `EHM`通知控制器釋放已分配的記憶體空間，並將其歸還給主機。

## HMB 設定範例

### 1. 檢查是否支援 HMB 

要檢查設備是否支持 **Host Memory Buffer (HMB)**，可以從 **Identify Controller Data Structure** 中取得 **HMPRE**（Host Memory Buffer Preferred Size）屬性。

- **HMPRE = 0**：表示不支援 HMB 功能。
- **HMPRE ≠ 0**：表示支援 HMB，且值表示建議的 HMB 大小（以 4KB 為單位）。

![[Pasted image 20241129064658.png]]

### 2. 開啟與配置 HMB


## HMB 配置分析

### 1. 解釋 HMB 資訊 

使用 Get-Feature ( Host Memory Buffer ) 命令，長度設定為 64 Bytes。

```
$ nvme get-feature -f 0x0d /dev/nvme0 -l 64
get-feature:0x0d (Host Memory Buffer), Current value:0x00000001
       0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
0000: 00 40 00 00 00 70 88 12 01 00 00 00 10 00 00 00 ".@...p.........."
0010: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
0020: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
0030: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
```

可以從 `CQ Entry DW` 得到目前 `HMB` 狀態是否開啟或是關閉，目前 `value=0x01` 代表開啟。

![[Pasted image 20241129070614.png]]

另外我們指定的 64 Bytes 則是 HMB 資料結構 **( Attributes Data Structure )**，此表描述所使用的容量大小以及配置的記憶體位址，最大可以指定 4096 Bytes。

![[Pasted image 20241129071812.png]]

不過 HMB 所使用的數量並不多，因此 64 Bytes 已經可以顯示足夠的資訊。

```
       0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
0000: 00 40 00 00 00 70 88 12 01 00 00 00 10 00 00 00 ".@...p.........."
0010: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
0020: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
0030: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
```

### 2. 使用的記憶體大小

我們要如何計算主機配置的記憶體大小 ?  當前設定 HSIZE = 0x00004000h = 16384

1. 計算容量需要先取得 MPS ( Memory Page Size ) 
2. 目前取得 MPS = ( 2 ^ ( 12 + 0 ) ) = 4096 Bytes
3. Host Memory Buffer Size  =  16384 * 4096 = 64MB

![[Pasted image 20241129073116.png]]

### 3. 配置的記憶體位置

作業系統分配的記憶體位址，分別為一個是高位址 (HMDALU) 一個是低位址 (HMDAL)
 - HMDAL : `0x12887000`
 - HMDALU : `0x00000001`
 - 完整的記憶體位置 : `0x0000000112887000`

![[hmb_cdw13_14.png]]

這個參數是描述 Host 提供給控制器可以使用主機的記憶體範圍，分配支援資源給控制器所使用，因此 Host 不能去修改這些記憶體範圍的內容，除非該記憶體被回收。

- HMDLEC : `0x00000010` 

![[hmb_descriptor_list.png]]
### 3. 開啟與配置 HMB

- 記憶體空間是由系統分配，若是關閉後想要再開啟需要手動設定。  
	- 指定先前系統所配置的位址 `0x0000000112887000`。
	- 由於是配置先前所指派的記憶體空間，`Mmemory Return Bit` 需要設定為 `1`。

**注意 : 記憶體是系統分配的，不能隨意指定一個記憶體位址。**

![[hmb_cdw11.png]]

```
$ nvme admin-passthru --opcode=0x09 --cdw10=0x0d --cdw11=0x01 --cdw12=0x00004000 --cdw13=0x12887000 --cdw14=0x00000001 --cdw15=0x10 /dev/nvme0

Admin Command Set Features is Success and result: 0x00000000
```
### 4. 關閉 HMB 功能

一旦取消 HMB，控制器無法再使用 `Host Memory Buffer` 任何資料，直到再一次的 Enable。

```
$ nvme set-feature -f 0x0d --value=0x00 /dev/nvme0
set-feature:0x0d (Host Memory Buffer), value:00000000, cdw12:00000000, save:0
```


## **HMB 的清除與回收**

1. **進入休眠  ( D3 Cold )** 
    - 系統進入休眠時，HMB 的記憶體空間無法保留，控制器失去對該記憶體的使用權限。
    - 主機需要回收該記憶體，釋放系統資源。
2. **系統恢復 ( Recovery from D3 Cold )**
    - 當系統從休眠狀態恢復時，應重新分配與先前相同的記憶體位址，提供控制器恢復使用。
    - 透過 Set-Feature 命令，將 **Memory Return Bit** 設置為 `1`，表示主機為控制器分配了先前使用的記憶體區域。
記憶體區域由控制器完全管理，系統無法直接修改或操作記憶體內容。