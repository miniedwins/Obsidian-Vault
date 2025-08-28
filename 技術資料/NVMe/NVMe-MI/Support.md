
1. MCTP Support Discovery
2. ARP Capable and Get UDID
3. UDID ASF Bit5 = 1

Once support for ASF has been indicated, an MCTP control message (for example, Get MCTP Version Support) can be issued to the device to determine whether it supports MCTP.

### MCTP Over SMBus 支援速度模式
1. 支援 7-bit addressing
	- Standard-mode 
	- Fast-mode ( 400 kHz )
	- Fast-mode Plus ( 1MHz )
2. 不支援 10-bit addressing

### 主機如何知道設備是否支援 MCTP Over SMBus
1. 發送 SMBus GET UDID 命令取得 Unique Device Identifier ( UDID )
2. 查詢 UDID Interface field bit fields description 其中的 **Bit 5** ( ASF=`0x0F` ) 

### 如何取得 SMBus Version
1. 發送 SMBus GET UDID 命令取得 Unique Device Identifier ( UDID )
2. 查詢 UDID Interface field bit fields description 其中的 **Bit 3:0** 代表 `SMBusVersion`

- SMBus Version : 
	- 0000b : SMBus 1.0 – do not use in ARPable devices
	- 0001b  : SMBus 1.1– do not use in ARPable devices
	- 0100b SMBus Version 2.0
	- 0101b SMBus Version 3.0
	- 0110b SMBus Version 3.1
	- 0111b SMBus Version 3.2

### 設備如何判斷是 MCTP 封包
1. MCTP Header 找到 Source Slave Address
2. 取得最低位元 ( LSB )， LSB 為 `1` 表示 MCTP over SMBus