
- Use 7-bit addressing
	- Standard-mode fast-mode (400 kHz)
	- Fast-mode Plus (1MHz) I2C buses 



### 主機如何知道設備是否支援 MCTP 封包?
1. 發送 GET UDID 命令取得 UDID
2. 查詢 Interface 其中的 Bit 5