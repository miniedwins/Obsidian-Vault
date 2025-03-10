Non-Operational Power States (NOPS) : 定義是當控制器沒有任何 I/O 命令需要處理，並且閒置了一段時間後，就會進入到非操作電源模式。因為是主機 (Host) 自動切換電源狀態，前提條件下必須要啟用 `APST`。

從主機的角度來看，就是沒有任何 `Pending I/O` 提交到控制器，主機就會發送 Set Features Command 切換目前的 **power state to non-operational power state**，在這段命令還沒執行完畢前，是不會再提交任何的 I/O 命令。因為控制器是平行處理 (parallel) 各種不同的命令，若是同時執行 `Admin & IO` 命令 ，可能會導致切換到不可預期電源狀態。

值得注意的一點，無論 `APST`是否有被啟用， 一旦電源狀態位在 `NOPS` 狀態下，當有任何的 I/O 命令被提交，控制器必須要切換到最近的 `operational power state`。

例如 : 電源狀態位在 `PS4` 的時候，若是控制器有收到 I/O 命令，就可能會將目前的電源狀態切換到 `PS0` 或其它能夠運行 I/O 命令的電源狀態，因為`NOPS` 狀態是不允許處理 I/O 命令 。比較正確的說法，當有一個 `I/O Submission Queue Tail Doorbell` 暫存器的值被主機寫入，代表有 I/O 命令需要被控制器提取以及處理。

當位在 NOPS 狀態，控制器還是可以運行其它非 I/O 命令，例如 : 閒置時候的背景操作，這個時候可能會超過控制器宣告該電源狀態的最大功耗 `MP`，以下的操作是可以在 `NOPS` 狀態中運行 :
- Servicing a memory-mapped I/O (MMIO) 
- Configuration register access
- Processing a command submitted to the Admin Submission Queue 

根據上述的結論，若是控制器有支援 Non-Operational Power State Permissive Mode，是可以允許控制器暫時超過該電源階段所宣告的最大功耗 (MP)。它的條件是在 `NOPS` 狀態下，允許背景執行以上所說的非 I/O 操作。

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/non_operational_power_state_config.png)

*備註 : Non-Operational Power State Permissive Mode Disable (待續 ...)*