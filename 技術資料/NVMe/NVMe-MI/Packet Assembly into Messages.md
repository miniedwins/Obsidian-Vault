在 MCTP (Management Component Transport Protocol) 中，一個 NVMe-MI Message 可能需要切割成多個 MCTP Packet 來傳輸。接收端必須根據封包中的 Start of Message (SOM) 與 End of Message (EOM) 標記，將多個封包重新組合 (Assembly) 成為完整的 Message。 

## 傳輸單元大小一致性
除了訊息的最後一個封包外， 一個 Message 內的所有封包，其 **MCTP Transmission Unit (MTU)** 大小必須相同，且需符合雙方事先協商好的 **MTU Size**。

## 最後一個封包 (EOM=1) 的大小
當封包是 Request/Response Message 的最後一個封包 (EOM bit = 1) 時，其大小應為剛好能容納剩餘的 Payload。不可額外填充 (padding)，除非是物理層需要的對齊或尾碼 (trailer)。

## 完整 Message 的驗證
當所有封包組合成完成後，驗證 Message Integrity Check (MIC)。 驗證結果的處理方法如下 :
- MIC 通過 → Message 交由 NVMe-MI 處理。
- MIC 失敗 → Message 被丟棄 (不處理)。

