All MCTP transactions are based on the SMBus [[Block Write Bus]] Protocol.

## 封包組成結構
- **MCTP Packet** = SMBus Header + MCTP Header and Payload ( Data Byes * N ) + PEC
- **SMBus Header** = DEST Slave + Command Code + Bytes Count + Data Bytes
- **Data Bytes** = Source Slave Address + MCTP Message Payload
- **MCTP Message Payload** = Message Header + Message Data
 ![[Pasted image 20250619113950.png]]
