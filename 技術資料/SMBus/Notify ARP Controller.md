## 概要說明
- 主要功能是一種「目標裝置主動通知 ARP Controller」的機制。    
- 通常用於告知：「我有新裝置插入」 或是 「裝置被移除」 等事件。　
- 它是一個可選的功能（Optional feature），不是所有支援 ARP 的裝置都必須實作。
- 若是做為 Host Controller ，必須要支援 Host Notify 命令。

## Host Notify 由誰發起？
- 發起者是原本的從裝置（Slave），此時角色變為 Controller（主控）    
- 接收者是 SMBus Host，裝置會發起一個 Write Word Protocol 給 Host

## Host Notify 有什麼幫助 ?
- 若系統允許裝置在 SMBus 上動態插拔，Host Notify 可以幫助通知 ARP Controller。    
- 這樣可以主動觸發 ARP 過程，而不用 Controller 不斷掃描（更有效率）