MCTP（Management Component Transport Protocol）透過 SMBus 傳送，其通訊格式是基於 **SMBus Block Write** 協定建立的。

公式 = Address + Command Code + Bye Count * N + Data Byes（MCTP Packet）

![[Pasted image 20250702110211.png]]

- MCTP Packet = Source Slave Address +  Packet Header + Message Payload + PEC 
- MCTP Message Payload = Message Header + Message Data
 ![[Pasted image 20250619113950.png]]