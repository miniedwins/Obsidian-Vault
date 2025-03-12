### 檢查 Format NVM 屬性
說明 : 控制器必須要支援這個 `format NVM`，所以我們應該要檢查的是 `FNA` 屬性功能是否有符合需求。

524 Bytes (FNA) : 
* Bit 2 : 代表是否支援 `cryptographic erase`
  * 0 : Don't Support
  * 1 : Support
* Bit 1 : 代表是否支援 `all namespaces` 或是 `particular namespace`
  * 0 : Don't support all namespaces
  * 1 : Supprot all namespaces
* Bit 0 : 不翻譯，保留原文說明 
  * 有部分內容暫時無法了解

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/identify_controller/Identify_Controller_FNA.png)

發送命令 : 

~~~shell
nvme id-ctrl | grep fna
~~~

### 如何執行 Secure Erase
說明 : 這裡只說明 Secure Erase 如何執行，若是沒有指定其他功能設定， `nvme-cli ` 會使用初始設定的方式執行。

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/admin_command_set/format_nvm_cmd_dw10.png)

發送命令 : 

~~~shell
# 使用初始設定值
nvme format /dev/nvme0n1

# 不使用 nvme-cli 初始設定值
nvme format /dev/nvme0 --namespace-id=1 --ses=1 --pi=1
~~~

