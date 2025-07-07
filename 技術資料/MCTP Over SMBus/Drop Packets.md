接收封包時可能中止或丟棄訊息可能會造成的原因。

## 1. 封包順序錯誤／訊息組裝問題
收到中段（SOM=0, EOM=0）或結尾（SOM=0, EOM=1）封包時，先前沒收到 SOM=1 開頭封包，即「訊息未開始就有中段或結尾」。

## 2. 資料鏈結層（Data Link Layer）錯誤
封包資料經過 **Integrity Check 或是 PEC 檢查失敗**。其他可能的物理層錯誤，包括訊框錯誤、位元組 對齊錯誤、封包大小不符合物理層要求等等。

## 3. Message Tag 錯誤


## 4. 目的端 EID 錯誤
收到封包，但封包中的 Destination EID 不符合本裝置 EID（或 Null-EID + physical address）。

## 5. EID 路由失敗
當一個 MCTP bridge 無法找到目標 EID 的路由紀錄，即無法路由該 EID 而造成失敗。

## 6. 通訊協定不支援或傳輸單位錯誤
- MCTP Header Version 欄位不是裝置能支援的版本
- 傳輸的封包太大或太小，不符合本 Endpoint 裝置所支援的限制


 


