# Controller Level Reset

## 介紹

主要的目的是對控制器進行復位，復位操作會影響整個控製器及其相關功能，會將控制器內部的`Internal state` 重置。 大部份 `Controller Properties` 會被清除並復位，僅有少部份 **持久屬性** 不會因為復位而被重置。其他形式的控製器級復位會根據相關的 **NVMe傳輸繫結規範** 對控製器屬性進行重設。

> Controller Properties : 定義在 Base-Specification
## 重置的三種方法

1. NVM Subsystem Reset
2. Controller Reset
3. Transport Specific Reset Types
## 重置的流程

重置分為控制器與主機端後續的執行動作，如下所述 : 

**控制器行為流程**
* 控制器停止所有的 `Admin` or `I/O` Commands
* 刪除所有的  I/O `SQ` 以及 `CQ` 
* 控制器會轉成 `Idle` 狀態，完成後 `CSTS.RDY`  會被清除為 `0`
* 所有的 `Controller Properties` 會被重置，除了持久屬性不會被重置

 **有哪些持久屬性不會被重置** 
* Controllers using a memory-based transport:
	* Admin Queue Properties `AQA`, `ASQ`, and `ACQ` ( Controller Reset )
	* `CMBMSC` ( Controller Reset and Function Level Reset )
	* `PMRMSCU` and `PMRMSCL` ( Controller Reset )

**主機端行為流程**
* Update transport specific state and controller property state as appropriate
* 設定 `CC.EN=1`
* 等待 `CSTS.RDY=0`  被設定為 `CSTS.RDY=1`
* **( 原文 ) Configure the controller using Admin commands as needed** 
	* 應該是指設定重置後需要的一些動作 ( e.g. HBM )
* 建立 I/O Completion Queues and I/O Submission Queues
* 執行正常的 I/O 命令操作