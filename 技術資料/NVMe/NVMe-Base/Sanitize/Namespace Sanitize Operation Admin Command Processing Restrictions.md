

- Namespace Sanitize Operations
	- Admin Command Restrictions, All Controllers
	- Admin Command Restrictions if Sanitizing Attached Namespace

這裡分為兩種限制，一個是針對所有 Controllers，另外一個是針對 Controller 有連結 Namespaces
規範當執行 Sanitize Operation，需要拒絕 Admin 命令以避免影響 Namespace 屬性或功能。

保持一個原則 : 
- 如果您的命令中 `NSID` 指定為該正在清理的 Namespace ID。
- 如果命令有影響到正在清理的 Namespace ID ( e.g., Namespace Management )。

那麼這條指令會被拒絕，無法執行
