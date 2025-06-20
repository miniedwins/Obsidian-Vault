All MCTP transactions are based on the SMBus [[Block Write Bus]] Protocol.

## 封包組成結構
- **MCTP** = SMBus Header + MCTP Message Payload ( Data Byes * N ) + PEC
- **SMBus Header** = DEST Slave + Command Code + Bytes Count + Data Bytes
- **Data Bytes** = Source Slave Address + MCTP Message Payload
 ![[Pasted image 20250619113950.png]]
## 欄位注意事項
- Source Slave Address 是 MCTP 欄位，不屬於 SMBus 協定 
- All MCTP over SMBus messages use a command code of `0x0F`
- Source Slave address :
	- Bit0  : This bit shall be set to `1b`. 
	- Reason : The value enables MCTP to be differentiated from IPMI over SMBus and IPMB (IPMI over I2C) protocols. ***(尚未了解原因)***

