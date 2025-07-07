MCTP（Management Component Transport Protocol）透過 SMBus 傳送，其通訊格式是基於 **SMBus Block Write** 協定建立的。

**SMBus Format :** 
Address + Command Code + Bye Count * N + Data Byes（MCTP Packet）

**Byte Count：**
- 用來表示 Message Body 不包含 PEC 欄位為止的「實際資料長度」。 
- 範例 : 64 Payload ( Starting with Byte 9 ) + 5 ( Byte 4~8 ) = 69 Bytes

>**Note：**
>1. 根據協議規範 MCTP over SMBus 傳送所使用的 Command code 需要設定為 `0x0F`。 

![[Pasted image 20250702110211.png]]

**MCTP Packet ：** 
Packet = Source Slave Address + MCTP Packet Header + MCTP Message Payload + PEC 

**MCTP Message Payload：** 
Payload = Message Header + Message Data
 ![[Pasted image 20250619113950.png]]