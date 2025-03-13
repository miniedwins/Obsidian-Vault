## 概要說明
* 裝置自檢，主要定義一系列 SSD 自我檢測的驗證項目。
* 內部實現的測試方法是由廠商自定義。

## 自檢類型
主要分成兩個類型，如下說明 : 
- **Short Device Self Test** 
	* 一個自檢測試，必須要在兩分鐘內或是更少的時間完成測試
	* 自檢的進度與測試的情況，可以從自檢日誌取得資訊內容
- **Extended Device Self Test**
	* 一個自檢測試，會依據 `EDSTT` 所指定的時間內完成測試	
	* 檢測進度與測試的情況，可以從自檢日誌取得資訊內容

## 自檢項目說明
### 1. DRAM Check
DRAM 作用是來做資料的緩存，或許會存放了部分代碼和重要的數據，所以需要讀寫校驗 DRAM 好壞。

### 2. SMART Check
檢查 SMART LOG 健康狀態並確認 Critical Warning bit set to 1，若是設定為 "1" 代表測試失敗。

### 3. Volatile Memory Backup
為了避免設備掉電影響資料遺失，必須要加入多個電容零件，保護在發生掉電後，一定的時間內有足夠的電力將所有緩存在 DRAM 的資料刷新到 NAND Flash。

該測試主要針對電容壽命檢測，以避免電容因為長期使用造成損壞或是容值下降不足，原因如下 : 
* 如果容值變低，則會影響SSD的掉電時間，可能會無法保證一定的時間內刷新所有的資料
* 不能針對電容檢測太過於頻繁，會影響電容的使用壽命

### 4. Metadata Validation
讀取並確認所有已寫入 Metadata 的資料完整性。因為有些資料可能很久都不會再更新，如果那些資料量很大，長時間下來會造成元數據不完整的可能性，所以韌體必須要定期或是透過自檢的方式去讀取校驗，確保元數據完整性。

### 5. NVM Integrity
讀寫每一個 NVM 保留區域，確保每一個讀寫 (channel) 都能夠正常，並不會造成資料遺失。

### 6. Data Integrity
- 該測試需要在背景下執行，主要確保所有使用者儲存的資料完整性。
- Extended only

### 7. Media Check
隨機讀取每一個可用的儲存空間，並作讀寫校驗。

### 8. Drive Life
檢查 SSD 壽命是否已經快要結束了。

![[Pasted image 20241218033254.png]]

## 注意事項
當前 SSD 若是正在運行自檢期間，如果控制器收到任何命令，應進行下列動作 :
* Suspend the device self-test operation
	* 暫停目前的自檢操作
* Process and complete that command
	* 處理收到的命令，並完成命令執行
* Resume the device self-test operation
	* 回到剛剛自檢的操作項目