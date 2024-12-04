## NVMe 初始化設定

下圖是主機初始化 NVMe 控制器的完整過程，這些步驟是基於 NVMe 規範中的描述。從圖中觀察 Linux 開機行為來看，不過似乎沒有遵循 **Controller Initialization**，但不影響整體觀察。

![[Pasted image 20241202071500.png]]

完成控制器初始化後，主機就會開始發送命令確認狀態或是使用 Set Feature 命令設定相關功能。

![[Pasted image 20241203091933.png]]
### 1. 等待控制器完成重置

檢查控制器狀態暫存器（CSTS）的 **RDY（Ready）位**，確認其值為 `0`，表示重置完成。
### 2. 設定 Admin Queue 記憶體位址與數量

在 NVMe 中，**Admin Queue** 包括 **Admin Submission Queue ( ASQ )** 和 **Admin Completion Queue ( ACQ )**，用於放置管理命令 ( 提交與完成 )，如 **Identify** 和 **Set Features**。它們的大小（Size）和基址（Base Address）需要主機在控制器初始化階段進行配置。
#### (1) 設定 Admin Queue Size

主機端設定控制器 Admin Queue Size 數量為多少，表示主機可以放置多少提交與完成最大管理命令數量，而非一次可以處理多少個命令。另外 ，Admin 命令都是一筆一筆執行，並沒有多工。

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
	- 設置 **CC.CSS = 110b**（支持 多個 I/O 命令集）。
- **CAP.CSS.NCSS = 1  and CAP.CSS.IOCSS = 0**：
	- 設置 **CC.CSS = 000b**（支持 NVM 命令集）。

![[Pasted image 20241202081215.png]]

這裡要注意一下，若是 **CC.CSS = 111b**，代表控制器僅支援 **Admin Command Set**。

![[Pasted image 20241202084405.png]]

主機讀取控制器 **CAP.CSS.NCSS** 的返回值，表示支持 NVM 命令集。

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

主機會持續等待 **CC.RDY** 狀態被設置成 `1`，這時候控制器已經準備好可以執行 Submission Queue，代表控制器可以開始處理主機發送的命令。

![[Pasted image 20241203065556.png]]

主機啟用控制器後，持續讀取 CSTS.RDY 狀態，直到 RDY 狀態被設定為 `1`。

![[Pasted image 20241203065646.png]]

### 7. 發送 Identify Controller

主機等待控制器都準備好 ( CSTS.RDY )，會提交第一道命令 **Identify Controller**，取得控制器狀態，並對後續執行相對的設定，例如 : 電源管理或是 HMB 等設定。

![[Pasted image 20241203071327.png]]
### 8. 確認控制器 I/O Command Set 設定資訊



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
- 第一筆 PRP1 : 0x000000001:1220000
- 第二筆 PRP1 : 0x000000001:1224000
- 範圍差異 : 1224000h - 1220000h = 4000h = 16384 Bytes = 16K Bytes

**計算公式 :** 
- Completion Queue Entry = 16 Bytes
- Queue Size = 0x3FF = 1024
- PRP1 Memory Range = 1024 * 16 = 16384 Bytes = 16K Bytes
### 11. 建立 I/O Submission Queues



### 12. 發送非同步事件通知




## NVMe 初始化總結

========================================================
 
 
 


4. The controller settings should be configured. Specifically:
   a. The arbitration mechanism should be selected in CC.AMS;
   b. The memory page size should be initialized in CC.MPS; and NVM Express TM Revision 1.4a 298
   c. The I/O Command Set that is to be used should be selected in CC.CSS or CC.CSS field should be set to the value indicating that only the Admin Command Set is supported;

   **說明 :** 

   * 建立仲裁機制 (Round Robin)
   * 設定主機端 Memory Page Size = 4K
   * 設定支援 NVM Command Set
   * 設定 IOSQES=64  IOCQES=16
   
   
   
   **屬性 :**
   
   * CC.AMS : 
   
     **說明 :** 設定仲裁機制
   
     **設定 :** 000b
   
     **參數 :** 
   
     * 000b : Round Robin
     * 001b : Weighted Round Robin with Urgent Priority Class
     * 010b to 110b : Reserved
     * 111b : Vendor Specific
   
   

   
  
  

8. If the controller implements I/O queues, then the host should determine the number of I/O Submission Queues and I/O Completion Queues supported using the Set Features command with the Number of Queues feature identifier. After determining the number of I/O Queues, the MSI and/or MSI-X registers should be configured;

   **說明 :**  以下由主機端發起設定 (Set-Feature) 

   * Number of Queues 
   * MSI and/or MSI-X registers
   * Arbitration   
     

   **MSI and/or MSI-X registers :**

   **說明 :** 

   * 設定是否要使用中斷聚合 (多個 (SQ) 命令完成後發起一次中斷，目的減少主機端 (CPU) 消耗)
   * 若是設定的參數 (TIME) & (THR) 符合，就會發起中斷請求
   * 目前主機端並沒有設定 (中斷聚合)

   **設定 :** 

   * Aggregation Time (TIME) : 0 
   * Aggregation Threshold (THR) : 0 

   **參數 :** 

   * Aggregation Time : 最大中斷延遲時間

   * Aggregation Threshold  : 最大中斷聚合的數量

   

   **Arbitration :** 

   * 設定仲裁機制 Arbitration Burst (AB) : 000b

   * Bits 2:0 = 000b (Round Robin)

   <img src="../../res/Feature_Identifier_01h_Arbitration.png" style="zoom:80%;" align="left"/>

   

      ***Step [7-8]***  

   <img src="../../res/Trcae_Number_of_Queues.png" style="zoom:80%;" align="left"/>

   

9. If the controller implements I/O queues, then the host should allocate the appropriate number of I/O Completion Queues based on the number required for the system configuration and the number supported by the controller. The I/O Completion Queues are allocated using the Create I/O Completion Queue command;

   **說明 :** 

   * 根據前面的系統設定值以及控制器所支援的數量，主機端會發送 Create I/O Completion Queue 建立適當的 I/O CQ Entry

   * 主機端 (Host) 連續建立 I/O CQ Entry = 8

   * 設定每個屬性

     * Queue Identifier (QID)  :  0x0001 ~ 0x0008 (CQID)

     * Queue Size (QSIZE) : 0x03FF (1024) (可以存放多少個CQ命令)

     * PRP Entry 1 :

       * 主機端會針對每個 CQ Entry 分配一個獨立的記憶體位置
       * 控制器處理 (SQ) 命令完成後，會從主機端分配的記憶體位置寫入 Completion Queue Entry 命令

     * Physically Contiguous (PC) : 1

     * Interrupts Enabled (IEN) : 1 (啟用中斷功能)

     * Interrupt Vector (IV) : 0x0001 ~ 0x0008 

       * QID & IV 基本上會是對應關係
       * Example : QID=0x0001, IV=0x0001

       

   > 補充 : 為什麼先建立 I/O Completion Queue Entry?
   >
   > Create I/O SQ Command 必須要指定 Completion Queue Identifier (CQID)，所以需要先建立的 CQ Entry。



10. If the controller implements I/O queues, then the host should allocate the appropriate number of I/O Submission Queues based on the number required for the system configuration and the number supported by the controller. The I/O Submission Queues are allocated using the Create I/O Submission Queue command; and

    **說明 :** 

    * 根據前面的系統設定值以及控制器所支援的數量，主機端會發送 Create I/O Submission Queue 建立適當的 I/O SQ Entry
    * 連續建立 I/O SQ Entry = 8
    * Queue Identifier (QID) : 0x0001 ~ 0x0008 (SQID)
    * Queue Size (QSIZE) : 0x03FF (1024) (可以存放多少個SQ命令)
    * PRP Entry 1 
      * 主機端會針對每個 SQ Entry 分配一個獨立的記憶體位置
      * 主機端發送 (SQ) 命令，都會往指定的記憶體寫入命令
      * 一但有命令 (SQ Tail Door Bell Register) 被寫入，控制器會從主機端分配的記憶體位置取 (SQ) 命令
    * Physically Contiguous (PC) : 1
    * QPRIO (Queue Priority) : Medium
    * CQID : 0x0001 ~ 0x0008 
      * 每一個 SQID 會對應一個 CQID
      * Example : QID=0x0001 & CQID=0x0001

    

    ***Step [9-10]***

    <img src="../../res/Trcae_Create_IO_CQ_SQ.png" style="zoom:80%;" align="left"/>



11. To enable asynchronous notification of optional events, the host should issue a Set Features command specifying the events to enable. To enable asynchronous notification of events, the host should submit an appropriate number of Asynchronous Event Request commands. This step may be done at any point after the controller signals that the controller is ready (i.e., CSTS.RDY is set to ‘1’)

    **說明 :** 

    這是一個非同步事件觸發 (asynchronous  events) 的功能，都是經由主機端透過 Set-Feature (Asynchronous Event Configuration) 設定觸發的事件，如果這個觸發條件成立，控制器會將這該事件通知給主機端 (Return Complete Queue Command to CQ Entry)。

    

    從圖示可知，主機端設定完成 Asynchronous Event Configuration 然後就發送出 Asynchronous  Events Requests，但是不會立刻回覆 Completion Queue Command。不過目前設定 Event Configuration 都是清除為零，所以不會有任何觸發事件。

    

    ***Step [11]***

    <img src="../../res/Trcae_Asynchronous Event Request.png" style="zoom:80%;" align="left"/>



**NVMe 初始化流程總結 :** 

經過這些初始化流程過後，系統就可以對控制器發送 I/O Command (e.g., Write, Read)

1. 系統設定 PCI Express 相關事項
2. Host 等待先前的 Reset 重置操作，然後等待控制器變成 Not Ready (CSTS.RDY=0)
3. Host 設定暫存器 (CC.AQA, CC.ACQ, CC.ASQ)，配置 (SQ & CQ Entry) 記憶體位置 
4. Host 設定暫存器 (CC.AMS, CC.MPS, CC.CSS, CC.IOSQES, CC.IOCQES)
5. Host 啟用控制器 CC.EN=1
6. Host 等待控制器 Ready (CSTS.RDY=1)
7. Host 發送 Identify Controller & Identify Namespace Commands
8. Host 透過 Set Feature (Number of Queues) 設定 IO SQ & CQ Entry 的數量以及中斷功能
9. Host 透過 Admin Command (Create I/O Completion Queue) 命令建立 I/O CQ Entry
10. Host 透過 Admin Command (Create I/O Submission Queue) 命令建立 I/O SQ Entry
11. Host 透過 Set Feature (Asynchronous Event Configuration) 設定非同步事件 (asynchronous  events)
