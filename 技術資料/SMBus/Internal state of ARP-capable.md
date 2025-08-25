
**ARP-capable Devices** 在上電重置 (POR) 後的行為差異。

![[Pasted image 20250825104428.png]]

## 1. PTA (Persistent Target Address)
- **AR Flag** : `CLEAR`    
- **AV Flag** : 從 NVR (非揮發性記憶體) 讀取    
- **SMBus Address** : 從 NVR 讀取（如果 AV Flag = CLEAR，則為未定義）    
- **UDID** : 不變 (NO CHANGE)  
- **重點**：PTA 會保留上次分配的 SMBus 地址，除非 AV Flag 清除。適合需要跨電源循環保存地址的裝置。

## 2. Non-PTA / Non-Random Number
- **AR Flag** : `CLEAR`    
- **AV Flag** : `CLEAR`    
- **SMBus Address**: 未定義    
- **UDID** : 不變 (NO CHANGE)  
- **重點**：不支援 PTA 的裝置，上電後地址會丟失，必須重新透過 ARP 分配新地址。

## 3. Non-PTA / Random Number
- **AR Flag** : `CLEAR`    
- **AV Flag** : `CLEAR`    
- **SMBus Address** : 未定義    
- **UDID** : **會生成一個新的隨機號碼**  
- **重點**：每次上電都會有一個新的 Random Number，用於避免地址衝突（增加唯一性），但還是需要重新 ARP 分配。

## 4. DTA (Default Target Address)
- **AR Flag** : `CLEAR`    
- **AV Flag** : `SET`    
- **SMBus Address** : 預設地址（Default Target Address, 從 ROM 讀出，通常是 `0x61h`）    
- **UDID** : 不變 (NO CHANGE)  
- **重點**：開機就固定在 DTA，不需要保存，也不會丟失；通常是最簡單的 ARP-capable 裝置。