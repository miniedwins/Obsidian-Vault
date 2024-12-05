## NVMe 初始化設定

下圖是主機初始化 NVMe 控制器的完整過程，這些步驟是基於 NVMe 規範中的描述。從圖中觀察 Linux 開機行為來看，系統似乎沒有遵循 **Controller Initialization** 順序，但不影響整體觀察。

前期大都是對控制器的暫存器做設定，此時的控制器還未能夠開始處理主機提交的命令，直到控制器的功能設定完畢後，並且暫存器 **CC.EN=1**，才會開始處理 NVMe Admin 命令。

![[Pasted image 20241202071500.png]]

完成控制器初始化後，主機就會開始發送 Identify Controller 命令確認控制器當前狀態，或是使用 Set Feature 命令設定相關功能。

從下圖執行命令來看，系統大致上會做以下動作 :  
- Identify Controller  ( 取得控制器相關支援功能 )
- Commands Supported and Effects ( 確認控制器支援的哪些命令 )
- Autonomous Power State Transition ( 如果有支援，設定 APST=1 )
- SMART / Health Information ( 取得 SMART 日誌 )
- Host Memory Buffer ( 如果有支援，設定 HMB )
- Number of Queues ( 設定多少組 I/O Queues )
- Create I/O Submission and I/O Completion Queues ( 建立 I/O Queues )

備註 : 控制器的功能越多，可能會有更多執行命令產生。

![[Pasted image 20241203091933.png]]
### 1. 等待控制器完成重置

檢查控制器狀態暫存器（CSTS）的 **RDY（Ready）位**，確認其值為 `0`，表示重置完成。
### 2. 設定 Admin Queue 記憶體位址與數量

在 NVMe 中，**Admin Queue** 包括 **Admin Submission Queue ( ASQ )** 和 **Admin Completion Queue ( ACQ )**，用於放置管理命令 ( 提交與完成 )，如 **Identify** 和 **Set Features**。它們的大小（Size）和基址（Base Address）需要主機在控制器初始化階段進行配置。
#### (1) 設定 Admin Queue Size

主機端設定控制器 Admin Queue Size 數量為多少，表示主機可以放置多少提交與完成最大管理命令數量。

![[Pasted image 20241202071855.png]]

從圖中得知可以發現到主機端將 **ASQS** 以及 **ACQS** 設定為 64 ( 0x3F )。

![[Pasted image 20241203063725.png]]
#### (2) 設定 Admin Queue Base Address

主機發出的管理命令與完成的命令都是存放在主機端的記憶體位址，因此主機需要告知控制器 Admin Queue Base 記憶體位址 **ASQ** 以及 **ACQ**。
 
**Admin Submission Queue Base Address** : 表示存放 Admin SQ 命令的記憶體位址。

![[Pasted image 20241202074605.png]]

**Admin Completion Queue Base Address** : 表示存放 Admin CQ 命令的記憶體位址。

![[Pasted image 20241202074835.png]]

從圖中得知可以發現到主機設定，記憶體需要根據 CC.MPS 對齊 ( MPS Default : 4K  )
- **ASQB**  : 0x00000000 : 7168C000
- **ACQB**  : 0x00000000 : 7168B000
- **位元對齊** : 7168C000h - 7168B000 = 1000h = 4096

![[Pasted image 20241203063846.png]]

下圖是一個 NVMe 初始化後的第一道 Admin 命令 ( Set Feature )，可以看到控制器拿取命令的記憶體位址，就是主機端初始化設定的記憶位址 **ASQB 以及 ACQB**。

![[Pasted image 20241202075200.png]]
### 3. 檢查控制器支援命令集與設定 I/O 相關屬性

初始化 NVMe 控制器時，主機需要檢查控制器支持的 I/O 命令集屬性，並配置相關參數。
#### (1) 檢查命令集支持

主機檢查 **CAP.CSS**（Command Set Support）欄位，根據以下條件設置 **CC.CSS**（Command Set Selected）：

注意 : 需要搭配 **CAP.CSS** 以及 **CC.CSS** 這兩組設定才能確認支援 NVM Command Set。

- **CAP.CSS.NOIOCSS = 1**：
	- 設置 **CC.CSS = 111b**（無 I/O 命令集支持）。
- **CAP.CSS.IOCSS = 1**：
	- 設置 **CC.CSS = 110b**（支持多個 I/O 命令集，例如 : Zoned Namespace Cmd Set）。
- **CAP.CSS.NCSS = 1  and CAP.CSS.IOCSS = 0**：
	- 設置 **CC.CSS = 000b**（支持 NVM 命令集）。

![[Pasted image 20241202081215.png]]

這裡要注意一下，若是 **CC.CSS = 111b**，代表控制器僅支援 **Admin Command Set**。

![[Pasted image 20241202084405.png]]

主機讀取控制器 **CAP.CSS.NCSS** 的返回值，表示 **NVM Command Set Support**。

![[Pasted image 20241202090225.png]]

**CC.CSS** 屬性會被主機設置為 `000b`，代表選擇的是 **NVM Command Set**。

![[Pasted image 20241202090645.png]]
#### (2) 設定 I/O Queue Entry Size

I/O Queue Entry Size 代表一個 Queue 的結構大小，也就是**命令結構的大小**。NVMe 規範主機提交命令給控制器為 **64 Bytes**，控制器完成命令後回傳給主機為 **16 Bytes**。

Identify Data Structure [ 513: 512 ] 可以得到控制器對於 **I/O Queue Entry Size** 標準定義。

![[Pasted image 20241203033310.png]]

**I/O Submission Queue Entry Size** : 表示提交命令資料結構大小 ( 單位 : 2^n )

![[Pasted image 20241202095513.png]]

**I/O Completion Queue Entry Size** : 表示完成命令資料結構大小 ( 單位 : 2^n )

![[Pasted image 20241202095900.png]]

當前 **IOSQES** 設定 2^6 代表 64 Bytes，**IOCQES** 設定為 2^4 代表 16 Bytes，符合標準規範。

![[Pasted image 20241203033802.png]]

### 4. 設定命令執行優先序 Round Robin Arbitration

**Round Robin Arbitration** 是 NVMe 控制器仲裁命令執行順序的一種機制。當控制器接收到多個提交隊列的命令時，仲裁機制決定命令的執行優先順序，而 **Round Robin** 模式則是一種公平分配執行機會的方式。

**TODO : 尚未了解**

### 5. 啟用控制器

**CC.EN** 是 NVMe 控制器配置暫存器（**Controller Configuration, CC**）中的一個關鍵位元，用於控制控制器的啟用和禁用狀態。當設置 **CC.EN** 為 `1` 時，控制器進入啟用狀態並開始處理命令。

![[Pasted image 20241203065144.png]]

從圖中觀察，主機會先讀取 CC 暫存器內容，確認後再將 **CC.EN** 設定為 `1`。

![[Pasted image 20241203065244.png]]
### 6. 等待控制器 Ready

主機會持續等待 **CC.RDY** 狀態被設置成 `1`，這時候控制器已經準備好可以處理主機發送的命令。

![[Pasted image 20241203065556.png]]

主機啟用控制器後，持續讀取 CSTS.RDY 狀態，直到 RDY 狀態被設定為 `1`。

![[Pasted image 20241203065646.png]]
### 7. 發送 Identify Controller

主機等待控制器都準備好 ( CSTS.RDY )，會提交第一道命令 **Identify Controller**，取得控制器狀態，並對後續執行相對的設定，例如 : 電源管理或是 HMB 等設定。

![[Pasted image 20241203071327.png]]
### 8. 取得與設定控制器 I/O Command Set 資訊

前面已經有確認支援的 I/O Command Set，這邊主機端還需要設定或取得什麼樣的資訊 ? 

主機會確認控制器有沒有支援多個 **I/O Command Set**，若是有支援多個 I/O 命令集，主機會根據支援的命令集，發送 Identify with Command Set Identifier 命令，取得相關資訊。

若是沒有支援多個 **I/O Command Set**，基本上最少也支援 NVM Command Set，因此主機也會去獲取 Identify 相關資訊。

首先會檢查 CAP.CSS.IOCSS = 1 ( 支援多個 I/O 命令集 ) 

![[Pasted image 20241205161420.png]]

以及 CC.CSS = 111b ( All Supported I/O Command Sets )

![[Pasted image 20241205161530.png]]

**(1) 提交命令 Identify I/O Command Set data structure ( CNS=1C )**

![[Pasted image 20241205152733.png]]

執行命令後會取得 **I/O Command Set Vector**，這個結構表代表結合哪幾種 I/O Command Set。

***例如 : Combination Index = 1 ，表示啟用了 NVM 和 ZNS。( 猜測 : 暫時未經過確認 )***

| Index | I/O Command Set Combination | I/O Command Set Vecctor |
| ----- | --------------------------- | ----------------------- |
| 0     | 0b0001                      | 支持 NVM Command Set      |
| 1     | 0b0101                      | 支持 NVM 和 ZNS            |
| 2     | 0b0011                      | 支持 NVM 和 Key-Value      |

![[Pasted image 20241205152858.png]]

**(2) 提交命令 Set Features with the I/O Command Set Profile**

根據取得結構表的 Index，主機可以選擇使用哪一種 **IOCSC** 命令集。

![[Pasted image 20241205154024.png]]

查詢當前所使用的 **IOCSC** 命令集，透過 Get Feature 命令回傳所選擇的 Index。

![[Pasted image 20241205154722.png]]

**(3) 提交 Identify 命令，指定支援的 I/O Command Set，獲取相關資料結構表。**

無論有無支援多個 I/O 命令集，主機多會對這些支援的命令集 ( 例如 : NVM，Zoned Namespace Command Set ) 取得相關的 Identify 資料結構表。

**範例說明 :** 假設控制器有支援 **Zoned Namespace Command Set**，主機端除了獲取 NVM Command Set 資料結構表 Identify Controller and NS ，另外也會提交命令獲取關於 ZNS Command Set 結構表。

![[Pasted image 20241205155534.png]]

如何取得關於 Zoned Data Structure 結構表呢 ?

```bash
# Namespace Datat Structure
nvme admin-passthru --opcode=0x06 --cdw10=0x05 -cdw11=0x2000000 /dev/nvme0 --data-len=4096 --read -b

# Controller Data Structure
nvme admin-passthru --opcode=0x06 --cdw10=0x05 -cdw11=0x2000000 /dev/nvme0 --data-len=4096 --read -b
```

![[Pasted image 20241205160705.png]]

### 9. 設定 Number of Queues

在 NVMe 設備中，I/O 提交隊列（Submission Queues）和完成隊列（Completion Queues）的數量直接影響 I/O 命令的並行處理能力。

主機端發出命令要求設定 I/O Queues ( Submission Queues and Completion Queues ) 數量大小，Submission Queue 以及 Completion Queue 定義為一組。

另外有一點要注意，**控制器不一定能夠符合主機端要求設定**，也就是說控制器內部所設定的 I/O Queues 可能會低於主機要求，不過最小一定會支援 One Queue。

**設定範例說明** :
* 控制器 ( 無法符合主機要求 )，控制器回覆的值會 **小於主機要求**。
* 控制器 (符合主機要求)，控制器回覆的值可能會 **等於或是大於主機要求**。

![[Pasted image 20241203100436.png]]

當主機完成設定後，控制器回覆 NCQA 以及 NSQA，代表控制器能夠建立的 I/O Queues，而主機會依據回覆的結果建立同等的 I/O Queues。

備註 : 若是控制器回覆 **NCQA=0 and NSQA=0**，則代表最小支援一個 Queue。

![[Pasted image 20241204025143.png]]

圖中可以看到主機設定 `NSQR=0x000B` 以及 `NCQR=0x000B`，要求建立 12 組 I/O Queues。控制器回覆 `NSQA=0x0007` 以及 `NCQA=0x0007`，顯然控制器無法符合主機要求，因此回覆的結果會是控制器能夠建立 I/O Queues 的數量。

![[Pasted image 20241203092444.png]]

最後主機端會根據控制器回覆 NSQA 以及 NCQA  建立 8 組 I/O Queues。設定值是 `0x0007` 為什會是 8 組 ? 因為單位最小是 **0's based value**，所以結果會是 7 + 1 = 8 。

![[Pasted image 20241203100809.png]]
### 10. 建立 I/O Completion Queues

根據前面的系統設定值以及控制器所支援的數量，首先主機會發送 **Create I/O Completion Queue**命令建立適當的 I/O Queues。

為什麼會是先建立 I/O Completion Queue ?  因為 Create I/O Submission Queue 需要指定 **Completion Queue Identifier ( CQID )**，所以主機開始會是先建立 I/O Completion Queue。

主機會針對每一個 I/O Completion Queue 分配一組獨立記憶體範圍，指定 **PRP Entry 1** 做為開始位址。這些記憶體它是存放控制器執行後的結果 **Common Completion Queue Entry**，當控制器完成命令，會將執行的結果 **Completion Queue Entry** 寫回到到記憶體。

備註 : 上述說明都是關於 **NVMe Command Processing** 命令處理的行為之一。

![[Pasted image 20241204035707.png]]

接下來指定  Queue Identifier ( Completion QID )  以及 Queue Size，其中 Queue Size 代表可以放置多少個 **Completion Queue Entry**，這也表示 I/O Completion Queue 記憶體位址範圍。

**Completion Queue Identifier**：
- 主機在創建時分配該 ID，標識唯一個 **I/O Completion Queue**。
- 建立 **I/O Submission Queue** 會指定該 Completion QID，是互相對應的關係。

![[Pasted image 20241204035812.png]]

主機設定中斷功能 ( Interrupts Enabled )，中斷向量 ( Interrupt Vector )，以及確認 **Physically Contiguous** 是否要設定 I/O Completion Queue 是不是一個連續的記憶體。

 **Interrupt Vector** : 
- NVMe 控制器使用中斷向量通知主機完成某些操作，例如 I/O 完成。
- 每個 **I/O Completion Queue** 可綁定一個單獨的中斷向量

**Physically Contiguous** : 
- 若是 PC=1，表示記憶體連續，PRP1 Entry 為記憶體起始位址。
- 若是 PC=0，表示記憶體不連續，PRP1 Entry 會做為一個 PRP List。

![[Pasted image 20241204035851.png]]

圖中簡易描述執行 **Create I/O Completion Queue** ( 備註 : 說明用，主機並不會連續建立 )。主機設定 PRP1 記憶體 ( PRP1 ) 為連續記憶體，以及 Completion Queues 數量及中斷向量與起用中斷。

![[Pasted image 20241204150039.png]]

從上述可以了解一個 **I/O Completion Queue** 所佔的記憶體空間為 16K Bytes。

**如何觀察 PRP1 記憶體的範圍 ?**
- 第一筆 PRP1 : `0x000000001:122C0000`
- 第二筆 PRP1 : `0x000000001:122C4000`
- 範圍差異 : 122C4000h - 122C0000h = 4000h = 16384 Bytes = 16K Bytes

**計算公式 :** 
- Completion Queue Entry = 16 Bytes
- Queue Size = 0x3FF = 1024
- PRP1 Memory Range = 1024 * 16 = 16384 Bytes = 16K Bytes

**從第一筆 Read 命令** 可以看到主機回寫 **CQ Entry** 開始位址就是 `0x000000001:122C0000`。

![[Pasted image 20241204160153.png]]
### 11. 建立 I/O Submission Queues

基本上跟 **I/O Completion Queues** 的設定是相同的，唯一不同的是 **Command Dword 11**。

1. **Completion Queue Identifier** ( 先前建立的 CQID )
2. **Queue Priority**  ( 僅使用 **WRR 仲裁機制** 且啟用 **Urgent Priority Class**）

![[Pasted image 20241204162025.png]]

- PRP1 : `0x00000001:14610000`
- Completion Queue Identifier : `0x0001`
- Queue Priority : `Urgent`

![[Pasted image 20241204162932.png]]

**從第一筆 Read 命令** 可以看到主機提交命令 **SQ Entry** 開始位址就是 `0x000000001:14610000`。

![[Pasted image 20241204163632.png]]
### 12. 發送非同步事件通知

這是一個非同步事件觸發 ( Asynchronous  Events ) 的功能，都是經由主機端透過 Set-Feature ( Asynchronous Event Configuration ) 設定觸發的事件，然後再發出 **Asynchronous Event Request**。如果這個觸發條件成立，控制器會將主機關注的事件通知給主機端。
 
從圖示可知，主機設定完成 Asynchronous Event Configuration 然後就發送出 Asynchronous  Events Requests，但是不會立刻回覆主機 Completion Queue。

![[Pasted image 20241204165012.png]]   

連結筆記 :  [[Asynchronous Event Request]]