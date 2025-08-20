## Pause
### 概要
每個 Command Slot 都有一個 Pause Flag，標示該 Slot 是否被暫停。成功回應時會帶回 Pause Flag 狀態。也可透過 Get State Control Primitive 查詢 Command Slot 狀態。

當主機端發送 Pause Control Primitive 命令，控制器會暫停 Response 傳送與暫停等待後續封包的 timeout 計時，並且 Management Endpoint 需回傳 Success Response（表示成功接受）。

這裡提到的計時器 ( Timer )，Management Endpoint 會停用等待封包的 Timeout 計時器（定義於 MCTP Base Spec）。Command Timeout 時間是 `100ms` ( MCTP 傳輸綁定規範指定的時間 )。

### 狀態說明
- **Idle 狀態** : 
	- Pause Control Primitive 不會改變 Pause Flag (保持 `0`)。        
- **Receive 狀態** : 
	- 表示後續封包可能延遲，但仍可正常接收封包 ( 注意 : 並非暫停接受封包 )。        
- **Process 狀態** : 
	- 不影響目前命令的處理流程，處理完成後仍會進入 Transmit 狀態。        
- **Transmit 狀態** : 
	- 在封包邊界處暫停傳送，應盡快停止後續傳輸。

### 問題處理 FAQ
- Q1：如果 Slot 1 被 Pause，可以接受新的 Command 到相同 Slot 嗎？
- A1： A3：不行。在同一個 Slot 中，上一個命令尚未完成前，不應接受新的 Command。只有其他空閒沒有被 Pause 的 Slot 可接受新命令。

- Q2：Pause 狀態下，控制器會不會回應 Control Primitive Response？
- A2：會。Pause Control Primitive 本身仍會收到一個 Success Response（或 Error Response，如果 CSI=1）。對於 **Command Message 的 Response Message 會被暫停**。
    
- Q4 : CSI bit 固定為 `0h`，若設為 `1` 需不需要回應訊息？　
- A4 :  Management Point 應該要回傳 Invalid Parameter Error Response。

### 其他備註
1. The `CPSP` field for the Pause Control Primitive is reserved
2. The `CSI` bit in a Pause Control Primitive is not used and shall be cleared to `0h`. 

## Resume
### 概要
恢復被 Pause 的 Command Slot，使其繼續 Response 傳送與恢復 timeout 計時。基本上 Resume 會與 Pause 成對使用，Management Controller 動作會是先 Pause 然後再 Resume。

### 為什麼會遺失封包？
另外需要探討的是 Management Controller 為什麼會收到不一致的封包，而造成掉包的影響 ? 

##### 管理端是如何判斷掉包 ?
如果 Resume 後續封包的序號 ( Packet Number ) 不是 Controller 所預期的 ⇒ Controller 丟棄。 

##### Pause → Resume 為什麼可能會導致封包丟棄？
Resume 時，Endpoint 會從「上次已發送的封包」之後開始繼續傳送，但假設最後一個封包（例如 Packet \#2）被 Endpoint 傳送了，但 Management Controller 沒收到，那 Controller 只記得自己「最後收到的是 Packet \#1」。序號錯誤（out-of-order）進而丟棄整個 Response Message！

##### 正確流程（防止封包掉落）
1. Pause 傳送中斷。    
2. Controller 在 Resume 前先發送 Replay 告知 Endpoint「請從 Packet \#NN  重新開始」        
3. Resume 然後 Endpoint 根據 Replay offset 重新傳送。    
4. 確保封包順序正確，避免 Controller 誤認為掉包。

### 狀態說明
#### Idle 狀態
- Resume 無效果。    
- Pause Flag 保持不變 (`0`)。        
#### Receive 狀態
- Resume 告知 Management Endpoint 繼續接收 Command Message 剩餘封包。        
    - Pause Flag 清除為 `0`。  
#### Process 狀態
- 如果該 Slot 被 Pause，且尚未送出 More Processing Required Response：        
       - Request-to-Response Timer 需被重設並重新啟動。            
	   - Pause Flag 清除為 `0`。
#### Transmit 狀態
- Management Endpoint 在回應 Resume Control Primitive 後，  
        繼續傳送對應的 Response Message（從暫停點之後）。        
-  Pause Flag 清除為 `0`。

### 流程範例
- Host 發送 Command 1 → Slot 1 進入 Process。
- Host 發送 Pause → Slot 1 暫停，控制器停止回傳 Response。    
- Host 發送 Resume → Slot 1 恢復，控制器從 Pause 前最後一個已送封包之後繼續傳送。
- 如果 Pause 前最後一個封包遺失，Resume 後的 Response 會發生序號錯誤 → Host 丟棄該 Response。
- Host 應送 Replay Control Primitive，要求控制器從指定的封包序號開始重送 Response。

### 問題處理 FAQ
- Q1 : 若是 Command Slot 在沒有 Pause 狀態下收到 Resume，會造成影響嗎 ?
- A1 : 接受端 ( Management Point ) 會成功完成命令，並不會造成任何影響。

- Q2：Resume 會自動補齊遺失的封包嗎？  
- A2：不會。需要主機透過 Replay Control Primitive 明確要求重送。

### 其他備註
1. The `CPSP` field for the Resume Control Primitive is reserved. 
2. The `CPSR` field in the Control Primitive Success Response is reserved.

## Abort
### 概要
重新初始化指定的 Command Slot → 轉為 `Idle` 狀態並且清除 Pause Flag = 0，其本質是清除 Command Slot 狀態、資源，並嘗試中斷未完成的命令流程。

### 影響範圍    
- 僅影響目標 Command Slot。       
- 不影響：  
	- 另一個 Command Slot
	- 其他 Management Endpoints    
	- NVMe Controllers in NVM Subsystem            

### 狀態說明
#### Idle 狀態
- Abort 不影響。
- 回傳 Response Success with `CPAS=0h`。
#### Receive 狀態    
- Slot 內容被丟棄 → 狀態轉為 Idle。
- 回傳 Response Success with `CPAS=1h`
#### Process 狀態
- Slot 內容被丟棄 → 轉為 Idle。
    - 分兩種情況：  
        a) **尚未開始處理命令**        
        - 回傳 Response Success with `CPAS=0h` 。
        b) **命令正在處理中**
	    - 內容被丟棄 → 狀態轉為 Idle。
		- Management Endpoint 嘗試中止命令：
            - 若成功中止且對 NVM Subsystem 無影響 →Response Success with `CPAS=1h` 。
            - 若無法中止（命令可能部分已執行） → Response Success with `CPAS=2h` 。
#### Transmit 狀態
- Slot 內容被丟棄 → 轉為 Idle。
- 回傳 Response Success with `CPAS=0h`。

#### CPAS 欄位說明
- `CPAS` ( Command Processing Abort Status ) 欄位說明 : 
	- `00h` : Command aborted after processing completed or no command to abort
	- `01h` : Command aborted before processing began
	- `02h` : Command processing partially completed

### 應用情境
- 對主機端來說 : 
	- 若命令發送失敗或中途要切換工作，可使用 Abort 做重置處理。
	- Command Slot 無回應或狀態不明，可發送 Abort 來「清空」該 Slot。
- 即使命令無法中止（CPAS=2h），該 Slot 最終仍會切換到 Idle 狀態，可接受新命令。

### 問題處理 FAQ
Q1 : 若 Slot 處於 Pause 狀態，然後收到 Abort Control Primitive ?
A1 : Abort 不視為錯誤，Slot 會被重新初始化，Pause Flag 清除為 `0`。

### 其他備註
1. The `CPSP` field for the Resume Control Primitive is reserved. 

## Replay
### 概要
一般通訊的過程中，主機端接收的資料可能會與實際上不一致 ( 例如：封包遺失或是資料不正確 )，因此 Replay 主要用途，就是讓主機端可以重新傳送 Command Slot 中處理過的 Response Message。

### 功能說明
- 可以指定從哪個位置（offset）開始 Replay。
- 當收到 Replay 後，對應的 Command Slot 的 `Pause Flag` 會被清除為 0。
- 重播資料從 Response Replay Offset 開始，一直到原本 Response Message 的結尾。

### 狀態說明
#### Idle 狀態
- 重播是否成功 → 取決於是否有可用的 Response Message。   
    - **若剛經過 Abort / Reset → 無可重播的 Response**        
        - 回覆 Success Response，`RR bit = 0`。            
    - **若已處理過至少一個 Command → 可重播** 
        - 回覆 Success Response，`RR bit = 1`。 
        - 然後傳送該 Response Message 的 MCTP 封包（從指定的 RRO 開始）。            
#### Receive 狀態
- 無法進行重播，因為命令仍在接收。
- 回覆 Success Response，`RR bit = 0`。
#### Process 狀態
- 如果 **尚未傳送 More Processing Required (MPR) Response**：   
    - 回覆 Success Response，`RR bit = 0`。        
- 如果 **已傳送過 MPR Response**：    
    - 回覆 Success Response，`RR bit = 1`。        
    - 重新傳送 **MPR Response**，並更新其中的 **More Processing Required Time** 欄位。       
#### Transmit 狀態
- 停止當前的 Response 傳輸。   
- 回覆 Success Response，`RR bit = 1`。    
- 依照 `RRO` 欄位指定的位置，重播 Response Message 的剩餘封包。    
- Command Slot 保持在 Transmit 狀態直到重播完成。

### 流程範例
1. 第一個 Replay 封包必定要 `SOM=1`，即使不是從 offset=0 開始。
2. Replay 第一包必須含有原本的 `Message Header`，不管 offset 是不是從第 `0` 開始。
3. MCTP Message Tag 也需要先前傳遞封包的 Tag 相同。

>❌ 如果 Msg Tag 設定錯誤會發生什麼？
> 因為 MCTP Message Tag 是用來分辨與組裝封包的一致性與順序依據。若 Msg Tag 不相同，Receiver（如 Management Controller）會認為這是另一筆新訊息，就無法將 Replay 封包與先前接收到的前半部分組合起來。

### 錯誤處理流程（Offset ≠ 0h）
1. Management Controller 收到一串 Response 封包 → 前半部分 OK。
2. 某個封包出錯 → MCTP 層會終止組裝。
3. 把已收到的正確部分交給 NVMe-MI 層。
4. 指定 Replay Offset → 要求從某個位置繼續傳送。        
5. NVMe-MI 層 → 將「前半部分 + Replay 後的部分」組合成完整 Response。    
6. 驗證整體 MIC（跨完整訊息）。

### 應用情境
- 在 Pause + Resume 後，Controller 掉包或順序錯亂（導致無法完整重組 Response Message）。
- 檢查 Response Message with MIC 發生資料比對不一致。

### 問題處理 FAQ
1. 即使某個 Command Slot 處於 Paused 狀態，也允許對它發送 Replay Control Primitive，不會當作錯誤。
2. 即使 Response Message 的傳送過程中，Command Slot 被暫停（Paused），Replay 還是會重新發送該 Response。
3. 當 Replay Control Primitive 成功後：
	- 相關的 Command Slots 都會自動 Resume（恢復傳送）    
	- 雖然沒有明確送出 Resume Control Primitive，但這個動作就是 Resume Both Slots。

