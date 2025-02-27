# 概要說明
**Emergency Power Fail Processing（緊急掉電處理）** 主旨在確保在電源丟失時，控製器能夠儘可能安全地完成 I/O 操作以及後續突發事件的操作流程，以防止資料丟失或損壞。

Power Loss Signaling 處理模式分為兩種 [[Forced Quiescence Processing]] 以及 [[Emergency Power Fail Processing]] 都與儲存裝置的穩定性和資料完整性相關，但它們適用於不同的情況，且處理方式不同 。

**Host ( 主機端 )** 可以透過 [[Power Loss Signaling Config]] 的方式 **設定掉電處理模式**，當發生電源丟失時，控制器可以立刻通知系統正在進行處理電源丟失流程。

那麼控制器如何通知 **Host ( 主機端 )** 發生掉電呢 ? 主要是透過 **PLN** 訊號通知系統發生電源丟失，以及 **PLA** 訊號來表示正在處理掉電流程 ( FQ 或是 EPF )。需要注意的是，任何時候都不能有多個斷電訊號模式處於活動狀態。

# 電源丟失通知機制
當控制器電源發生丟失時，主機和控製器之間是如何通訊 ? 主要會使用到這兩個變數  [[Power Loss Notification]] 以及  [[Power Loss Acknowledge]]。

1. **`Power Loss Notification`** :  
	- 主機透過 PLN 腳位設定 `Asserted`，通知控制器即將發生斷電。
2. **`Power Loss Acknowledge`** :  
	- 控制器透過 PLA  腳位設定 `Asserted`，通知主機端正在處理斷電流程。

## 通知流程
1. 主機檢測到斷電風險（例如電源不穩定或電池電量低）。    
2. 主機將 PLN 信號設置為 `Asserted`。    
3. 控制器收到 PLN 信號後，根據當前狀態設置 PLA 信號（例如 Asserted-FQ 或 Asserted-EPF-Enabled）。    
4. 主機根據 PLA 信號判斷控制器的準備情況，並決定是否繼續操作或採取其他措施。    
5. 當斷電風險解除後，主機將 PLN 信號設置為 `Deasserted`，控制器也會將 PLA 信號設置為 `Deasserted`。

# 電源丟失處理狀態機
控制器在接收到電源丟失通知（Power Loss Notification, PLN）後，如何處理並響應主機。
### (1) PLS Not Ready（未準備狀態）
- 控制器處於未準備好（Not Ready）狀態，不接受新的 I/O 命令。
- 當電源被恢復且初始化完成後，控制器會轉入 `PLS Ready` 狀態。
- 若是未完成掉電丟失處理，需要等待完成後，才會進入到 `PLS Ready` 狀態。
- 觸發條件：
    - **上電後的初始狀態**
    - **Forced Quiescence 未完成**
    - **Emergency Power Fail Recovery 未完成**  
### (2) PLS Ready（正常運行狀態）
- 控制器處於正常運行狀態，能夠執行 I/O 命令。
- **當 PLN 設為 Asserted 時，狀態轉變為 PLS Processing**。
### (3) PLS Processing（電源丟失處理狀態）
- 根據主機設定，控制器開始處理電源丟失模式。
- 當 PLN 設為 `Deasserted` 並且處理完成時，狀態轉變為 PLS Ready。
### (4) PLS Recovery（掉電恢復狀態）
- 當電源恢復時，控制器進行自檢 ( 可能處理未完成，繼續處理)，恢復資料完整性。
- 當控制器完成掉電恢復並準備好接收 I/O 命令時，狀態轉變為 `PLS Ready`。

![[Pasted image 20250225071237.png]]

> Note :
> 1. EPF is Enabled & PLN is Asserted & EPF Processing Port Enabled state is supported.
> 2. EPF is Enabled & PLN is Asserted & EPF Processing Port Disabled state is supported.
> 3. FQ is Enabled & PLN is Asserted.

# 控制器支援 PLS 條件
- 至少支援其中一個掉電模式處理，或者是兩個都支援：
	- Forced Quiescence Processing ( FQ )
	- Emergency Power Fail Processing ( EPF )
- 支援 Power Loss Acknowledge ( PLA ) 	
- 選擇性支援  Power Loss Acknowledge ( PLN )
- 支援 Power Loss Signaling Config feature
- 根據支援的模式而定，需要回報處理與恢復時間：
	- 所有的回報時間都不能為 `0`： 
		- `FQVT`（Forced Quiescence Vault Time）
		- `EPFVT`（Emergency Power Fail Vault Time）
		- `EPFRT`（Emergency Power Fail Recovery Time） 
	- 支援一個或是多個 Power States
		- 表示不同的 PS，處理與恢復時間會有所不同
- 支援回報 I/O Performance is degraded：
	- [[Namespace Status]] ( NSTAT ) 
		- 描述 I/O Impacted ( IOI ) 狀態
		- 描述 NS 是否準備接收 I/O

>備註 :
>1. `FQ` 沒有恢復時間，它的流程屬於正常關機，因此猜測沒有恢復時間的欄位值。
>2. `EPF` 它的流程屬於不正常掉電，控制器表示需要多久恢復時間的欄位值。