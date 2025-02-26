## **概要說明**

**Host Memory Buffer (HMB)** 是 NVMe 協議引入的一項功能，旨在使用主機的系統內存作為控制器的資料緩存區域（如 Flash Translation Layer，FTL）或用作資料緩存， 當主機或控制器需要訪問頻繁資料時，可以通過 HMB 加快響應速度。
## HMB 運作說明

1.  **記憶體管理與控制**
	- HMB 是由主機記憶體分配給 NVMe 控制器使用的緩存區域。
    - 主機僅提供記憶體空間，不干涉控制器對 HMB 的管理和使用。
    - 主機無法直接讀取或修改 HMB 的數據內容。

2. **記憶體分配規則**
    - 記憶體由主機動態分配，通常由驅動程序進行管理，不能隨意指定一個具體的記憶體位址。
    - 配置的記憶體範圍會是以連續以及多組範圍，提供給控制器使用。
    - 主機需確保分配的記憶體符合 NVMe 規範，並對齊到頁（通常為 4KB）。

3. **記憶體釋放與回收**
	-  **進入休眠  ( D3 Cold )** 
	    - 系統進入休眠時，控制器失去對 HMB 的訪問權限，記憶體內容不再有效。
	    - 主機需要回收該記憶體，釋放系統資源。
	- **系統恢復 ( Recovery from D3 Cold )**
	    - 系統從休眠狀態恢復時，應重新分配與先前相同的記憶體位址，提供控制器使用。
	    - 重新分配時，設置 **MR=1**，表示通知控制器這是針對先前分配的記憶體的恢復。
## HMB 設定範例

### 1. 檢查是否支援 HMB 

要檢查設備是否支持 **Host Memory Buffer (HMB)**，可以從 **Identify Controller Data Structure** 中取得 **HMPRE**（Host Memory Buffer Preferred Size）屬性。

- `HMPRE=0`：表示不支援 HMB 功能。
- `HMPRE≠0`：表示支援 HMB，且值表示要求 HMB 大小（以 4KB 為單位）。

![[Pasted image 20241129064658.png]]
### 2. 開啟與配置 HMB

設定參數 `opcde=0x09`，對應使用 **Set-Feature 命令** 執行。
設定參數 `cdw10=0x0d`，指定的 FID 對應於 **Host Memory Buffer**。

```bash
$ nvme admin-passthru --opcode=0x09 --cdw10=0x0d --cdw11=0x01 --cdw12=0x00001000 \
--cdw13=0x144CF000 --cdw14=0x00000001 --cdw15=0x00000004 /dev/nvme0
Admin Command Set Features is Success and result: 0x00000000
```

設定參數 `cdw11=0x000000001`，開啟 **Host Memory Buffer**。

![[Pasted image 20241129090536.png]]

另外一個要注意的是 **Memory Return Bit**，如下說明 : 

- `MR=0`：初始分配記憶體時，**表示主機首次配置 HMB**，記憶體內存空間不依賴之前的配置。這種情況通常在設備第一次上電或初始化時發生。

- `MR=1`：經歷過 `D3 State`（如進入休眠）或 `Reset` 後，主機會重新分配記憶體給控制器，此時會將 MR 設定為 `1`，表示記憶體應該按照之前的分配情況進行重新配置。

![[Pasted image 20241202025212.png]]

設定參數 `cdw12=0x00001000`，配置的記憶體容量 **16M Bytes**。

計算公式 : 4096 *  MPS ( 4096 ) = 16777216 = 16M Bytes

![[Pasted image 20241129090809.png]]

設定參數 `cdw13=0x144CF000`，`cdw14=0x00000001`，主要用來告知控制器讀取該位址內容，取得主機配置的記憶體容量與使用範圍，也就是 **Host Memory Buffer Descriptor List Address**。

什麼是  **Host Memory Buffer Descriptor Entry** ? 它是用來描述主機記憶體位址以及使用的容量大小。主機開始配置 HMB 並不會給予一段非常大的記憶體範圍，而是會配置多個一小段的記憶體範圍給控制器使用。

![[Pasted image 20241129081433.png]]

設定參數 `cdw15=0x00000004` 表示在 **Host Memory Buffer (HMB)** 的配置中，分配了 4 段範圍的記憶體地址區域。這些範圍的詳細信息將通過 **Host Memory Buffer Descriptor List (HMDL)** 來描述，每段記憶體對應一組 **Host Memory Buffer Descriptor Entry**。

![[Pasted image 20241129083224.png]]

當控制器收到命令後，就會根據設定發送 `TLP MRd(64)` 讀取該主機告知的記憶體位址，取得所有 **Host Memory Buffer Descriptor Entry**。

![[Pasted image 20241129083631.png]]

- **Host Memory Buffer Descriptor Entry** 它包含兩個關鍵信息：
	1. **Buffer Size** : 連續的記憶體頁數量（單位: MPS）。
	2. **Buffer Address** : 主機記憶體位址（單位: MPS）。
		- MPS=4k ( Bits [11:0] 這些位元需要對齊為 `0` )
		- MPS=8k ( Bits [12:0] 這些位元需要對齊為 `0` )

![[Pasted image 20241129083913.png]]

- **透過 TRACE 追蹤取得主機分配的記憶體內容如下** : 
	- 總共配置 4 段記憶體範圍。
	- 每段記憶體大小為 4MBytes。
	- 每個記憶體都有對齊 4K。
	- 總配置記憶體大小 = 4 Entry * 4M = 16M Bytes

![[Pasted image 20241202022625.png]]

- **如何計算 Buffer Size 容量大小** : 
	- Buffer Size = 1024 ( 0x400h ) * 4096 ( MPS ) = 4MBytes

| Memory Buffer Entry | Buffer Address      | Buffer Size        |
| ------------------- | ------------------- | ------------------ |
| 第一個範圍               | `00000001:14800000` | `0000000000000400` |
| 第二個範圍               | `00000001:14C00000` | `0000000000000400` |
| 第三個範圍               | `00000001:15000000` | `0000000000000400` |
| 第四個範圍               | `00000001:15400000` | `0000000000000400` |
### 3. 關閉 HMB 功能

一旦取消 HMB，控制器無法再使用 `Host Memory Buffer` 任何資料，直到再一次的 Enable。

```
$ nvme set-feature -f 0x0d --value=0x00 /dev/nvme0
set-feature:0x0d (Host Memory Buffer), value:00000000, cdw12:00000000, save:0
```
## HMB 配置分析

### 1. HMB 資訊 

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

另外我們指定的 64 Bytes 則是 HMB 資料結構 **( Attributes Data Structure )**，此表描述所使用的容量大小以及配置的記憶體位址，最大可以指定顯示 4096 Bytes。

![[Pasted image 20241129071812.png]]

不過 HMB 所使用的數量並不多，因此 64 Bytes 已經可以顯示足夠的資訊。

```
       0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
0000: 00 40 00 00 00 70 88 12 01 00 00 00 04 00 00 00 ".@...p.........."
0010: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
0020: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
0030: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
```

### 2. 記憶體大小

我們要如何計算主機配置的記憶體大小 ?  當前設定 HSIZE [ 3:0 ] = `0x00004000h` = `16384`

1. 計算容量需要先取得 MPS ( Memory Page Size ) 
2. 目前取得 MPS = ( 2 ^ ( 12 + 0 ) ) = 4096 Bytes
3. Host Memory Buffer Size  =  16384 * 4096 = 64MB

![[Pasted image 20241129073116.png]]

### 3. 記憶體位置

作業系統分配的記憶體位址，分別為低位址 **HMDAL** 以及高位址 **HMDALU**。

 - HMDAL [ 7: 4 ] : `0x12887000`
 - HMDALU [ 11: 8 ] : `0x00000001`
 - 完整的記憶體位置 : `0x00000001:12887000`

![[Pasted image 20241129081433.png]]

### 4. 記憶體範圍數量

**HMDLEC** 這個參數描述 Host 提供給控制器使用的記憶體範圍數量。

HMDLEC [15:12] = `0x00000004` ( 代表配置 **4** 段記憶體範圍 )

![[Pasted image 20241129083224.png]]