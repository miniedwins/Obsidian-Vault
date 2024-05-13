Packet Error Code (PEC) 是用來做檢驗傳遞的封包是否有錯誤，針對每個寫入或是讀取資料傳輸後，透過 cyclic redundancy check (CRC-8) 計算出校驗碼，傳輸最後結尾加入 PEC。

當收到的資料的 `Master` 或是 `Slave` 可以透過校驗碼確認資料是否有錯誤，若是傳遞的資料有錯誤則需要重新再發送。

> 以下圖示簡易說明 PEC 所傳遞的位置。

1. `Master` 傳送資料給 `Slave`，資料傳輸完畢後加入 `PEC` 校驗碼

// TODO : Capture Send byte protocol with PEC

2. `Master` 收到來自 `Slave` 回傳的資料，資料傳輸完畢後加入 `PEC` 校驗碼

// TODO : Capture Receive byte protocol with PEC

計算 PEC 不包含以下位元 : 
- ACK
- NACK
- START
- STOP
- REPEATED START
