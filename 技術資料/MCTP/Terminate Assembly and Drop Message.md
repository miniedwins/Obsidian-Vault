說明了哪些情況下，MCTP 組裝中的訊息（message-in-progress）會被終止與丟棄。

## 1. 正常 Termination
說明：收到了 EOM=1 的封包，且前面已正確收到 SOM=1 開頭的封包序列。
動作：對這些完整的訊息進行組裝，這是一個正常情況（Normal Termination）。

## 2. 收到新的 SOM（新的訊息起始封包）
說明：一筆訊息還在組裝中，就又收到另一筆對同一 Endpoint 的 SOM 封包。
動作：需要丟棄舊的那一筆正在處理的訊息，然後開始以新封包為開頭組裝新訊息。

## 3. 等待封包超時
說明：多個封包（multiple-packet message）中間間隔太久，超過 Timeout 時間。
動作：丟棄所有訊息。
備註：Timeout 由 Transport binding 規範定義。

## 4.  Pkt Seq 編號不連續（順序錯誤）
說明：同一筆訊息中，封包的 `Packet Sequence` 沒有按照 mod 4 順序遞增。
舉例：上個是 Seq=0，卻收到 Seq=2（應該是 Seq=1）。
動作：丟棄所有組裝中的訊息。

## 5. 不正確的傳輸單元（Unit）
說明：假設收到 middle packet 封包（SOM = 0b and EOM = 0b），但是它的 Payload 大小不符合開始封包（SOM = 1b and EOM = 0b）Payload 大小。每個封包的 payload 大小應一致（除了最後一包 EOM=1 的可能較小）。

**錯誤範例：起始封包不一致**

| Packet | SOM | EOM | Payload Length | 說明             |
| ------ | --- | --- | -------------- | -------------- |
| 1      | 1   | 0   | 48 bytes       | Start 封包       |
| 2      | 0   | 0   | 36 bytes       | ❌ 錯誤：與起始封包長度不同 |

**正確範例：Middle 封包與起始封包一致****

|Packet|SOM|EOM|Payload Length|說明|
|---|---|---|---|---|
|1|1|0|48 bytes|Start 封包|
|2|0|0|48 bytes|Middle 封包|
|3|0|0|48 bytes|Middle 封包|
|4|0|1|12 bytes|✅ End 封包（尾包可短）|
## 6. Message Integrity Check 錯誤
說明：一個或多個 Packet 組裝結束後，發現訊息完整性檢查值不匹配。
動作：組裝終止並且整個訊息被丟棄，因為是「silently discard」，對方不會傳任何 Response。
處理方式：
1. Host 等到 MCTP Transaction Timeout，發現沒有回覆，就會視為失敗。
2. Host 會嘗試 重送該封包訊息。