## Prepare to ARP

## Get UDID

### Directed Get UDID

### General Get UDID 
#### UDID 比對成功
如果裝置完整比對所有 16 個 UDID 位元組，它必須：
- 立即採用新的 SMBus Address
- 如果支援 Persistent Target Address，要更新它的記憶體設定    

#### NACK 回應時機
這讓 ARP Controller 可透過偵測哪個位元組 NACK，知道哪個裝置「不是」目標。
- 所有 ARP Capable 裝置都必須「監控整個 UDID」內容    
- 若某裝置在比對過程中某一個位元組不符，就應該：
    - 立即送出 NACK（理想情況）
    - 或是在下一個位元組送出 NACK（若無法及時） 

## Assign Address