
If the NSID field specifies a namespace as the sanitization target and an NVM subsystem sanitize operation is in progress, then the command shall be aborted with a status code of Sanitize In Progress.

>當指定的 NSID 正在執行 Sanitize，NVM 子系統會拒絕取得 Sanitize Log Page。

If the NSID field specifies a namespace as the sanitization target and the NVM subsystem is in the Restricted Failure state or the Unrestricted Failure state, then the command shall be aborted with a status code of Sanitize Failed.

>當 Sanitize 過程發生錯誤，導致 NVM 子系統進入 **Restricted Failure** 或 **Unrestricted Failure** 狀態時，若是指定該 NSID ( Sanitization Target ) 取得 Sanitize Log Page，控制器會 Abort 該命令並且返回 **Sanitized Failed Status Code**。