說明了哪些情況下，MCTP 組裝中的訊息（message-in-progress）會被終止與丟棄。

## 1. 正常 Termination
說明：收到了 EOM=1 的封包，且前面已正確收到 SOM=1 開頭的封包序列。
動作：對這些 Messages 進行組裝完成，這是一個正常情況（Normal Termination）。

## 2. 收到新的 SOM（新的訊息起始封包）
說明：一筆訊息還在組裝中，就又收到另一筆對同一 Endpoint 的 SOM 封包。
動作：需要丟棄舊的那一筆正在處理的 message，然後開始以新封包為開頭組裝新訊息。

## 3. 等待封包超時
說明：多個封包中間間隔太久，超過 Timeout 時間。
動作：丟棄這筆訊息。
備註：Timeout 由 Transport binding 規範定義（如 SMBus）。

## 4.  Pkt Seq 編號不連續（順序錯誤）
說明：同一筆訊息中，封包的 `Packet Sequence` 沒有按照 mod 4 順序遞增。
舉例：上個是 Seq=0，卻收到 Seq=2（應該是 Seq=1）。
動作：丟棄所有組裝中的訊息。

## 5. 不正確的傳輸單元（Unit）

## 6. Message Integrity Check 錯誤
說明：一個或多個 Packet 組裝結束後，發現訊息完整性檢查值不匹配。
動作：導致訊息組裝終止並且整個訊息被丟棄。