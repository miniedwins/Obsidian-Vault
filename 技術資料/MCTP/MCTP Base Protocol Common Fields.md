## Pkt Seq




## Message Tag 是什麼
- Message Tag 是一個 3-bit 欄位（0~7）
- 搭配 Source EID 和 TO 位元，可唯一識別一筆訊息    
- 同一 Source EID 可以 interleave 多個 messages 給同一個目標
	- 你可以同時傳送多個 message（最多 8 組），每組用不同的 tag 來追蹤
	- 只要這些訊息有不同的 Message Tag
	- 每筆訊息的多個 Packet（SOM ~ EOM）都會標記相同 tag，讓接收端能把封包組回來

### 圖解概念
例如：Host 發送兩個 Request 給同一個裝置（EID=0x20）

|Packet|SOM|EOM|Msg Tag|TO|說明|
|---|---|---|---|---|---|
|1|1|0|1|1|訊息 A 起始|
|2|0|1|1|1|訊息 A 結束|
|3|1|1|2|1|訊息 B 單包|
這兩筆訊息是交錯的傳出，但靠 Message Tag + TO 區分。
然後收到的回應會是：

|Packet|SOM|EOM|Msg Tag|TO|說明|
|---|---|---|---|---|---|
|4|1|1|1|0|Response to 訊息 A|
|5|1|1|2|0|Response to 訊息 B|
