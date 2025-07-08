說明了哪些情況下，MCTP 組裝中的訊息（message-in-progress）會被終止與丟棄。

## 1. 正常 Termination
收到了 EOM=1 的封包，且前面已正確收到 SOM=1 開頭的封包序列。這是一個正常情況（Normal Termination）。

## 2. 收到新的 SOM（新的訊息起始封包）
一筆訊息還在組裝中，就又收到另一筆對同一 endpoint 的 SOM 封包。需要丟棄舊的那一筆正在處理的 message，然後開始以新封包為開頭組裝新訊息。

## 3. 等待封包超時
多個封包中間間隔太久，超過 Timeout 時間，丟棄這筆訊息。timeout 由 Transport binding 規範定義（如 SMBus）。

## 4.  Pkt Seq 編號不連續（順序錯誤）
同一筆訊息中，封包的 `Packet Sequence` 沒有按照 mod 4 順序遞增。舉例：上個是 Seq=0，卻收到 Seq=2（應該是 Seq=1）。丟棄所有組裝中的訊息。

## 5. 不正確的傳輸單元（Unit）

## 6. Message Integrity Check 錯誤
一個或多個 Packet 組裝結束後發現錯誤，如果訊息完整性檢查值不匹配，則可能導致訊息組裝終止並且整個訊息被丟棄。