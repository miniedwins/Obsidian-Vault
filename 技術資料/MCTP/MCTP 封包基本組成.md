


Package = MCTP Header + Message Body 
MCTP Header = 
Message Body  = Message Header + Message Data
Message Body  = ( MessageType + IC ) + Message Data


MCTP packet payload = 64 Bytes
每一個 MCTP Packet 的 Payload 最多為 64 bytes
最多一次可以傳送 66 Packets × 64 bytes = 4224 bytes