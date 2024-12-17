# Controller Level Reset

## 基本介紹

主要的目的是對控制器進行復位，復位操作會影響整個控製器及其相關功能，會將控制器內部的`Internal state` 狀態重置，大部份 `Controller Properties` 會被清除並復位，僅有少部份**持久屬性**不會因為復位而被重置。

常規復位（Conventional Reset）和功能級復位（Function Level Reset, FLR）是根據 PCI Express 規範定義的復位方法，**它們也都會觸發 NVMe 控製器級復位（Controller Level Reset）**
## 觸發重置的三種方法

1. [[NVM Subsystem Reset]] 
2. [[Controller Reset]]
3. **Transport Specific Reset Types ( PCIe )**
	* [[Conventional Reset]]
	* [[Function Level Reset]]
## 重置的流程

當發生重置後，**控制器與主機端**如何執行後續的動作，如下所述 : 
### 控制器流程

* 控制器停止所有的 `Admin` or `I/O` Commands
* 刪除所有的 I/O Completion Queues and I/O Submission Queues
* 控制器會轉成 `Idle` 狀態，完成後 `CSTS.RDY`  會被清除為 `0`
* 所有的 `Controller Properties` 會被重置，除了持久屬性不會被重置

 **有哪些持久屬性不會被重置**  
* **( 原文 )** For Controllers using a memory-based transport
	* **Controller Reset**
		* Admin Queue Properties **`AQA`, `ASQ`, `ACQ`**
		* `CMBMSC` ( Controller Memory Buffer Memory Space )
		* Persistent Memory Region
			* **`PMRMSCU`** 
			* **`PMRMSCL`**
	* **Function Level Reset** 
		* `CMBMSC`
* **( 原文 )** For Controllers using a message-based transport
	* There are no exceptions

> **補充說明 :** 
> 1. [[Memory Based Transport]]
> 2. [[Message Based Transport]]
### 主機端流程

* **( 原文 ) Update transport specific state and controller property state as appropriate**
	* **( 譯文 )** PCI 暫存器空間會按照**PCI Express 基本規範**中的定義被重設
	* **( 譯文 )** 主機端也需要再一次設定控制器屬性
* 設定 `CC.EN=1` **( 代表控制器可以處理命令 )**
* 等待 `CSTS.RDY=0`  被控制器設定為 `CSTS.RDY=1`   **( 代表控制器可以處理 Admin SQ )**
	* `CC.EN=1` 被設定完成後，`CSTS.RDY` 會由 `0` 被切換成 `1` 
* **( 原文 ) Configure the controller using Admin commands as needed** 
	* **( 譯文 )** 應該是指設定重置後需要的一些動作 ( e.g. HBM )
* 建立 I/O Completion Queues and I/O Submission Queues
* 執行正常的 I/O 命令操作

**重置過程中注意事項 !!!**
* 除了 `Controller Reset` 之外，`Cntroller Level Reset` 操作都會導致控製器立即失去與主機的通訊
* 控製器將無法 `Abort` 任何命令或是 `Update`  Completion Queue Entries
* 通過以上兩點說明， 主機端正在傳送的資料應該也會丟失