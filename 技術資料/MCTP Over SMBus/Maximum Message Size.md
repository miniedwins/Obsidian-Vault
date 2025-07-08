The MCTP message body (including IC bit, Message Type, Message type-specific header fields,
message payload and message integrity check if present) for NVMe Management Messages over MCTP shall be less than or equal to 4224 (4K+128) bytes.

This corresponds to a transfer of 66 MCTP packets using a baseline transmission unit of 64 bytes for the MCTP packet payload.

這代表：
- 每個封包 **最多可帶 64 bytes 的 payload**    
- 要傳送的 message 內容超過 64 × 66 = **4224 bytes**    
- 必須切成 66 個封包傳送（其中最後一包 payload 可能較短）