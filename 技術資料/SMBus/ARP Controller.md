## 什麼是 ARP Controller？
- ARP Controller = 負責執行 ARP 流程的 SMBus 主控制器 (Host Controller)**。   
- 功能：    
    1. 偵測新裝置（例如 : 有支援 [[Notify ARP Controller]] 命令裝置）。
    2. 發送 ARP 指令，與所有 ARP-capable devices 互動。        
    3. 收集裝置 UDID (Unique Device Identifier)。        
    4. 分配裝置唯一的 SMBus 地址，避免位址衝突。

## ARP Controller 的職責
1. 廣播查詢 (Discovery)    
    - 用預設廣播地址（0x61h，依 SMBus 規範）詢問線上有哪些 ARP-capable devices。        
2. 收集 UDID    
    - ARP-capable devices 回覆自己的 UDID (128-bit unique identifier)。        
    - ARP Controller 確認裝置 ( Slave ) 身份
3. 分配新地址 (Assign Address)    
    - 給每個裝置分配一個唯一的 7-bit SMBus 地址。        
    - 裝置之後就用這個新地址與 Host 通訊。        
4. 維護地址表    
    - 建立 UDID ↔ SMBus Address 的對應表。        
    - 之後主機就能透過分配的地址來存取裝置。
    - 確保所有裝置位址 ( Slave Address ) 不衝突。 