# 概要說明

**Emergency Power Fail Processing（緊急掉電處理）** 主旨在確保在電源丟失時，控製器能夠儘可能安全地完成 I/O 操作以及後續突發事件的操作流程，以防止資料丟失或損壞。

Power Loss Signaling 處理模式分為兩種 [[Forced Quiescence Processing]] 以及 [[Emergency Power Fail Processing]] 都與儲存裝置的穩定性和資料完整性相關，但它們適用於不同的情況，且處理方式不同。

**Host ( 主機端 )** 可以透過 **Power Loss Signaling Config feature** 的方式 **設定掉電處理模式**，當發生電源丟失時，控制器可以立刻通知系統正在進行處理電源丟失流程。

那麼控制器如何通知 **Host ( 主機端 )** 發生掉電呢 ? 主要是透過 **PLN** 訊號通知系統發生電源丟失，以及 **PLA** 訊號來表示正在處理掉電流程 ( FQ 或是 EPF )。需要注意的是，任何時候都不能有多個斷電訊號模式處於活動狀態。
# 電源丟失通知機制

當控制器電源發生丟失時，主機和控製器之間是如何通訊 ? 主要會使用到這兩個變數  [[Power Loss Notification]] 以及  [[Power Loss Acknowledge]]。

- **`Power Loss Notification`** : 
	- 通知控制器即將發生斷電。
- **`Power Loss Acknowledge`** : 
	- 通知主機端正在處理斷電流程。
## 通知流程

1. 主機檢測到斷電風險（例如電源不穩定或電池電量低）。    
2. 主機將 PLN 信號設置為 **Asserted**，並通過 NVMe 傳輸層發送給控制器。    
3. 控制器收到 PLN 信號後，根據當前狀態設置 PLA 信號（例如 Asserted-FQ 或 Asserted-EPF-Enabled）。    
4. 主機根據 PLA 信號判斷控制器的準備情況，並決定是否繼續操作或採取其他措施。    
5. 當斷電風險解除後，主機將 PLN 信號設置為 **Deasserted**，控制器也會將 PLA 信號設置為 **Deasserted**。

> 疑問 : 
> 1. EPF Port Communication Processed 通訊的定義 ? 
# 電源丟失處理狀態機

![[Pasted image 20250225071237.png]]
# 控制器支援條件

- 至少支援其中一個掉電模式處理，或者是兩個都支援
	- Forced Quiescence Processing ( FQ )
	- Emergency Power Fail Processing ( EPF )
- Power Loss Signaling 需要條件
	- 支援 Power Loss Acknowledge ( PLA ) 	
	- 支援設定 Power Loss Signaling Config feature
	- 至少支援一個或是多個 Power States ( FQ & EPF )
	- 根據支援的模式，需要回報 FQ & EPF Vault Time
	- 支援回報 I/O Performance is degraded
- 選擇性支援
	- Power Loss Acknowledge ( PLN )