## **安裝方法**

1. **作業系統**：    
    - Windows 11 (版本：23H2)
2. **開發工具：SDK**    
    - 版本：10.1.22621.2428
3. **Windows 驅動開發工具：WDK**    
    - 版本：10.1.22621.2428
4. **Windows 驅動測試框架：WTDF**    
    - 在 WDK 資料包中找到以下兩個安裝檔案進行安裝：
        - `OneCoreUap_WDTF_Desktop_Kit_Content-x64_en-us.msi`
        - `WDTF_Desktop_Kit_Product-x64_en-us.msi`
5. **Intel oneAPI Base Toolkits**    
    - 安裝過程中僅選擇 `vtune`，取消其他選項，完成後將獲得 `socwatch.exe`。
    - **檔案路徑**：
	    - C:\Program Files (x86)\Intel\oneAPI\vtune\2024.2\socwatch\64
## **注意事項**

1. **版本相容性**    
    - Windows 11 的版本需要與 WDK 相匹配。
2. **SDK & WDK 版本一致**
    - 確保 SDK 和 WDK 的版本相同，避免兼容性問題。
3. **版本不匹配的影響**
    - 如果 WDK 和 SDK 版本不同，將無法進入 Modern Standby 模式。
    - 此時執行 `socwatch` 會出現錯誤提示。

## Reference

**SDK :** 
[https://developer.microsoft.com/en-us/windows/downloads/sdk-archive/](https://developer.microsoft.com/en-us/windows/downloads/sdk-archive/)
  
**WDK :** 
https://learn.microsoft.com/zh-tw/windows-hardware/drivers/other-wdk-downloads

**WDTF :** 
[https://learn.microsoft.com/zh-tw/windows-hardware/drivers/wdtf/wdtf-runtime-library](https://learn.microsoft.com/zh-tw/windows-hardware/drivers/wdtf/wdtf-runtime-library)

**Intel oneAPI :**
[https://www.intel.com/content/www/us/en/developer/tools/oneapi/base-toolkit.html](https://www.intel.com/content/www/us/en/developer/tools/oneapi/base-toolkit.html)