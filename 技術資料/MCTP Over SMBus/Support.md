
### MCTP Over SMBus 支援速度模式
1. 7-bit addressing
	- Standard-mode fast-mode (400 kHz)
	- Fast-mode Plus (1MHz) I2C buses 

> 備註 : 不支援 10-bit addressing

### 主機如何知道設備是否支援 MCTP Over SMBus
1. 發送 SMBus GET UDID 命令取得 Unique Device Identifier (UDID)
2. 查詢 Interface field bit fields description 其中的 Bit 5 代表 `ASF`

### 如何取得 SMBus Version
1. 發送 SMBus GET UDID 命令取得 Unique Device Identifier (UDID)
2. 查詢 Interface field bit fields description 其中的 Bit 0-3 代表 `SMBusVersion`

### 設備如何判斷是 MCTP 封包
1. MCTP Header 找到 Source Slave Address
2. 取得最低位元 ( LSB )， LSB 為 `1` 表示 MCTP over SMBus