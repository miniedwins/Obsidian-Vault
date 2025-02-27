當控制器被設定為 Power Loss Signaling（PLS）並啟用 Emergency Power Fail（EPF），如果進入 `EPF Processing Port Disabled` 或 `EPF Processing Port Enabled`，則會執行以下步驟：

### 工作流程 
1. 如果支援 `PLA`，則根據 EPF 狀態設定對應的 PLA 值：
	- EPF Processing Port Disabled → `Asserted-EPF-Disabled`
	- EPF Processing Port Enabled → `Asserted-EPF-Enabled`
2. 停止擷取所有 Submission Queues 任何命令
3. 並行或順序執行以下操作：
	- 依據 Port Communication ( Enable  or Disable )規則處理與其他設備的通訊。
	- 準備電源丟失處理流程
		- ( 原文 ) : prepare for power loss in a manner that may or may not allow command processing to resume quickly in the event of power loss and then power resumption
		- ( 說明 ) : 控制器在電源丟失（Power Loss）前的準備方式，可能會影響電源恢復（Power Resumption）後命令處理的恢復速度。
	- 進入 `EPF Complete` 狀態（表明 EPF 完成）。
		- 若進入 EPF Complete Port Enabled，則 PCIe 端口仍可保持活動。
		- 若進入 EPF Complete Port Disabled，則 PCIe 端口將被關閉。
	- 完成 EPF 處理，將 PLA 變數設為 `Deasserted`。

### 注意事項
1. 所有在進入 EPF Processing 之前從 Submission Queue 已經被提取的命令：
	- 將被直接丟棄，不會執行。
	- 所有 Out-of-Band（Management Endpoint）命令也會被丟棄。

2. 控制器只能實作一種 EPF 處理狀態：
	- EPF Processing Port Enabled
	- EPF Processing Port Disabled

3. EPF 恢復時間 由 `EPFRT` 和 `EPFRTS` 決定：
	- 表示控制器在 EPF 成功處理後的首次初始化所需的恢復時間。
	- 不同廠商的控制器恢復方式不同：
		- 可能在主機設置 `CC.EN=1` 之前開始恢復。
		- 也可能等到主機設置 `CC.EN=1` 之後才開始恢復。
		- 控制器設定為 `CSTS.RDY=1` 也不代表恢復完成。

4. 處理過程中主電源就已經完全丟失：
	- 恢復時間可能會超過「緊急掉電恢復時間（EPFRT）」的上限。