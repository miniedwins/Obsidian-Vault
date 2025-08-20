## Pause

### 概要
每個 Command Slot 都有一個 Pause Flag，標示該 Slot 是否被暫停。成功回應時會帶回 Pause Flag 狀態。也可透過 Get State Control Primitive 查詢 Command Slot 狀態。

當主機端發送 Pause Control Primitive 命令，控制器會暫停 Response 傳送與暫停等待後續封包的 timeout 計時，並且 Management Endpoint 需回傳 Success Response（表示成功接受）。

### 狀態說明
- **Idle** : 
	- Pause Control Primitive 不會改變 Pause Flag (保持 `0`)。        
- **Receive** : 
	- 表示後續封包可能延遲，但仍可正常接收封包 ( 注意 : 並非暫停接受封包 )。        
- **Process** : 
	- 不影響目前命令的處理流程，處理完成後仍會進入 Transmit 狀態。        
- **Transmit** : 
	- 在封包邊界處暫停傳送，應盡快停止後續傳輸。

### 問題處理 FAQ
- Q1：如果 Slot 1 被 Pause，能否送 Command 2 (tag=1) 到 Slot 1？
- A1：不行。Slot 處於 Pause 狀態時，不應發送新的命令。必須先 Resume，完成 Command 1。
    
- Q2：Pause 狀態下，控制器會不會回應 Control Primitive Response？
- A2：會。Pause Control Primitive 本身仍會收到一個 Success Response（或 Error Response，如果 CSI=1）。但在 Pause 狀態下，對於 Command Message 的 Response Message 會被暫停。
    
- Q3：Controller 在 Pause 狀態下，可以接受新的 Command 到相同 Slot 嗎？  
- A3：不行。在同一個 Slot 中，上一個命令尚未完成前，不應接受新的 Command。只有其他空閒的 Slot 可接受新命令。

- Q4 : CSI bit 固定為 `0h`，若設為 `1` 需不需要回應訊息？　
- A4 :  Management Point 應回傳 Invalid Parameter Error Response。

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
- **Idle 狀態**
	- Resume 無效果。    
    - Pause Flag 保持不變 (`0`)。        
- **Receive**
    - Resume 告知 Management Endpoint 繼續接收 Command Message 剩餘封包。        
    - Pause Flag 清除為 `0`。  
- **Process**    
    - 如果該 Slot 被 Pause，且尚未送出 More Processing Required Response：        
        - Request-to-Response Timer 需被重設並重新啟動。            
	    - Pause Flag 清除為 `0`。
- **Transmit**    
    - Management Endpoint 在回應 Resume Control Primitive 後，  
        繼續傳送對應的 Response Message（從暫停點之後）。        
    - Pause Flag 清除為 `0`。

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

Abort Primitive 的目的：

- **強制將某個 Command Slot 重設為 Idle 狀態**。
    
- 同時 **清除 Pause Flag（設為 0）**。
    
- 若正在執行中的命令已產生作用，則根據是否能中斷而做回應。

其本質是：

> 清除 Command Slot 狀態、資源，並嘗試中斷未完成的命令流程。

---

#### ✅ 合理應用情境

- Management Controller 發現某 Slot 無回應或狀態不明，可發送 Abort 來「清空」該 Slot。
    
- 結合 `Get State` 指令確認目前每個 Slot 狀態（是否 Busy、Paused）。
    
- 若命令發送失敗或中途要切換工作，可使用 Abort 做復原處理。

---

- `Abort` 只會作用於 **指定的 Command Slot**，不會影響其他 Slot、Endpoint、或 NVMe 控制器。
    
- 即使命令無法中止（CPAS=2h），該 Slot 最終仍會 **reset 成 Idle**，可接受新命令。
    
- 即使在 Idle，Abort 還是會回應一個成功狀態（只是沒做任何事）。


## Replay
#### 📌 功能簡介

Replay Control Primitive 的功能是：

- **重新傳送** 上一筆在 Command Slot 中處理過的 Response Message。
    
- **可以指定從哪個位置（offset）開始 replay**。
    
- 同時會將 **Pause Flag 清除（兩個 Slot 的 Pause Flag 皆設為 0）**。


#### 🔄 Replay 的細節與原則

Replay 起點（Response Replay Offset）
從原本 Response Message 的 offset 位置開始 replay，直到完整結束（含 MIC）

1. 第一個 Replay 封包必定要 SOM = 1，即使不是從 offset=0 開始
2. Replay 第一包必須含有原本的 Message Header，不管 offset 是不是 0|
3. Response Message Msg Tag 要與 Replay Control Primitive 相同
4. MCTP Message Tag 也需要先前傳遞封包的 Tag 相同

>❌ 如果 Msg Tag 設定錯誤會發生什麼？
> 因為 MCTP Message Tag 是用來分辨與組裝封包的一致性與順序依據。若 Msg Tag 不相同，Receiver（如 Management Controller）會認為這是另一筆新訊息，就無法將 Replay 封包與先前接收到的前半部分組合起來。

#### 🎯 為什麼需要 Replay？

Replay 是為了處理以下情境：

#### ✅ 常見應用情境

- **在 Pause + Resume 後，Controller 掉包或順序錯亂**（導致無法完整重組 Response Message）。
    
- **Response Message 很大，Controller 在中間掉了某一包（Packet Integrity Fail）**。
    
    - 若支援 **non-zero offset Replay**，可以指定從掉落之後的某個 Packet 重新傳送。



### 🔁 Replay with Pause 重點解釋：

(原文) : It is not an error to issue a Replay Control Primitive to a Command Slot that is paused. A Response Message is transmitted even if the Command Slot is paused at any time during the response, including before the first packet was transmitted. After successful completion of the Replay Control Primitive, neither Command Slot is paused (i.e., there is an implicit Resume Control Primitive affecting both Command Slots when processing the Replay Control Primitive except that the Management Endpoint shall not transmit a Response Message).

> **"It is not an error to issue a Replay Control Primitive to a Command Slot that is paused."**

即使某個 **Command Slot 處於 Paused 狀態**，也允許對它發送 Replay Control Primitive，不會當作錯誤。

---

> **"A Response Message is transmitted even if the Command Slot is paused at any time during the response..."**

即使 Response Message 的傳送過程中，Command Slot 被暫停（Paused），Replay 還是會重新發送該 Response。

---

> **"After successful completion of the Replay Control Primitive, neither Command Slot is paused..."**

當 Replay Control Primitive 成功後：

- **相關的 Command Slots 都會自動 Resume（恢復傳送）**
    
- 雖然沒有明確送出 Resume Control Primitive，但這個 Replay 動作的副作用就是 **Resume Both Slots**。
    

---

> **"except that the Management Endpoint shall not transmit a Response Message"**

這句是補充條件：

- 雖然 Command Slot Resume 了，
    
- **但 Management Endpoint（Responder）不能因為 Replay Control Primitive 而回傳新的 Response Message**（因為 Replay 是重播前面已存在的 Response，不該產生新的訊息）




