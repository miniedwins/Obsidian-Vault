EID (Endpoint ID) 是 MCTP 資料鏈結層中用來識別設備的邏輯位址。 每個 Endpoint（例如 NVMe-MI、BMC 內部元件等）會分配一個唯一的 **非 0 EID**（通常由 Endpoint Discovery 或靜態配置來決定）。

## Null Source EID
這筆封包的發送端也尚未擁有 EID，例如：
- 某設備主動廣播自身存在（像 Get UDID Response） 
- 此時 header 中 `Source EID = 0`，只能透過 SMBus Slave Address 辨識來源

>**限制：**
>1. 同樣不能在 multi-bus 或透過 bridge 傳送，因為 Physical Address 不是全域唯一。

## Null Destination EID
適用於設備尚未經由 Endpoint Discovery 分配 EID 的情況，例如：
- 剛開機的 NVMe-MI 裝置        
- 還沒做 Set EID 的 ARP-capable 設備

>**限制：**
>1. 不能跨 bus 使用（因為 Physical Address 在不同 bus 可能重複）。