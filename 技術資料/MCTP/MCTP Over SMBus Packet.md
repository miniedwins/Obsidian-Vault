All MCTP transactions are based on the SMBus **Block Write Bus Protocol**.

## 封包組成結構
MCTP = SMBus Header + MCTP Message Payload ( Data Byes * N ) + PEC
SMBus Header = DEST Slave + Command Code + Bytes Count + Bytes Data
Bytes Data = Source Slave Address + MCTP Message Payload

1. All MCTP over SMBus messages use a command code of `0x0F`.
2. Source Slave address : This bit shall be set to `1b`. The value enables MCTP to be differentiated from IPMI over SMBus and IPMB (IPMI over I2C) protocols.
 ![[Pasted image 20250619113950.png]]
A Block Read or Block Write is allowed to transfer a maximum of `255` data bytes.

![[Pasted image 20250619114132.png]]
