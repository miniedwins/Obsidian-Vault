## 參數說明
主機透過 `PLN` 訊號通知控制器，表示當前即將發生斷電，控制器需要採取相應的處理流程。 

1. **PLN 的作用**：
	- PLN 是一個由主機發出的信號，用於通知控制器即將發生斷電（Power Loss）。  
    - 控制器收到 PLN 信號後，會根據當前的狀態和配置，採取相應的措施來保護數據（例如將緩存中的數據寫入非易失性存儲）。

2. **PLN 的兩個狀態**：    
    - `Asserted`：表示主機檢測到即將發生斷電，並通知控制器。 
    - `Deasserted`：表示斷電風險已解除，系統恢復正常運行。

![[Pasted image 20250221153007.png]]

## 注意事項
**(1) 控制器應忽略 PLN 變數的變化，當任一下列情況發生時：**
1. 控制器正在進行 `Controller Level Reset`
	- 這表示控制器正在重置，任何狀態變化都可能不穩定，因此 PLN 變數的變化應被忽略。
2. CSTS.SHST 欄位未清除為 `00b`
	- 代表控制器正在關機或已經完成關機，在這種情況下 PLN 應被忽略，以避免影響關機流程。

 **(2) 如果 PLN 被設為 Asserted，且當前電源狀態滿足以下條件之一：
 - 如果這些欄位表示為 `0`
	1. Emergency Power Fail Vault Time 
	2. Forced Quiescence Vault Tim 
	3. Emergency Power Fail Recovery Time
- 內容說明
	 1. 代表沒有規範該如何處理，而是由廠商自行決定具體的行為。
	 2. 應該可以表示不支援 `Power Loss Signaing`。