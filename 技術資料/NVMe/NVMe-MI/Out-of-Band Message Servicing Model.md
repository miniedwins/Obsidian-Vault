
## Command Slot 機制

| 項目      | 說明                                                |
| ------- | ------------------------------------------------- |
| Slot 數量 | 每個 Endpoint 有 **2 個 Command Slots**               |
| 組裝行為    | 對每個 Command Slot，Endpoint 會獨立組裝 MCTP 封包為完整命令      |
| 執行流程    | Command Message 組裝完成 → 處理 → 回傳 Response → 清除 Slot |
| 限制      | 同一個 Slot 在 **完成前不可接受第二個命令**                       |
| Msg Tag | 用來區分封包，但同一條命令的封包需保持一致（同一 Msg Tag）                 |
| 並行能力    | 一個 Endpoint 最多同時處理 2 條命令；N 個 Endpoint 可並行 2N 條命令  |
### 範例說明（單 Slot）

假設目前正在使用 Command Slot 0，Controller 傳送以下 3 個封包：

| Packet | SOM | EOM | Msg Tag | TO  | Payload | 屬於哪個 Slot |
| ------ | --- | --- | ------- | --- | ------- | --------- |
| 1      | 1   | 0   | 0       | 1   | ...     | Slot 0    |
| 2      | 0   | 0   | 0       | 1   | ...     | Slot 0    |
| 3      | 0   | 1   | 0       | 1   | ...     | Slot 0    |
這 3 個封包是 **同一條 Command Message**，由 SOM 開始、EOM 結束、Msg Tag 一致 → 屬於同一 Slot。

在這個命令還沒回應完成前，**不可以用 Slot 0 傳送另一條命令**，即使換 Msg Tag 也不行。

### 延伸範例（同時使用 2 Slot）

✔ Slot 0 和 Slot 1 可以同時處理不同的 Command Message（互不干擾）

| Packet  | Msg Tag | Target Slot | 狀態         |
| ------- | ------- | ----------- | ---------- |
| A-1~A-n | 0       | Slot 0      | 正在傳送中      |
| B-1~B-n | 1       | Slot 1      | 可同時傳送第二條命令 |
|         |         |             |            |
## Command Servicing State Diagram

![[Pasted image 20250711141407.png]]

### 狀態：Idle
#### 1. 狀態說明
- 預設初始狀態（例如裝置 Reset 之後） 
- 沒有任何命令在處理中，Command Slot 處於空閒狀態
#### 2. 轉移條件（轉入下一狀態）
- 收到一個新的 MCTP 封包，且該封包：
    - SOM = 1（封包起始）        
    - Message Type = 0x4（Command Message） → 進入 `Receive` 狀態
#### 3. 發生問題時的處理
- 無特殊錯誤處理，Idle 是穩定狀態
- 如果從 Transmit 回到 Idle，表示一輪完整流程已完成或中止
---
### 狀態：Receive
#### 1. 狀態說明
- 收到 Command Message 的第一個封包（SOM=1），開始組裝多封包命令   
- 檢查封包完整性
	1. 順序 ( Pkg Seq )
	2. 長度 ( Payload Size )
	3. 資料完整度 ( Integrity Check )
#### 2. 轉移條件（轉入下一狀態）
- 如果完整收到且驗證成功 → 進入 `Process` 狀態（準備處理命令）   
- 上層通知中止命令 Abort Control Primitive 控制訊號 → `Idle`（中止流程）
#### 3. 發生問題時的處理
- 收到錯誤時會「中止組裝」
- 檢查到封包錯誤（如亂序、完整性錯誤）
---
### 狀態：Process
#### 1. 狀態說明：
- 組裝完成後，進入命令處理階段    
- 執行 Command Message 中的指令，例如查詢資訊、改變狀態等
#### 2. 轉移條件（轉入下一狀態）
- 命令執行完成或是處理未完成但時間已到（Timeout） ，需要傳送回應訊息 → 進入 `Transmit`
- 處理命令未完成或是沒有 Primitive Pause，則會進入→ `Transmit` 發送 "More Processing Required"  → 然後再返回 `Process`
- 上層通知中止命令 Abort Control Primitive 控制訊號 → `Idle`（中止流程）
#### 3. 發生問題時的處理：
- 若解析或執行指令中發現邏輯錯誤 → 進入 `Transmit` 回應錯誤碼 
---
### 狀態：Transmit
#### 1. 狀態內容
- 傳送 Response Message 回覆 Management Controller
- Response Message 可能是成功結果、錯誤代碼，或 "More Processing Required"
#### 2. 轉移條件（轉入下一狀態）
- Response Message 全部傳完 → 進入 `Idle`
-  上層通知中止命令 Abort Control Primitive 控制訊號 → `Idle`（中止流程）
#### 3. 發生問題時的處理
- 若傳送中失敗或超時，可回報錯誤後中止命令

### 狀態轉移總結表
| 狀態       | 行為說明           | 可轉移到              | 發生錯誤後處理           |
| -------- | -------------- | ----------------- | ----------------- |
| Idle     | 空閒，等待新指令       | → Receive         | 無，為穩定初始狀態         |
| Receive  | 組裝封包、檢查格式      | → Process / Idle  | 檢查錯誤、Abort → Idle |
| Process  | 執行命令、驗證合法性     | → Transmit / Idle | Abort → Idle      |
| Transmit | 傳送回應、或要求更多時間處理 | → Idle / Process  | 傳送失敗後回 Idle       |
|          |                |                   |                   |
### 注意事項
( 原文 ) : The behavior of receiving two or more overlapping Command Messages to the same Command Slot is undefined. If this results in the Management Endpoint discarding a Command Message, then this is considered receiving a Command Message to a non-Idle Command Slot (CMNICS)

( 說明 ) :  若 Controller 傳送兩條重疊的命令（相同 Slot 未完成又重送新命令）， Endpoint 應丟棄第二條命令，並且回傳 Command Message to non-Idle Command Slot (CMNICS)。回傳的 Response Message 會是 Control Primitive Success Response Fields。