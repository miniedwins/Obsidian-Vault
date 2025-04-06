
---
### ETC-13 Malformed ComPacket Header Regular Session
#### 測試情境說明
此測試是要驗證 **ComPacket 的長度超過 `MaxComPacketSize-20`** 時，TPer 的處理行為是否正確。

#### 期望結果
回傳 no further data。

#### 測試行為

---
### ETC-14 Exceed TPer Properties Regular Session
#### 測試情境說明
此測試是要驗證當主機端發送 MaxSubPackets + 1 時，TPer 的處理行為是否正確。
1. MaxSubPackets :  TPer 宣告的最大可接受封包數量。
2. MaxSubPackets 規範上定義為 `1`。

#### 期望結果
回傳 no further data。

#### 測試行為
1. 寫入資料到 Data Store Table
2. 發送多個 Subpacket 封包 ( Subpacket 1  +Subpacket 2 )
![[Pasted image 20250407062258.png]]

---
