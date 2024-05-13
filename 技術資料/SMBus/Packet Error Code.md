Packet Error Code (PEC) 是用來做檢驗傳遞的封包是否有錯誤，針對每個寫入或是讀取資料傳輸後，透過 (CRC-8) 計算出所有的 `message` 校驗碼，最後在傳輸的結尾加入 PEC。

當收到的資料的 `Master` 或是 `Slave` 可以透過校驗碼確認資料是否有錯誤，若是傳遞的資料有錯誤則需要重新再發送。

- 傳遞 PEC 前確認事項 : 
  - `Master` 控制端在傳送 PEC 之前，需要確認 `Slave` 目標端是否有支援 PEC。
  - `Slave` 目標端在收到資料後，必須要檢查是否需要回傳 with PEC 或是 Without PEC 給控制端。

- 計算 PEC 不包含以下位元 : 
  - ACK
  - NACK
  - START
  - STOP
  - REPEATED START

> 以下圖示簡易說明 PEC 所傳遞的位置。

1. `Master` 傳送資料給 `Slave`，資料傳輸完畢後加入 `PEC` 校驗碼

// TODO : Capture Send byte protocol with PEC

2. `Master` 收到來自 `Slave` 回傳的資料，資料傳輸完畢後加入 `PEC` 校驗碼

// TODO : Capture Receive byte protocol with PEC
