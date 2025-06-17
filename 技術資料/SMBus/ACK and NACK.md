
## ACK
A SMBus device must always acknowledge (ACK) its own address. SMBus uses this signaling to detect the presence of detachable devices on the bus.

## NACK
A SMBus target device may decide to NACK a byte other than the address byte in the following situations:

• The target device is busy performing a real time task, or data requested are not available. The controller upon detection of the NACK condition must generate a STOP condition to abort the transfer. Note that as an alternative, the target device can extend the clock LOW period within the limits of this specification in order to complete its tasks and continue the transfer.

• The target device detects an invalid command or invalid data. In this case the target device must NACK the received byte. The controller upon detection of this condition must generate a STOP condition and retry the transaction.

• If a controller-receiver is involved in the transaction it must signal the end of data to the target-transmitter by generating an NACK on the last byte that was clocked out by the target. The target-transmitter must release the data line to allow the controller to generate a STOP condition.