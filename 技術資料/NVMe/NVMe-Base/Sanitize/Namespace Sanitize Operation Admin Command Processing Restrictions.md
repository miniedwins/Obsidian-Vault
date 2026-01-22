
這裡分為兩種限制，一個是針對所有 Controllers，另外一個是針對 Controller 有連結 Namespaces
當 Sanitize Operation 正在執行時，需要 Abort Admin 命令以避免影響 Namespace 屬性或功能。

保持一個基本原則 : 
- (1) 如果命令中 `NSID` 指定為該正在清理的 Namespace ID。
- (2) 如果命令會影響到正在清理的 Namespace ID ( e.g., Namespace Management )。
- 若是任何一個條件成立，那麼當前這條指令會被拒絕 ( Abort )，無法執行。

## Admin Command Restrictions, All Controllers


## Admin Command Restrictions if Sanitizing Attached Namespace