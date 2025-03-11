## 概要說明
NOPS (Non-Operational Power State) 指的是當控制器 `沒有任何 I/O 命令需要處理`，且閒置超過設定時間後，主機 (Host) 或控制器 (NVMe) 會將電源狀態切換到 `非操作電源模式`，以降低功耗。

## 重點整理
1. 主機可以發送命令要求進入 `NOPS` 非操作電源模式。
2. 透過 [[Autonomous Power State Transitions#Idle Time Prior to Transition（ITPT）|ITPT]] 閒置時間判定是否進入該電源狀態。
3. 不允許處理 I/O 命令，但仍可執行管理類 (Admin) 指令與背景操作。
4. 當有 I/O 命令時，控制器需自動切換至最近操作電源狀態，確保能夠處理請求。
5. 支援 `Permissive Mode` 的控制器可以暫時超過 `MP` 來執行背景工作，以提高系統靈活度。

當位在 NOPS 狀態，控制器還是可以運行其它非 I/O 命令，例如 : 閒置時候的背景操作，這個時候可能會超過控制器宣告該電源狀態的最大功耗 `MP`，以下的操作是可以在 `NOPS` 狀態中運行 :
- Servicing a memory-mapped I/O (MMIO) 
- Configuration register access
- Processing a command submitted to the Admin Submission Queue 

根據上述的結論，若是控制器有支援 [[Non-Operational Power State Permissive Mode]]，是可以允許控制器暫時超過該電源階段所宣告的最大功耗 (MP)。它的條件是在 `NOPS` 狀態下，允許背景執行以上所說的非 I/O 操作。
