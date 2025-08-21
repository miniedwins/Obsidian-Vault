### Response Message 與傳輸方式
根據不同 NVMe-MI Message Type → 有不同的 Response Message 格式。

![[Pasted image 20250821160710.png]]

## NVMe Admin Response Message Format
- Dword 0/1 : 對應到 CQE DW0/1
- Dword 2：Reserved   
- Dword 3 : 對應到 CQE DW3
    - Command ID field：必須清除為 `0h`        
    - Status field：用於回傳 Status Code

![[Pasted image 20250821164838.png]]

![[Pasted image 20250821165027.png]]

- Identify Controller
	- DW3 : `0x00` 
	- Response Data : `AZ123456`（Serial Number）
	- Message Integrity Check : `0x7BC41F7A` ( 後面是空白字元 )
	- PEC : `48h`

![[Pasted image 20250821165500.png]]

## NVMe-MI Command Response Message Format

![[Pasted image 20250822025808.png]]

- NVM Subsystem Health Status Poll
	- Status Field : `00h`
	- NVMe Management Response : `Rsvd`
	- Response Data : Subsystem Management Data Structure
	- MIC : `0x573B3BC8h`

![[Pasted image 20250822030059.png]]

## Control Primitive Response Format

![[Pasted image 20250822031803.png]]

- Replay Control Primitive
	- Status Field : `00h`
	- TAG : `45h`
	- CPSR : `0x0001` ( 表示會重新再發送 Response Message )
	- MIC : `0x830286BDh`

![[Pasted image 20250822032014.png]]

由於管理端發送 Replay Control Primitive，Management Endpoint 表示會再發送先前的 Response Message，因此管理端還會接收到第二個 Response Message。