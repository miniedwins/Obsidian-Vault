
---
### ETC-13 Malformed ComPacket Header Regular Session
#### 測試目的
驗證傳送 ComPacket 封包超過最大所支援的長度 MaxComPacketSize。

#### 期望結果
回傳 no further data。

#### 測試說明

#### 測試行為

---
### ETC-14 Exceed TPer Properties Regular Session
#### 測試目的
驗證 MaxSubPackets + 1 ( 當前 TPer MaxSubPackets=1)。

#### 期望結果
回傳 no further data。

#### 測試說明
1. Host 調用 Properties Method，取得 MaxSubPackets
2. 主機發送多個 MaxSubPackets + 1
	- ComPacket = Packet + Subpacket 1 + Subpacket 2
3. 確認回傳結果狀態

#### 測試行為
1. 寫入資料到 Data Store Table
2. 發送多個 Subpacket 封包 ( Subpacket 1  +Subpacket 2 )
![[Pasted image 20250407062258.png]]

---
