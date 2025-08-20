一個 NVMe-MI Message Data 可能很大，所以會被拆分成多個 MCTP Packets。MCTP 的 Packet Payload 中裝的是 NVMe-MI Message Body 的一部分（可能包含 Message Header、資料本體的一段、或最後的完整性檢查區）。  

## 每個 MCTP Packet 的組成
1. Physical Medium Specific Header（物理層的 Header， SMBus、PCIe、I²C 等）    
2. MCTP Packet Header（定義這是 MCTP 的第幾個封包、是否是第一包或最後一包）    
	- `SOM`（Start of Message）bit → 標示這包是第一個      
    - `EOM`（End of Message）bit → 標示這包是最後一個 
    - `Seq`（Sequence Number）→ 用來組裝封包順序
3. MCTP Packet Payload（實際承載上層的 Message 部分資料）  
4. Physical Medium Specific Trailer（物理層的結尾部分，例如 SMBus PEC）

## 如何分割 MCTP Message
1. 只有第一個封包的 Payload 開頭會包含 Message Header + Message Data。  
2. 後續封包只是把剩下的 Message Data 切成片段裝進來。    
3. 最後一個封包通常會包含 Message Data + Message Integrity Check。

![[Pasted image 20250813163919.png]]

## 多個封包分割範例
假設 NVMe-MI Message 長度需要 4 個 MCTP 封包：
- Packet #1 → MCTP Header (SOM=1, EOM=0) + NVMe-MI Message Header + 第一段資料    
- Packet #2 → MCTP Header (SOM=0, EOM=0) + 第二段資料    
- Packet #3 → MCTP Header (SOM=0, EOM=0) + 第三段資料    
- Packet #4 → MCTP Header (SOM=0, EOM=1) + 最後一段資料 + MIC