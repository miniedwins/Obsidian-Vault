## MCTP Transport Header

![[Pasted image 20250619142254.png]]

### Header version ( Hdr )
定義 MCTP 可使用的不同媒體類型相對應的介面，這個欄位的值會依據不同的傳輸綁定而有所不同。
如果要傳送的介面是 MCTP over SMBus，則需要將 Header Version 欄位設定為 `0x01`。

![[Pasted image 20250704031027.png]]

### Start Of Message ( SOM )
用來區別是否為第一筆傳遞的封包訊息，設定為 `SOM=1b` 代表是第一筆封包訊息。

### End Of Message ( EOM )
用來區別是否為最後一筆的封包訊息，設定為 `SOM=0b` 代表是最後一筆封包訊息。

### Packet Sequence Number ( Pkt Seq )
用來表示一個 MCTP Message 被拆成多個封包（Packet）傳送。每個封包的順序，用來協助接收端、**辨識順序、重組訊息、偵測遺失封包**。封包順序（0~3，modulo 4）可表達 0~3 編號。

如果一筆 MCTP 訊息被拆成多個封包傳送，那麼封包的 Packet Sequence Number 應該每次遞增（modulo 4），**例如：0 → 1 → 2 → 3 → 0**。因為欄位是 2-bits，最多可追蹤 4 個封包順序，接收端最多可以偵測連續遺失最多 3 個封包。

如果是第一個封包（SOM=1），其實 Sequence Number **可以任意選（0~3 都可以）**，但規範建議還是照順序從前一個訊息的結尾封包遞增（modulo 4），雖然 SOM 封包可隨意設，但建議用上一封訊息最後一包（EOM=1）的 Pkt Seq # 加一（mod 4），這樣有助於串接後續訊息流的連貫性。

**範例說明1 : 一筆 MCTP 訊息被分成 3 個封包，SOM=1, EOM=1 放在頭尾：**

| Packet | SOM (Start of Msg) | EOM (End of Msg) | Pkt Seq # |
| ------ | ------------------ | ---------------- | --------- |
| 1      | 1（起始封包）            | 0                | 0         |
| 2      | 0                  | 0                | 1         |
| 3      | 0                  | 1 （結尾封包）         | 2         |
> 下一筆訊息建議從 Seq # 3 開始。

| Packet | SOM (Start of Msg) | EOM (End of Msg) | Pkt Seq # |
| ------ | ------------------ | ---------------- | --------- |
| 4      | 1（起始封包）            | 0                | 3         |
| 5      | 0                  | 0                | 0         |
| 6      | 0                  | 1（結尾封包）          | 1         |

**範例說明2 : 一筆 MCTP 訊息跨 5 個封包傳送：**

| Packet | SOM (Start of Msg) | EOM (End of Msg) | Pkt Seq #      |
| ------ | ------------------ | ---------------- | -------------- |
| 1      | 1 （起始封包）           | 0                | 0              |
| 2      | 0                  | 0                | 1              |
| 3      | 0                  | 0                | 2              |
| 4      | 0                  | 0                | 3              |
| 5      | 0                  | 1 （結尾封包）         | 0 （mod 4 循環回來） |
### Source Slave address 
Source Slave address 之中的最低位元 LSB，是為了區別使用哪一種協定的封包。

設定說明 : 
1. IPMI over SMBus/I2C  規範要求最小有效位元（LSB）為 `0b` 
2. MCTP over SMBus 規範要求 LSB 為 `1b`

注意事項 : 
屬於 MCTP 欄位，並非 SMBus 協定。

### Tag Owner ( TO )
用來表示：「這個訊息的 Message Tag 是由哪一方產生的？這樣可以讓雙方知道，這是哪一筆 Request 的回應，也能避免不同方向的 Tag 衝突。

- 發起端 Request（請求）會建立一個 Tag 值，例如 Msg Tag = 0，並設定 TO = 1
- 目的端 Response（回應）回應時會使用同一個 Msg Tag =0，並設定 TO = 0

**範例說明：假設 A 是發起端、B 是回應端。**

| Packet | SOM | EOM | Msg Tag | TO  | 備註                   |
| ------ | --- | --- | ------- | --- | -------------------- |
| 1      | 1   | 1   | 0       | 1   | A 發送 Request，建立 tag  |
| 2      | 1   | 1   | 0       | 0   | B 回應 Response，回用 tag |
|        |     |     |         |     |                      |
>訊息 1 和 訊息 2 的 Msg Tag 相同，但 TO 不同，可區分 Request vs Response。

### Message Tag
1.  Message Tag 是一個 3-bit 欄位（0~7）
2. 搭配 Source EID 和 TO 位元，可唯一識別一筆訊息    
3. 同一 Source EID 可以 interleave 多個 messages 給同一個目標
	- 你可以同時傳送多個 message（最多 8 組），每組用不同的 tag 來追蹤
	- 只要這些訊息有不同的 Message Tag
	- 每筆訊息的多個 Packet（SOM ~ EOM）都會標記相同 tag，讓接收端能把封包組回來

**範例說明：Host 發送兩個 Request 給同一個裝置（EID=0x20）**

| Packet | SOM | EOM | Msg Tag | TO  | 說明      |
| ------ | --- | --- | ------- | --- | ------- |
| 1      | 1   | 0   | 1       | 1   | 訊息 A 起始 |
| 2      | 0   | 1   | 1       | 1   | 訊息 A 結束 |
| 3      | 1   | 1   | 2       | 1   | 訊息 B 單包 |
這兩筆訊息是交錯的傳出，但靠 Message Tag + TO 區分。
然後收到的回應會是：

| Packet | SOM | EOM | Msg Tag | TO  | 說明               |
| ------ | --- | --- | ------- | --- | ---------------- |
| 4      | 1   | 1   | 1       | 0   | Response to 訊息 A |
| 5      | 1   | 1   | 2       | 0   | Response to 訊息 B |

## MCTP Message body
### Integrity Check Bit ( IC )
1. 用來指出這筆 MCTP 封包是否包含額外的完整性檢查機制。
2. 出現在第一個 packet 的 message body 開頭第一個 byte ( Message Type )
