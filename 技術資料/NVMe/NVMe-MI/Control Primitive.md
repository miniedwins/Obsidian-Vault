## 定義
Control Primitives 是一種特殊類型的訊息，屬於「Request Message」的一種，由 Management Controller (管理控制器) 發送至 Management Endpoint (管理端點)。

### 🔹 功能與目的

用來：

- **影響已送出之 Command Message 的執行行為**    

- **查詢 Command Slot 或 Management Endpoint 的狀態**
    
### 🔹 適用範圍

- **僅適用於 Out-of-Band 機制**    

    - ✅ 可用於 **Out-of-Band (OOB)** 管理通道        

    - ❌ **禁止使用於 In-Band Tunneling 機制**        

> 🔸 補充：Out-of-Band 指的是獨立於主資料路徑以外的管理通道，常用於遠端管理設備狀態。

### 🔹 與 Command Slot 的互動

- Control Primitives **可以針對特定 Command Slot 發送**
    
- **不受 Command Slot 當前狀態限制**：
    
    - 無論 Command Slot 是在何種「命令服務狀態（Command Servicing State）」都可以傳送
        
    - **會立即由 Management Endpoint 處理**
        

### 🔹 狀態影響

- **通常不會改變 Command Slot 的命令處理狀態**
    
    - 除非文件中另有特別說明，否則：
        
        - Control Primitives 僅用來控制或查詢
            
        - 不會影響命令本身的執行流程或狀態轉換

### 不需等待回應 
說明 : 與 Command Message 不同，**Control Primitive 可連續發送，不需等待前一筆 Response**。

### 只有最後一筆保證處理
說明 : 如果連續送出多筆 Control Primitive，未等回應或是處理以及處理中，**只有「最後一筆」保證被處理且回傳**，其他的可能會被忽略（discarded），Response 也不會發出。

**情境一：三筆 Primitive 是依序進入，前一筆還沒處理完就來新的**

| 時間  | 動作                 | 狀態                            |
| --- | ------------------ | ----------------------------- |
| T0  | Primitive A        | Slot idle → 收到 A、準備處理         |
| T1  | Primitive B        | 還沒處理完 A，B 到 → 蓋掉 A（discard A） |
| T2  | Primitive C        | 還沒處理 B，C 到 → 蓋掉 B（discard B）  |
| T3  | 處理 C，傳回 Response C |                               |

**情境二：Primitive A 已經開始處理（Process 中），B 和 C 進來得太快**

| 時間  | 動作                            | 狀態                             |
| --- | ----------------------------- | ------------------------------ |
| T0  | Primitive A                   | Slot idle → 收到 A、進入處理          |
| T1  | Primitive B                   | 收到，但 A 還沒回，B 覆蓋 A（依據 spec 可覆蓋） |
| T2  | Primitive C                   | 覆蓋 B                           |
| T3  | 處理結束（其實是處理 C） → 傳回 Response C |                                |
### 不會損壞前一筆
說明 : 即使多個 Control Primitive 被後送蓋掉，也不會 corrupt 之前那筆的資料或狀態。

### Response 中會攜帶 TAG
說明 : Controller 可利用 **TAG** 對應 Request and Response 做關聯。TAG 為 Controller 指定，用來識別設備回傳到 Response Message 中供對應。若是 Controller 指定 TAG=1，則設備需要回覆相同的TAG =1 作為回傳識別。

## Control Primitive

### Pause

- Pause 狀態下的 Command Slot 不會回應 Command Message
- Controller 不應在 Pause 狀態時再送新的 Command 到這個 Slot    

正確流程應是：
1. 發送 Command 1 (tag=0) 到 Command Slot 1    
2. Slot 進入 Process 狀態    
3. 發送 Pause Control Primitive → Slot 1 暫停    
4. 等待管理端（例如 BMC）處理外部原因    
5. 發送 Resume Control Primitive → Slot 1 恢復    
6. 等待 Command 1 的回應    
7. Command 1 完成後，再送 Command 2 (tag=1) 到同一個 Slot

問題錯誤流程：　
問題 : 如果 Command 1 (tag=0) 在 Slot 1 被 Pause，可以傳 Command 2 (tag=1) 到 Slot 1 嗎？
說明 : 不行，Slot 處於 Pause 狀態，不應傳新指令。應先 Resume，完成 Command 1。

### Resume

#### 🔍 **1. 為什麼 Controller 會掉包？**

其實不是「Controller 掉包」，而是 **Controller 判斷**「某個封包沒有收到」，進而 **丟棄整個回應訊息（Response Message）**。  

##### ✳️ 原因說明

Resume 時，**Endpoint 會從「上次已發送的封包」之後開始繼續傳送**，  
但假設最後一個封包（例如 packet \#2）**被 Endpoint 傳送了，但 Controller 沒收到**（可能是通訊錯誤），那 Controller 只記得自己「最後收到的是 packet \#1」。

##### ❗ 問題就出在這裡

Resume 之後，Endpoint 會傳送 packet \#3，Controller 卻期望下一包是 packet #2 ⇒ **序號錯誤（out-of-order）⇒ Controller 丟棄整個 Response Message！**

#### 🔁 **2. Pause → Resume 為什麼可能會導致封包丟棄？**

不是 Resume 本身導致掉包，而是：

- 如果 Resume **後續封包的序號**不是 Controller 所預期的 ⇒ Controller 丟棄。
    
- 若封包同步出問題 ⇒ 就需要使用 **Replay Control Primitive** 來要求重新傳送特定編號之後的封包。

#### ✅ **正確流程（防止封包掉落）**
1. `Pause` 傳送中斷。    

2. 若有疑慮是否收到最後一包，**Controller 在 Resume 前先發送 Replay**：    
    - 告知 Endpoint：**「請從 packet #N 重新開始」**        

3. `Resume` 然後 Endpoint 根據 Replay offset 重新傳送。    

4. 確保封包順序正確，避免 Controller 誤認為掉包。

### Abort

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

#### 📌 額外注意：

- `Abort` 只會作用於 **指定的 Command Slot**，不會影響其他 Slot、Endpoint、或 NVMe 控制器。
    
- 即使命令無法中止（CPAS=2h），該 Slot 最終仍會 **reset 成 Idle**，可接受新命令。
    
- 即使在 Idle，Abort 還是會回應一個成功狀態（只是沒做任何事）。


### Replay
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




