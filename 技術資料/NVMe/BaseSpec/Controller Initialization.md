# Controller Initialization

1. Set the PCI and PCI Express registers described in section 2 appropriately based on the system configuration. This includes configuration of power management features. A single interrupt (e.g., pin-based, single-MSI, or single MSI-X) should be used until the number of I/O Queues is determined

   

2. The host waits for the controller to indicate that any previous reset is complete by waiting for CSTS.RDY to become ‘0’;

   **說明 :** 

   * 主機端必須等待控制器重置 (Reset) 完成
   * 並確認該狀態變成 CSTS.RDY=0

   

3. The Admin Queue should be configured. The Admin Queue is configured by setting the Admin Queue Attributes (AQA), Admin Submission Queue Base Address (ASQ), and Admin Completion Queue Base Address (ACQ) to appropriate values;

   **說明 : **

   *  設定主機端 Admin SQ & CQ Entry Memory Address
   
   **功能 :** 
   
   * 主機端告知控制器若是要取得 (SQ) 命令 或是 寫入完成的 (CQ) 命令，需要從指定的記憶位置提取或寫入
   
   
   
   ***備註 : 一旦主機端發送 Admin 命令，就可以從該命令的 PRP1 or PRP2 看到該記憶體所指定的位置***
   
   
   
   **屬性 :** 
   
   * AQA --  設定 (Admin SQ and CQ) 最大可以存放命令的數量，目前該主機端設定為 256 (0x00 - 0xFF)
   * ACQ --  設定 (Admin CQ) 所存放的記憶體位址 (當主機端完成命令後，會將 (CQ) 命令寫入到該記憶體中) 
     * ACQB Address Low : 0x02610000
     * ACQB Address High : 0x00000001
   * ASQ --  設定 (Admin SQ) 所存放的記憶體位址 (當主機端發送命令後，會將 (SQ) 命令寫入到該記憶體中)
     * ASQB Address Low : 0x0260C000
     * ACQB Address High : 0x00000001
     
     


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
   
   
   
   * CC.MPS :
   
     **說明 :** 定義主機端 Memory Page Size
   
     **設定 :** 0000b (Default) :  (2 ^ (12 + 0 )) = 4K
   
     **參數 :** 2 ^ (12 + MPS)
   
   
   
   * CC.CSS : 
   
     **說明 :** 定義 (Command Sets) 支援的型態，基本上該值都固定為 (000b)，全部支援 (Admin and I/O Command)
   
     **設定 :** 000b (Default)
   
     **參數 :** 
   
     * 000b : NVM Command Set
     * 001b to 110b : Reserved
     * 111b : Admin Command Set only (若是設定 111b，不支援 I/O Command)
   
   
   
   * CC.IOSQES : 
   
     **說明 :** I/O Submission Queue Entry Size
   
     **設定** : 0110b (2^6 = 64)
   
     **參數 :** 2^n
   
   
   
   * CC.IOCQES : 
   
     **說明 :** I/O Complete Queue Entry Size
   
     **設定 :** 0100b (2^4 = 16)
   
     **參數 :** 2^n
   
   
   
   ***Identify Controller Data Structure (IOSQES and IOCQES)***
   
   <img src="../../res/Identify_Controller_SQES_CQES.png" style="zoom:80%;" align="left"/>
   
   
   
5.  The controller should be enabled by setting CC.EN to ‘1’; 

   **說明 :** 主機端設定 CC.EN=1，控制器才可以處理 Submission Queue Tail doorbell writes

   

6. The host should wait for the controller to indicate that the controller is ready to process commands. The controller is ready to process commands when CSTS.RDY is set to ‘1’;

   **說明 :** 

   * 前面設定(第五步驟) CC.EN=1，所以主機端會等待狀態成為 CSTS.RDY=1

   **功能 :** 

   * 控制器 (CSTS.RDY=1) 才可以處理 (SQ) 命令

   

   ***Step [1-6]***

   <img src="../../res/Trace_Controller_Initialization_Register.png" style="zoom:80%;" align="left"/>

   

7. The host should determine the configuration of the controller by issuing the Identify command, specifying the Controller data structure. The host should then determine the configuration of each namespace by issuing the Identify command for each namespace, specifying the Namespace data structure

   **說明 :** 主機端 (Host) 發送 Identify Controller and Namesapce 命令取得控制器資訊，並根據這些內容作為後續設定

   **備註 :**  LeCroy (NVMe_Z4DriveEmulation.pex) 並未看到主機端發送 Identify Ctrl & Identify Namespace Command

   

8. If the controller implements I/O queues, then the host should determine the number of I/O Submission Queues and I/O Completion Queues supported using the Set Features command with the Number of Queues feature identifier. After determining the number of I/O Queues, the MSI and/or MSI-X registers should be configured;

   **說明 :**  以下由主機端發起設定 (Set-Feature) 

   * Number of Queues 
   * MSI and/or MSI-X registers
   * Arbitration

   

   **Number of Queues – Command Dword 11 :**

   * Number of I/O Submission Queues Requested (NSQR) : 0x0007 (IO SQ Entry=8)

   * Number of I/O Completion Queues Requested (NCQR) : 0x0007 (IO CQ Entry=8)

   

   **Number of Queues – Completion Queue Entry Dword 0**

   * Number of I/O Completion Queues Allocated (NCQA) : 0x0040 (64)

   * Number of I/O Submission Queues Allocated (NSQA) : 0x0040 (64)

      

   主機端要告訴控制器設定 IO SQ  & CQ Entry 數量的大小，主機端就會根據此設定值，發送 Create IO CQ & SQ 的命令建立 IO Queue Entry，可以由 ***Step [9-10]*** 確認主機端發送過程。但是控制器不見得會符合主機端所要求的這些設定，也就是說控制器內部所設定的值不一定符合主機端的要求，不過最小一定會支援 One Queue (SQ & CQ) Entry (NCQA=0x0000 and NSQA=0x0000)。

   

   **以上說明會有兩種行為產生 :** 

   * 如果主機端要求設定 IO Queue Entry，控制器 (無法符合主機要求)，則主機端會依控制器回覆的值建立 IO Queue Entry

   * 如果主機端要求設定 IO Queue Entry，控制器 (符合主機要求)，則主機端會依當初的要求的值建立 IO Queue Entry

     也就造成為什麼控制器回覆 (NCQA & NSQA = 0x0040)，而主機端還是根據當初要求的設定值建立 IO SQ & CQ Entry=8

   

   **另外一套軟體解析開機的時候設定 Number of Queues 的結果 :**

   * 主機端要求設定 IO NSQR=0x0003 & NCQR=0x0003，而控制器端也回覆 NSQA=0x0003 & NCQA=0x0003
   * 主機端收到回覆後，確認該設定值也符合主機端的要求，所以會根據主機端當初要求參數建立 IO SQ & CQ Entry
   * 主機端之後就會發出 Cerate IO CQ & SQ Commands，建立 IO SQ & CQ Entry = 0x0003 (Total = 4)

   <img src="../../res/Number_of_Queues_Detail_Data.png" style="zoom:80%;" align="left"/>

      

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
