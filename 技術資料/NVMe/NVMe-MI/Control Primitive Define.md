## 定義
Control Primitive 的重點在於，它並不是用來「傳資料」，而是用來「控制命令服務執行狀態」（Command Servicing State Diagram）。也因為它是即時控制訊息，所以通常會優先處理，確保管理端可以精準地調整端點的回應節奏與資料傳輸狀態。

## 運作功能
當管理控制器（Management Controller）需要對端點（Management Endpoint）下達某種即時控制時，就會送出一個 Control Primitive 訊息。該訊息會放在 NVMe-MI Message Fields 欄位中的 NVMe-MI Message Type 來表示傳遞的訊息是 Control Primitive Message。

當端點（Management Endpoint）收到 Control Primitive Request 訊息後，會立即針對控制要求做動作，並以一個對應的 Control Primitive Response（例如 : Pause Control Primitive Response）回送給發送端，以確認指令執行的狀態。

> Note :
> - ✅ 可用於 Out-of-Band
> - ❌ 禁止使用於 In-Band Tunneling

## 發送與回應特性
1. **Command Slot 的互動**
	- Control Primitive 可以直接針對特定 Command Slot 發送，不受該 Slot 當前狀態的限制。
	- 無論該 Command Slot 正處於哪一種命令服務狀態，這類訊息都會被立即處理。

2. **不需等待回應即可連續發送**  
	- Control Primitive 可以在上一筆尚未回覆時繼續發送下一筆，不過前一筆會被覆蓋不執行。
    
3. **只有最後一筆保證被處理**  
	若連續送出多筆 Control Primitive 而未等待回應，只有最後送出的那一筆保證會被處理並回覆，其餘的可能會被忽略（discarded），而且不會有 Response 傳回。
    
4. **不會破壞前一筆狀態**  
    即使多筆 Control Primitive 中有部分被後送的覆蓋掉，這些操作也不會損壞先前已生效的狀態。    
5. **Request & Response TAG（請求回應識別）**　
	Management Controller 透過 TAG 將 Control Primitive Request 與 Response 對應。TAG 由 Controller 指定，設備回傳的 Response 必須使用相同 TAG 以識別執行完成的回覆命令。

## 情境範例說明

### 情境一：三筆 Primitive 是依序進入，前一筆還沒處理完就來新的

| 時間  | 動作                 | 狀態                            |
| --- | ------------------ | ----------------------------- |
| T0  | Primitive A        | Slot idle → 收到 A、準備處理         |
| T1  | Primitive B        | 還沒處理完 A，B 到 → 蓋掉 A（discard A） |
| T2  | Primitive C        | 還沒處理 B，C 到 → 蓋掉 B（discard B）  |
| T3  | 處理 C，傳回 Response C |                               |

### 情境二：Primitive A 已經開始處理（Process 中），B 和 C 進來得太快

| 時間  | 動作                            | 狀態                             |
| --- | ----------------------------- | ------------------------------ |
| T0  | Primitive A                   | Slot idle → 收到 A、進入處理          |
| T1  | Primitive B                   | 收到，但 A 還沒回，B 覆蓋 A（依據 spec 可覆蓋） |
| T2  | Primitive C                   | 覆蓋 B                           |
| T3  | 處理結束（其實是處理 C） → 傳回 Response C |                                |

