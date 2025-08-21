以下是 NVMe-MI 標準回傳格式，不同的 Message Type 有不同的 Response Message。 若是使用 in-band tunneling，回傳會是 CQE Mapping to NVMe-MI Response Format。

![[Pasted image 20250821160710.png]]

> Note : 
> 1. in-band tunneling : CSI = 0
> 2. out-of-band : CSI = 1

## NVMe Admin Response Message Format
- Completion Queue Entry Dword 2 : `Reserved`
- Completion Queue Entry Dword 3 :
	- Command ID field : shall be cleared to `0h`
	- Status : Status Code ( Mapping to DW3 Status )

![[Pasted image 20250821164838.png]]

![[Pasted image 20250821165027.png]]

這是一個執行 Identify Controller 所回傳的範例 : 
- DW3 Status : `0x00` 
- Response Data : `AZ123456`（Serial Number）
- CRC32 : `7BC41F7A`
- PEC : `48h`

![[Pasted image 20250821165500.png]]

## NVMe-MI Command Response Message Format