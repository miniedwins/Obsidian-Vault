## 概要說明
Packet Error Code (PEC) 是用來做檢驗傳遞的封包是否有錯誤，針對每個寫入或是讀取資料傳輸後，透過 (CRC-8) 計算出所有資料的校驗碼，最後在傳輸的結尾加入 PEC。

當收到的資料的 `Master` 或是 `Slave` 可以透過校驗碼確認資料是否有錯誤，若是傳遞的資料有錯誤則需要重新再發送。

## 傳遞 PEC 前確認事項
1.  `Master` 控制端在傳送 PEC 之前，需要確認 `Slave` 目標端是否有支援 PEC。
2. `Slave` 目標端在收到資料後，必須要檢查是否需要回傳 with PEC 或是 Without PEC 給控制端。

- 計算 PEC 不包含以下位元 : 
  - ACK
  - NACK
  - START
  - STOP
  - REPEATED START

## 行為規範
- **Target 端（Slave）如果支援 PEC**：   
    - 必須能處理 **有 PEC** 和 **無 PEC** 的傳輸。
    - 如果有 PEC，就驗證其正確性。        
    - PEC 錯誤 → 建議回覆 **NACK**，讓 Controller 知道資料損毀。
        
- **Controller 端（Master）**：    
    - 可選擇送出 PEC 或不送。        
    - 但在 **ARP 流程**，一定要送 PEC。

## ACK/NACK 與 PEC 並不構成絕對保證

### 1. ACK ≠ 確認資料正確
- 即使有 ACK，也**不能保證 PEC 正確或資料寫入成功**。

### 2. NACK 代表目標設備可能偵測錯誤
- 如果你發送資料 + PEC，然後收到 **NACK**：   
    - 代表目標設備可能在 link layer 就偵測到了錯誤（如 PEC 不正確）       
    - 因此它有機會即時送出 NACK

###  3. ACK 的限制
- 如果你發送資料 + PEC，然後收到 **ACK**：   
    - 只能表示：目標設備的 link 層「沒有發現錯誤」
    - 但它不一定來得及做 PEC 驗證（即有可能是錯誤但來不及 NACK）

### 4. 建議使用：Write 後 Read 回來 + PEC 驗證
- 如果你要保證寫入真的成功、資料正確：
    - 發送 write 命令（加 PEC）        
    - 再用 read + PEC 回讀該值
    - 比對 PEC 是否正確，若 OK → 資料可被信任