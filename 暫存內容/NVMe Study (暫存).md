- FLR
	- 重置後沒有 LTSSM ( 疑問 ? )
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

- **後續要記錄的 TRACE**
	- 重新記錄多個 NS 新增, 刪除, 或是加入等多個操作
	- 嘗試紀錄不正常斷電後, 控制器關閉的行為