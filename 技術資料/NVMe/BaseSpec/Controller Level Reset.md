# Controller Level Reset

## 基本介紹

主要的目的是對控制器進行復位，復位操作會影響整個控製器及其相關功能，會將控制器內部的`Internal state` 狀態重置，大部份 `Controller Properties` 會被清除並復位，僅有少部份 **持久屬性** 不會因為復位而被重置。其他形式的控製器級復位會根據相關的 **NVMe傳輸繫結規範** 對控製器屬性進行重設。

> Controller Properties : 定義在 Base-Specification
## 重置的三種方法

1. [[NVM Subsystem Reset]] 
2. [[Controller Reset]]
3. Transport Specific Reset Types
## 重置的流程

當發生重置後，**控制器與主機端**後續的執行動作，如下所述 : 

**控制器行為流程**
* 控制器停止所有的 `Admin` or `I/O` Commands
* 刪除所有的 I/O Completion Queues and I/O Submission Queues
* 控制器會轉成 `Idle` 狀態，完成後 `CSTS.RDY`  會被清除為 `0`
* 所有的 `Controller Properties` 會被重置，除了持久屬性不會被重置

 **有哪些持久屬性不會被重置**  
* **( 原文 )** For Controllers using a memory-based transport
	* **控制器屬性後面標示 ( 括號 ) 是說明哪一種 Reset 不會被重置**
	* Admin Queue Properties `AQA`, `ASQ`, and `ACQ` ( Controller Reset )
	* `CMBMSC` ( Controller Reset and Function Level Reset )
	* `PMRMSCU` and `PMRMSCL` ( Controller Reset )
* **( 原文 )** For Controllers using a message-based transport
	* There are no exceptions

> **補充說明 :** 
> 1. [[#基於記憶體的傳輸協議]] - Memory-based Transport 
> 2. [[#基於消息傳遞機制]] - Message-based transport

**主機端行為流程**
* **( 原文 ) Update transport specific state and controller property state as appropriate**
	* **( 譯文 )** PCI 暫存器空間會按照 **PCI Express 基本規範**中的定義被重設
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
* 通過以上兩點說明， 上主機端正在傳送的資料應該也會丟失

## 補充說明

### 基於記憶體的傳輸協議

NVMe 控製器**使用基於記憶體的傳輸方式**，通常是指通過共用記憶體或記憶體對應的機制在主機與控製器之間傳遞資料，而不是傳統的暫存器訪問。

- 在 PCIe 中，NVMe 控製器和主機共享相同的記憶體空間，主機可以直接通過記憶體對應訪問 NVMe 控製器的暫存器和資料結構，如命令佇列 **( Admin SQ )** 和完成佇列 **( Admin CQ )**。
- PCIe 的高頻寬和低延遲使其非常適合在高性能儲存裝置（如 NVMe SSD）上使用。
### 基於消息傳遞機制

主機和 NVMe 控製器之間的通訊是通過消息 **( 特定傳輸協議 )** 的形式進行的，而不是直接訪問記憶體或暫存器。

- 主機和控製器之間通過封裝在特定傳輸協議（例如 : PCIe 或 TCP）中的消息進行通訊。
-  NVMe 命令、封包和響應，使用這些消息來管理主機對 NVMe 控製器的命令提交和完成。
- 例如 : 主機將 NVMe 命令封裝成 PCIe 封包傳遞出去，任何的資料或是響應都透過 PCIe 傳輸協議。控制器收到後封包並且取出 NVMe 命令，解析來自主機端命令的內容。