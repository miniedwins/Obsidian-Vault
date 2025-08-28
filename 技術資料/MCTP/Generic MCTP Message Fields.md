Referring to Figure 1, the NVMe Management Messages over MCTP are carried via the MCTP packet payload of one or more MCTP packets.

![[Pasted image 20250619142254.png]]

Medium-specific Header : 
1. 傳輸媒介特定封裝（Transport-Specific）
2. 適應不同物理傳輸層（如 SMBus、PCIe、I2C）的定址與協商需求。

## Maximum message size
The MCTP message body- (including IC bit, Message Type, Message type-specific header fields,
message payload and message integrity check if present) for NVMe Management Messages over MCTP shall be less than or equal to 4224 (4K+128) bytes.

- MCTP 規定最大封包不能超過 4224 (4K+128) bytes
- 
