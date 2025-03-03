## 參數說明
1. `NSTAT`（當前 I/O Impacted 狀態）
	- 代表 NVMe 控制器當前 **I/O 受影響（I/O Impacted）** 的狀態。
	- 控制器因 **電源管理、故障處理或異常狀態** ，可能會變化。
 1. `NRDY`（控制器未準備就緒狀態）
	- `NRDY` 代表 **控制器未準備好（Not Ready）** 的狀態。
	- 當 `NRDY` 被設置時，控制器不接受新的 I/O 命令。 
    - 發生異常狀態（如 `PLS Not Ready` 或 `CSTS.RDY = 0`）

![[Pasted image 20250226070520.png]]