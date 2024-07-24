- **安裝方法**
	- OS：Win11_23H2
	- SDK：10.1.22621.2428
	- WDK：10.1.22621.2428
	- WTDF  ( WDK資料包裡面找到下列兩個安裝檔案 )
		- OneCoreUap_WDTF_Desktop_Kit_Content-x64_en-us.msi
		- WDTF_Desktop_Kit_Product-x64_en-us.msi
	- Intel oneAPI Base Tool Kits
		- 選擇 `vtune` 其他選項都取消，安裝完成會得到 `socwatch.exe`
		- 位置 : `C:\Program Files (x86)\Intel\oneAPI\vtune\2024.2\socwatch\64`
- **注意事項**
	- WIN 11 版本要 WDK 相符
	- SDK & WDK 版本一定要相同
	- WDK & SDK 不相同，不能進 Modern Standby，執行 `socwatch` 會報錯

---
# Reference

**SDK :** 
[https://developer.microsoft.com/en-us/windows/downloads/sdk-archive/](https://developer.microsoft.com/en-us/windows/downloads/sdk-archive/)
  
**WDK :** 
https://learn.microsoft.com/zh-tw/windows-hardware/drivers/other-wdk-downloads

**WDTF :** 
[https://learn.microsoft.com/zh-tw/windows-hardware/drivers/wdtf/wdtf-runtime-library](https://learn.microsoft.com/zh-tw/windows-hardware/drivers/wdtf/wdtf-runtime-library)

**Intel oneAPI :**
[https://www.intel.com/content/www/us/en/developer/tools/oneapi/base-toolkit.html](https://www.intel.com/content/www/us/en/developer/tools/oneapi/base-toolkit.html)