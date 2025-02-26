### 工作流程
當控制器進入 `FQ Processing 狀態時，會依序執行以下步驟 ：

1. 設置 PLA 變數為 `Asserted-FQ`（如果支援）
2. 停止擷取所有 Submission Queues 任何命令
3. 並行或順序執行以下操作：
	- 處理來自管理端點的 `out-of-band 命令`（如果有 NVMe-MI）。
	- 完成進入該狀態前處理已擷取的命令（例如，回報命令完成或中止）。
	- 準備電源丟失處理流程 （FQ Processing）。
4. 進入 `FQ Complete` 狀態（表明 FQ 完成）。
5. 通知系統 `FQ` 處理已完成，將 PLA 變數設為 `Deasserted`。

### 注意事項
1. 如果正在執行背景作業（如 Self-Test 或 Sanitize）：
	- 暫停執行，直到 PLN 變數恢復至 `Deasserted` 並恢復命令提取。

2. 如果在 FQ Processing 狀態收到 `Set Features` 命令： 
	- 指定 Power Loss Signaling Config  該命令會被 中止。

3. 如果控制器在「FQ Processing」狀態下轉換到「PLS Not Ready」：
	- 處理將被中止（Abort FQ Processing）。
	- 不會影響主機與控制器的通訊。

4. 如果 PLN 被設為 `Asserted`，然後又變回 `Deasserted`：
	- 控制器會恢復提取與處理命令（沒有經歷掉電、控制器重置或關機）。

5. 如果 `FQ Processing` 期間發生掉電，控制器的恢復時間取決於掉電方式：
	- 比正常關機後重新上電更久。
	- 但比直接掉電恢復要快（FQ 可能執行一半的處理，因此恢復速度相比直接掉電快）。