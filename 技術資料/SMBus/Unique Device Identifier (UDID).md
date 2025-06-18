

- 筆記整理內容
	- UDID 概要
	- 說明欄位內容
	- 使用環境


| 位元值（bit[1:0]） | 類型                           | 說明                                                            |
| ------------- | ---------------------------- | ------------------------------------------------------------- |
| `00b`         | Fixed Address Device         | 裝置有一個**固定的 SMBus/I²C 位址**，無法透過動態指派變更。常見於簡單感測器或 legacy 裝置。     |
| `01b`         | Dynamic & Persistent Address | 裝置支援動態指派 SMBus 地址，且**地址在斷電後仍會保留（非易失性）**。例如支援 EEPROM 存儲的智能裝置。  |
| `10b`         | Dynamic & Volatile Address   | 裝置支援動態指派 SMBus 地址，但**斷電後會遺失地址設定（易失性）**。例如初始化後分配地址，但下次開機重新分配。  |
| `11b`         | Random Number Device         | 裝置沒有可用地址，**僅用於初始裝置發現階段（如 ARP）**，可透過唯一隨機碼識別它。通常會要求分配新位址後才啟用功能。 |

## GET UDID ( General ) 
### UDID 比對 & NACK 回應時機
這讓 ARP Controller 可透過偵測哪個位元組 NACK，知道哪個裝置「不是」目標。

- 所有 ARP-capable 裝置都必須「監控整個 UDID」內容    
- 若某裝置在比對過程中某一個位元組不符，就應該：
    - 立即送出 NACK（理想情況）
    - 或是在下一個位元組送出 NACK（若無法及時）        

### 裝置比對成功
如果裝置完整比對所有 16 個 UDID 位元組，它必須：
- 立即採用新的 SMBus Address
- 如果支援 Persistent Target Address，要更新它的記憶體設定    
- 忽略分配位元組的 bit0（LSB），因為地址是 7-bit（最高只能到 0x7F）

## GET UDID ( Direct ) 

