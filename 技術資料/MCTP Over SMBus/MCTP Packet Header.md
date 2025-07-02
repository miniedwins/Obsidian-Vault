
## Pkt Seq

## Command Code
1. 所有 MCTP over SMBus 傳送所使用的 Command code = `0x0F`。

## Byte Count
1. 從 Byte Count 欄位之後開始，不包含 PEC 欄位為止的「實際資料長度」。
2. 範例說明：Byte Count = 64 Payload ( Starting with Byte 9 ) + 5 ( Byte 4~8 ) = 69 Bytes

## Source Slave address 
1. 屬於 MCTP 欄位，並非 SMBus 協定
2. Bit0  : This bit shall be set to `1b`. 
3. Reason : The value enables MCTP to be differentiated from IPMI over SMBus and IPMB (IPMI over I2C) protocols. ***(尚未了解原因)***

## PEC ( Packet error code )
1. 所有 MCTP 傳送應該都要包含 PEC byte

## Message Tag 是什麼
1.  Message Tag 是一個 3-bit 欄位（0~7）
2. 搭配 Source EID 和 TO 位元，可唯一識別一筆訊息    
3. 同一 Source EID 可以 interleave 多個 messages 給同一個目標
	- 你可以同時傳送多個 message（最多 8 組），每組用不同的 tag 來追蹤
	- 只要這些訊息有不同的 Message Tag
	- 每筆訊息的多個 Packet（SOM ~ EOM）都會標記相同 tag，讓接收端能把封包組回來

例如：Host 發送兩個 Request 給同一個裝置（EID=0x20）

| Packet | SOM | EOM | Msg Tag | TO  | 說明      |
| ------ | --- | --- | ------- | --- | ------- |
| 1      | 1   | 0   | 1       | 1   | 訊息 A 起始 |
| 2      | 0   | 1   | 1       | 1   | 訊息 A 結束 |
| 3      | 1   | 1   | 2       | 1   | 訊息 B 單包 |
這兩筆訊息是交錯的傳出，但靠 Message Tag + TO 區分。
然後收到的回應會是：

|Packet|SOM|EOM|Msg Tag|TO|說明|
|---|---|---|---|---|---|
|4|1|1|1|0|Response to 訊息 A|
|5|1|1|2|0|Response to 訊息 B|

