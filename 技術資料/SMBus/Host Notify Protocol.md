To prevent messages coming to a SMBus Host from unknown devices in unknown formats only one method of communication is allowed, a modified form of the Write Word protocol. The standard Write Word protocol is modified by replacing the command code with the alerting device’s address. This protocol MUST be used when a SMBus device, which is normally a target, becomes a controller for this transaction in order to communicate with the SMBus Host (which acts as a target for this transaction).

Communication from a SMBus device to the SMBus Host begins with the SMBus Host address (0001 000b). The message’s Command Code is the initiating SMBus device’s address. From this, the SMBus Host knows the origin of the following 16 bits of device status. The contents of the status are device specific.

SMBus Hosts, as defined in Section 6.1.3, must support the SMBus Host Notify protocol. Hosts may implement the optional SMBALERT# line if devices in the system use it.

## 為什麼需要 Host Notify？
- 有些事件發生時，裝置需要主動通知主機 。
- 因此 SMBus 規範定義一個叫做 **Host Notify 的特殊寫入格式**，讓裝置也能變成 Controller 傳送一筆資料給主機。

## Host Notify 資料由誰發起？
- 發起者是原本的從裝置（Slave），此時角色變為 Controller（主控）    
- 接收者是 SMBus Host，裝置發起一個 Write Word Protocol 給 Host