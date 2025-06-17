Packet Error Code (PEC) 是用來做檢驗傳遞的封包是否有錯誤，針對每個寫入或是讀取資料傳輸後，透過 (CRC-8) 計算出所有資料的校驗碼，最後在傳輸的結尾加入 PEC。

當收到的資料的 `Master` 或是 `Slave` 可以透過校驗碼確認資料是否有錯誤，若是傳遞的資料有錯誤則需要重新再發送。

- 傳遞 PEC 前確認事項 : 
  - `Master` 控制端在傳送 PEC 之前，需要確認 `Slave` 目標端是否有支援 PEC。
  - `Slave` 目標端在收到資料後，必須要檢查是否需要回傳 with PEC 或是 Without PEC 給控制端。

- 計算 PEC 不包含以下位元 : 
  - ACK
  - NACK
  - START
  - STOP
  - REPEATED START

> 以下圖示簡易說明 PEC 所傳遞的位置。

1. `Master` 傳送資料給 `Slave`，資料傳輸完畢後加入 `PEC` 校驗碼

// TODO : Capture Send byte protocol with PEC

2. `Master` 收到來自 `Slave` 回傳的資料，資料傳輸完畢後加入 `PEC` 校驗碼

// TODO : Capture Receive byte protocol with PEC


## Packet Error Checking
The Packet Error Checking mechanism improves reliability and communication robustness. Implementation of Packet Error Checking by SMBus devices is optional for SMBus devices but is required for devices participating in and only during the ARP process. SMBus devices that implement Packet Error Checking must be capable to communicate with the controller and other devices that do not implement the Packet Error Checking mechanism.

Packet Error Checking, whenever applicable, is implemented by appending a Packet Error Code (PEC) at the end of each message transfer. Each protocol (except for Quick Command and the SMBus Host Notify protocol described Section 6.5.9) has two variants: one with the Packet Error Code (PEC) byte and one without. The PEC is a CRC-8 error-checking byte, calculated on all the message bytes (including addresses and read/write bits). The PEC is appended to the message by the device that supplied the last data byte.

## Packet error checking implementation
The SMBus must accommodate any mixture of devices that support Packet Error Checking and devices that do not. A device that acts as a target and supports the PEC must always be prepared to perform the target transfer with or without a PEC, verify the correctness of the PEC if present, and only process the message if the PEC is correct. Implementations are encouraged to issue a NACK if the PEC is present but not correct.

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