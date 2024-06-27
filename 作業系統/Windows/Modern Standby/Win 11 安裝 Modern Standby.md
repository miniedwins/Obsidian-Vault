
- 安裝方法 ( Example : Win11 23H2):
	- Win11 (23H2)
	- SDK 10.1.22621.2428
	- WDK 10.1.22621.2428
	- WTDF ( 從WDK資料包裡面找到檔案, 安裝方法在下面圖示)
		- OneCoreUap_WDTF_Desktop_Kit_Content-x64_en-us.msi
		- WDTF_Desktop_Kit_Product-x64_en-us.msi
	- Intel oneAPI Base Tool Kits
		- 只要選擇 vtune其他選項都取消  安裝完成會得到socwatch.exe
		- 位置 : C:\Program Files (x86)\Intel\oneAPI\vtune\2024.2\socwatch\64

- 注意事項 :
	- WIN 11 版本要 WDK 相符
	- SDK & WDK 一定要相同
	- WDK & SDK 不相同, 不能進 Modern Standby, socwatch 會報錯

SDK : 
[https://developer.microsoft.com/en-us/windows/downloads/sdk-archive/](https://developer.microsoft.com/en-us/windows/downloads/sdk-archive/)
  
WDK : 
https://learn.microsoft.com/zh-tw/windows-hardware/drivers/other-wdk-downloads

WDTF : 
[https://learn.microsoft.com/zh-tw/windows-hardware/drivers/wdtf/wdtf-runtime-library](https://learn.microsoft.com/zh-tw/windows-hardware/drivers/wdtf/wdtf-runtime-library)

Intel oneAPI :
[https://www.intel.com/content/www/us/en/developer/tools/oneapi/base-toolkit.html](https://www.intel.com/content/www/us/en/developer/tools/oneapi/base-toolkit.html)