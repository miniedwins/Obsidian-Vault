
- 只能對 Admin SP 的 SP table 中的物件執行，且不能對已發行（issued）的 SP 執行。
- 會將 SP 還原為原廠狀態（Original Factory State），移除 SP 擁有者的所有權。
- 可對任何生命週期狀態的 Manufactured SP 執行，若 SP 處於 Manufactured-Inactive 狀態則無影響。
- 必須在 Admin SP 的 Read-Write session 內執行，且必須在非交易（non-transaction）狀態下立即還原。
- 若對 Admin SP 本身執行 Revert，TPer 會在回報狀態後立即終止 session。

## Effects of Revert
- 成功執行 Revert 方法後，會產生以下效果：
	- 若 Locking SP 不在 “Manufactured-Inactive” 狀態
		- 依據 Active Data Removal Mechanism 移除使用者資料。
		- 媒體加密金鑰會被消除，導致 User LBA 區域的所有資料被安全抹除。
	- 若 Locking SP 處於 “Manufactured-Inactive” 狀態
		- 則執行 Revert 不會影響 User LBA 區域的所有資料。