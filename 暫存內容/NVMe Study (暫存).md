- FLR
	- 重置後沒有 LTSSM ( 疑問 ? )
		-  **FLR 的作用範圍**
			- FLR 僅重置設備的特定功能，涉及設備內部邏輯，而非物理鏈路。
			- FLR 不會觸發鏈路的重新訓練，因此 LTSSM 狀態通常保持在 **L0（Active）**。
		- **特殊狀況**	 
			 - **設備設計需要重新初始化鏈路**：
				 - 如果 NVMe 設備的設計要求 FLR 同時重置物理層，則可能觸發鏈路重新訓練，LTSSM 狀態會從 **L0 → Recovery → Configuration → L0**。
			- **驅動或系統層干預**：
				- 如果主機在執行 FLR 後，選擇釋放設備並重新綁定驅動，則可能會導致鏈路重新訓練。	 
	- 系統沒有**刪除 I/O SQ and CQ**
		- 可能是直接對 PCIe 暫存器操作, 因此沒有經過驅動程式, 所以直接重置 ( 猜測 )

- NVMeCli Reset
	- 系統有執行**刪除 I/O SQ and CQ**

- Linux Remove Device
	- 系統有執行**刪除 I/O SQ and CQ**
	- 寫入CC.SHN=01 ( Shutdown Notification )

- Power Off
	- 系統有執行**刪除 I/O SQ and CQ**
	- 寫入CC.SHN=01 ( Shutdown Notification )

- Linux Rescan
	- 主機端會直接將 CC.EN=0
	- 讀取控制器 SHST=01, 然後等待後再讀取會變成 SHST=00 
		- 代表前面移除後,  因為還是維持有電的狀態, 所以一開始 SHST=01 還是維持這個值
	- 重新執行初始化相關流程


---

- **問題追蹤**
	- 確認NVMeCli重置後, 檢查關機或不正常關機會是加在哪一個參數 ? 
	
- **後續要記錄的 TRACE**
	- 重新記錄多個 NS 新增, 刪除, 或是加入等多個操作
	- 嘗試紀錄不正常斷電後, 控制器關閉的行為

 - **後續要修改的筆記**
	 - HMB :  加入詳細說明 Host Memory Descriptor
	![[Pasted image 20241127081953.png]]