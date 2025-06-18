To prevent messages coming to a SMBus Host from unknown devices in unknown formats only one method of communication is allowed, a modified form of the Write Word protocol. The standard Write Word protocol is modified by replacing the command code with the alerting device’s address. This protocol MUST be used when a SMBus device, which is normally a target, becomes a controller for this transaction in order to communicate with the SMBus Host (which acts as a target for this transaction).

Communication from a SMBus device to the SMBus Host begins with the SMBus Host address (0001 000b). The message’s Command Code is the initiating SMBus device’s address. From this, the SMBus Host knows the origin of the following 16 bits of device status. The contents of the status are device specific.

SMBus Hosts, as defined in Section 6.1.3, must support the SMBus Host Notify protocol. Hosts may implement the optional SMBALERT# line if devices in the system use it.

## 概要說明


## 為什麼需要 Host Notify？
- Host Notify 是一種「目標裝置主動通知 ARP Controller」的機制。    
- 通常用於告知：**「我有新裝置插入」** 或是 **「裝置被移除」** 等事件。

## Host Notify 由誰發起？
- 發起者是原本的從裝置（Slave），此時角色變為 Controller（主控）    
- 接收者是 SMBus Host，裝置會發起一個 Write Word Protocol 給 Host

## Host Notify 有什麼幫助 ?
- 若系統允許裝置在 SMBus 上動態插拔，Host Notify 可以幫助通知 ARP Controller。    
- 這樣可以主動觸發 ARP 過程，而不用 Controller 不斷掃描（更有效率）