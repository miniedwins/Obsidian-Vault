# 概要說明

**Emergency Power Fail Processing（緊急掉電處理）** 主旨在確保在電源丟失時，控製器能夠儘可能安全地完成 I/O 操作以及後續突發事件的操作流程，以防止資料丟失或損壞。

Power Loss Signaling 處理模式分為兩種 **Forced Quiescence Processing** 以及 **Emergency Power Fail Processing** 都與儲存裝置的穩定性和資料完整性相關，但它們適用於不同的情況，且處理方式不同。

**Host ( 主機端 )** 可以透過 **Power Loss Signaling Config feature** 的方式 **設定掉電處理模式**，當發生電源丟失時，控制器可以立刻通知系統正在進行處理電源丟失流程。

# 電源丟失處理模式

###  **Forced Quiescence Processing**

#### 主要目的

#### 觸發條件

#### 處理過程

###  **Emergency Power Fail Processing**

#### 主要目的

#### 觸發條件

#### 處理過程

# 電源丟失通知機制

當控制器電源發生丟失時，主機和控製器之間是如何通訊 ? 主要依賴於兩個變數 **Power Loss Notification（PLN）** 以及 **Power Loss Acknowledge（PLA）**。
### Power Loss Notification

電源丟失時主機與控制器的透過設定 **PLN** 訊號通知，表示當前電源是否丟失或是電源恢復正常：

 - **Asserted** 
	 - 表示主機通知 NVMe 裝置即將掉電。
 - **Deasserted** 
	 - 表示主機已撤銷掉電通知，或是當前電源情況正常。
### Power Loss Acknowledge
 
 控制器設定 **PLA** 訊號，用於表示當前的電源丟失處理狀態，可以分為四種處理方式：
 
- **Asserted-FQ**
	- 強制靜默流程處理中，當前狀態可以正常與主機端通訊。
- **Asserted-EPF-Enabled**
	- 緊急掉電流程處理中，當前狀態可以正常與主機端通訊。
- **Asserted-EPF-Disabled** 
	- 緊急掉電流程處理中中，當前狀態無法與主機正常端通訊。
- **Deasserted**
	- 控製器未處理任何電源丟失流程，一切正常運行。

> 疑問 :  EPF Processing Port Communication Processed ( Enable or Disable )
> 推測但不確定是否正確 : 
> 1. ( Enable ) 當前正在處理的命令，可以回覆主機端是否完成。
> 2. ( Disable) 拋棄正在處理的命令，專心處理掉電流程。


