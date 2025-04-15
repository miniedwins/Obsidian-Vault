1. 使用 SET FEATURES 設定
	- Subcommands ( 0x10 ) : Enable  SATA feature
	- Subcommands ( 0x90 ) : Disable SATA feature
	- Sector Count ( 0x09 )  :  Device Sleep

2. 當前這個設定是失敗的，主機端回傳 Status=0x02，代表 Command Aborted

![[Pasted image 20250415074822.png]]

- SET FEATURES Subcommands ( 省略很多 Subcommands )

![[Pasted image 20250415080041.png]]

- Enable/Disable SATA Feature ( 允許主機端設定關於 SATA 功能 )

![[Pasted image 20250415075146.png]]