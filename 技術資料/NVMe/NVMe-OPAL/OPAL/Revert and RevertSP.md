
## Revert
### 重點摘要如下：
- Revert 是 Opal SSC 專用方法，用於管理製造時建立的 SP（Manufactured SP）的生命週期。

- 只能對 Admin SP 的 SP table 中的物件執行，且不能對已發行（issued）的 SP 執行。

- 執行 Revert 會將 SP 還原為原廠狀態（Original Factory State），移除 SP 擁有者的所有權。

- 僅允許 TPer 擁有者或製造商（若權限允許）執行。

- 可對任何生命週期狀態的 Manufactured SP 執行，若 SP 處於 Manufactured-Inactive 狀態則無影響。

- 必須在 Admin SP 的 Read-Write session 內執行，且必須在非交易（non-transaction）狀態下立即還原。

- 若對 Admin SP 本身執行 Revert，TPer 會在回報狀態後立即終止 session，並可能準備 CloseSession 方法供主機檢索。
- 
- Revert 方法的 MethodID 為 0x00 00 00 06 00 00 02 02。
