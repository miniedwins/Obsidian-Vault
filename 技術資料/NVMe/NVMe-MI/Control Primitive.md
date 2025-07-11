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