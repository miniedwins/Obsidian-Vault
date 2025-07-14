TODO :  
1. 介紹 Control Primitive
2. 說明每個 Control Primitive 特性

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

### 🔍 **1. 為什麼 Controller 會掉包？**

其實不是「Controller 掉包」，而是 **Controller 判斷**「某個封包沒有收到」，進而 **丟棄整個回應訊息（Response Message）**。  

#### ✳️ 原因說明

Resume 時，**Endpoint 會從「上次已發送的封包」之後開始繼續傳送**，  
但假設最後一個封包（例如 packet \#2）**被 Endpoint 傳送了，但 Controller 沒收到**（可能是通訊錯誤），那 Controller 只記得自己「最後收到的是 packet \#1」。

#### ❗ 問題就出在這裡

Resume 之後，Endpoint 會傳送 packet \#3，Controller 卻期望下一包是 packet #2 ⇒ **序號錯誤（out-of-order）⇒ Controller 丟棄整個 Response Message！**

### 🔁 **2. Pause → Resume 為什麼可能會導致封包丟棄？**

不是 Resume 本身導致掉包，而是：

- 如果 Resume **後續封包的序號**不是 Controller 所預期的 ⇒ Controller 丟棄。
    
- 若封包同步出問題 ⇒ 就需要使用 **Replay Control Primitive** 來要求重新傳送特定編號之後的封包。

### ✅ **正確流程（防止封包掉落）**
1. `Pause` 傳送中斷。    

2. 若有疑慮是否收到最後一包，**Controller 在 Resume 前先發送 Replay**：    
    - 告知 Endpoint：**「請從 packet #N 重新開始」**        

3. `Resume` 然後 Endpoint 根據 Replay offset 重新傳送。    

4. 確保封包順序正確，避免 Controller 誤認為掉包。