
### ETC-10 Invalid Invoking ID - Get

#### CASE 1 : 測試情境說明 
1. 此測試是要驗證調用無效的 Invalid Invoking ID。
2. 該測試所調用的是 Get Method。

#### 期望結果
回傳 NOT_AUTHORIZED。

#### 測試行為
1. 調用無效的 Invoking UID : 00 00 08 01 AA BB CC DDh ( UNKNOWN )
2. 調用有效的 Method UID : 00 00 00 06 00 00 00 17h ( Set )

![[Pasted image 20250519141449.png]]



---
### ETC-11 Invalid Invoking ID – Non-Get
#### 測試情境說明
1. 此測試是要驗證調用無效的 Invalid Invoking ID。
2. 該測試所調用的是 Set Method。

#### 期望結果
回傳 NOT_AUTHORIZED。

#### 測試行為
1. 調用無效的 Invoking UID : 00 00 08 01 00 00 00 05h ( UNKNOWN )
2. 調用有效的 Method UID : 00 00 00 06 00 00 00 17h ( Set )

備註 : 官方測試案例所調用的是無效的 UID of 00 00 08 01 00 00 00 05。

![[Pasted image 20250407092200.png]]

返回執行結果 NOT_AUTHORIZED。

![[Pasted image 20250407092621.png]]

---
### ETC-13 Malformed ComPacket Header Regular Session
#### 測試情境說明
此測試是要驗證 **ComPacket 的長度超過 `MaxComPacketSize-20`** 時，TPer 的處理行為是否正確。

#### 期望結果
回傳 no further data。

#### 參數說明
MaxComPacketSize = 10B8h
MaxPacketSize = 10A6h
Data Pay Load = 10A6h - 20Bytes ( ComPacket Header )

#### 測試行為
- 不太清楚為什要用 MaxComPacketSize - 20 作為 Data Pay Load。
- ComPacket 封包會因為 Payload 大小而最終導致超過 MaxComPacket Size，符合測試案例。

![[Pasted image 20250407073546.png]]

---
### ETC-14 Exceed TPer Properties Regular Session
#### 測試情境說明
此測試是要模擬主機端發送 MaxSubPackets + 1 時，也就是 Packet 帶有多個 SubPacket。

#### 期望結果
回傳 no further data。

#### 參數說明
MaxSubPackets :  TPer 宣告的最大可接受封包數量。

#### 測試行為
1. 寫入資料到 Data Store Table
2. 發送多個 Subpacket 封包 ( Subpacket 1  +Subpacket 2 )

![[Pasted image 20250407062258.png]]

---
