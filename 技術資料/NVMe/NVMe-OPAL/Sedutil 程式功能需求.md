
請提供 Sedutil-CLI  for CNL 控制的操作介面，包含 Locking Object 指派、解除、範圍設定與 Shadow MBR 控制。這些相關執行命令主要用來測試 TCG OPA CNL 基本功能使用。

備註 : 
1. 以下僅是列出初步建立可執行的命令需求，後續需要再討論細節
2. 未來還會有機會追加新功能的可能性，請保持程式開發的彈性

後續討論內容 : 
1. 執行的參數是否符合設定需求
2. 執行命令格式是否需要調整
3. 定義執行輸出結果的格式 ( 終端機畫面與輸出檔案格式 )
4. 定義顯示 Locking object 輸出的顯示畫面結果以及屬性欄位

====================================================
命令與功能說明： 
1. assign - 建立 Locking Object 與 Namespace 的關聯
2. deassign - 解除 Locking Object 與 Namespace 關聯
3. setLockingrange - 設定 Locking Object 的範圍屬性
4. enableLockingrange -  設定 Locking Object Locked 狀態
5. listLockingobject  -  顯示目前有多少個 locking object 包含所有的屬性
6. setmbrEnable - 控制 Shadow MBR 啟用與不啟用
7. setmbrNSID - 控制 Shadow MBR 狀態與 Namespace 對應

參數定義 : 
./sedutil --assign --ns=<NSID>  --range-start=<LBAs>  --range-length=<LBA_LEN>
./sedutil --deassign --uid=<LO>  --keepGlobalRangeKey=<true|false>
./sedutil --setLockingrange --uid=<LO> --range-start<LBAs>  --range-length<LBA_LEN>
./sedutil --enableLockingrange  --uid=<LO> --rw=<LK|RO|RW>
./sedutil --listLockingobject  --uid=<LO> --all=<true|false>
./sedutil --setmbrNSID --ns=<NSID>
./sedutil --setmbrEnable <true|false> 
====================================================