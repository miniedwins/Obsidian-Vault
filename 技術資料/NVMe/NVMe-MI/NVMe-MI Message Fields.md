
![[Pasted image 20250620171239.png]]

## Message Type
MCTP 封包的 Message Type 必須設定為 `0x04`，表示這是一個 NVMe-MI over MCTP Message。

## Integrity Check field ( IC )
- All NVMe-MI Messages in the **in-band tunneling mechanism** shall not be protected by a CRC and thus this bit shall be cleared to `0` in all in-band NVMe-MI Messages.

- All NVMe-MI Messages in the **out-of-band mechanism** shall be protected by a CRC and thus this bit shall be set to `1` in all out-of-band NVMe-MI Messages.

## Request or Response ( ROR )
用來標示該 NVMe-MI Message 是 Request 還是 Response。
- ROR = `0` → Request Message (主機送出的命令)。    
- ROR = `1` → Response Message (控制器對 Request 的回應)。

## Command Slot Identifier ( CSI )
- 定義：CSI 是 Command Slot 的識別碼，用於區分不同命令。    
- 用途：確保 Request ↔ Response 一一對應。        
- 分配方式：一個 Command Slot 同一時間只能被一個命令佔用。        
- 回收機制：管理端收到對應的 Response 後，CSI Slot 才能釋放並重複使用。

## NVMe-MI Message Type
在 NVMe-MI (Management Interface) 中，所有管理端 (Management Controller) 與受管端 (Management Endpoint) 的互動，都是透過 Message (訊息) 完成的。  

這些訊息的類型會標記在 Message Type 欄位，用來區分傳送內容屬於哪一種。

![[Pasted image 20250710153234.png]]


