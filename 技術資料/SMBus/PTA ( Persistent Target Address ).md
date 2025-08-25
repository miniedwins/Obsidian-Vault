在 SMBus ARP 機制中，ARP Controller 會給 ARP-capable device 分配一個唯一的 SMBus 地址。  
但有些裝置支援  PTA ( Persistent Target Address )，意思是：

- 裝置在被分配新地址後，可以把這個地址永久記憶下來（例如寫入內部 NVM 或 EEPROM）。    
- 即使 **斷電 / 重開機 / 熱插拔**，裝置仍會保留並使用這個地址，而不是回到「ARP 廣播預設地址」   
- 這樣可以避免系統每次上電都要重新進行 ARP 流程，加快初始化速度。

## PTA 的功能
- **保留地址**：被 ARP Controller 分配的地址可以跨電源循環持久存在。    
- **避免重複分配**：下次上電後，裝置可以直接用既有地址運作，無需重新走 ARP 流程。    
- **提高效率**：省略頻繁的 ARP 指令交換，縮短系統啟動時間。    
- **相容性**：若系統偵測到地址衝突，仍可重新觸發 ARP 流程並更新 Persistent Address。

## 若不支援 PTA
- 裝置在斷電或重啟後，會忘記上一次分配的地址。    
- 開機後，它會回到 Default Target Address (DTA, 預設廣播地址 0x61h)。    
- 系統必須再次由 ARP Controller 執行 ARP 流程，重新分配新的 SMBus 地址。