### Response Message 與傳輸方式
- 不同 NVMe-MI Message Type → 有不同的 Response Message 格式。
- in-band tunneling  → 回傳 CQE Mapping to NVMe-MI Response Format。

![[Pasted image 20250821160710.png]]

## NVMe Admin Response Message Format
### Mapping To Completion Queue Entry
- Dword 0/1 : 對應到 CQE DW0/1
- Dword 2：Reserved   
- Dword 3 : 對應到 CQE DW3
    - Command ID field：必須清除為 `0h`        
    - Status field：用於回傳 Status Code

![[Pasted image 20250821164838.png]]

![[Pasted image 20250821165027.png]]

這是一個執行 Identify Controller 所回傳的範例 : 
- DW3 : `0x00` 
- Response Data : `AZ123456`（Serial Number）
- CRC32 : `7BC41F7A`
- PEC : `48h`

![[Pasted image 20250821165500.png]]

## NVMe-MI Command Response Message Format