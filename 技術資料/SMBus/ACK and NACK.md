## ACK
A SMBus device must always acknowledge (ACK) its own address. SMBus uses this signaling to detect the presence of detachable devices on the bus.

## NACK
A SMBus target device may decide to NACK a byte other than the address byte in the following situations:

• The target device is busy performing a real time task, or data requested are not available. The controller upon detection of the NACK condition must generate a STOP condition to abort the transfer. Note that as an alternative, the target device can extend the clock LOW period within the limits of this specification in order to complete its tasks and continue the transfer.

• The target device detects an invalid command or invalid data. In this case the target device must NACK the received byte. The controller upon detection of this condition must generate a STOP condition and retry the transaction.

• If a controller-receiver is involved in the transaction it must signal the end of data to the target-transmitter by generating an NACK on the last byte that was clocked out by the target. The target-transmitter must release the data line to allow the controller to generate a STOP condition.

## 什麼是 NACK
 NACK 是 SMBus/I2C 中從裝置對特定位元組發出的「拒絕」訊號：
- 通常在 **裝置不存在**、**裝置不支援命令**、或 **PEC 錯誤** 時出現。    
- SMBus 裝置會在特定 byte 送出 NACK，例如：    
    - UDID 比對錯誤
    - PEC 檢查錯誤        
    - 無法處理的命令
    - 停止資料傳送