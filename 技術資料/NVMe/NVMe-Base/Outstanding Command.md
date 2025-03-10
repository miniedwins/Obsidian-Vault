主機提交 NVMe 命令，只要命令還在「等待處理」的狀態，它就是 `Outstanding`。

什麼狀態下可以稱為 Outstanding : 
- 主機（Host）已經將該命令提交到控制器（Controller）。
- 主機尚未收到該命令的完成（Completion Entry）。
- 取消命令（Abort Command）。

什麼時候命令不再是 Outstanding？
- 當 NVMe 完成命令，結果進入 `Completion Queue`，此時命令不再 Outstanding。
- 取消命令（Abort Command）。
- 執行影響命令狀態的動作，例如 : 
	- 控制器重設（Reset Controller）
	- `CSTS.RDY` 位元由 `1` 設定為 `0`。
	- `CSTS.SHST` 狀態改變成 `10`，表示控制器已經完成關機。
	- 執行 Delete I/O Submission Queue。