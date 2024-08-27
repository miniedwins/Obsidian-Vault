# Firmware Download



## 基本介紹

NVMe Firmware Command 分為以下兩種命令 : 

### Firmware  Image Download 

此功能主要是用來更新全部或是部份的資料 (image) 到控制器上(controller)，也就是可以將新的韌體資料上傳到控制器上，由此方式更新韌體。更新的過程中需要將該更新的資料分成一小部份的方式作為傳遞，每一份傳遞資料都包含了 NUMD and OFST，所以 host 必須要確保資料傳遞的 NUMD and OFST是否有符合 FWUG，可以透過  identify-ctrl 取得，若是沒有符合 FWUG 就會造成韌體更新錯誤。

當所有的資料傳遞完成後，並不會馬上被啟用 (active)，Host 還需要發送 firmware commit，並且在其它  downloading image 之前發送該命令，這個時候控制器就會處理第一次 firmware commit 之前的 firmware image。

(重要) 如果在執行 firmware image download or commit 的期間，發生系統斷電或式控制器被重置等突發事件後，先前傳遞的資料都會被控制器給移除。

*備註 : 建議要越小越好，目前  FADU Sample 所提供的  FWUG value = 1。*

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/identify_controller/Identify_Controller_FWUG.png)

#### NUMD (Number of  Dwords)

這裡是設定傳遞資料的大小，可以由 NUMD 設定較大的傳輸資料 128k bytes，最小要設定成 4k bytes 大小，不過最後都要符合 FWUG 所要求的規範。

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/admin_command_set/firmware_image_download_dw10.png)

#### OFST (Offset)

開始傳遞的資料都會是由 OFST=0h 開始，它必需要隨者傳遞的資料做偏移。也就是每次傳遞的 OFST 位置會不同。例如 : 傳遞資料大小每次為 4k bytes，第一次 OFST 位置就會是 0h，第二次傳遞的資料 OFST 位置就會是從 `0x1000h` 開始，以此方式遞增到傳遞資料結束。

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/admin_command_set/firmware_image_download_dw11.png)

###  Firmware Commit 

主要功能是用來更動 Firmware image or Boot Partitions。當韌體被更動後，firmware commit 會去驗證剛剛  download image 並且修訂所指定的 firmware slot。此時還無法使用當前下載 firmware image，需要等下一次 Controller Level Rest 完成後，指定的 firmware slot 才會被啟動。 

host 會在下一次 Controller Level Rest 去檢查兩件事情， 如下 :

1. 檢查目前所使用的 Firmware Revsion (FR)
2. 檢查 Firmware Slot Information (Log Page : AFI)

host 檢查下列表格就可以得知，下一次控制器重置後，是否需要 active firmware slot

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/log_page/log_page_firmware_slot_information_AFI.png)

#### Commit Action (CA)

當然 Firmware Commit 的功能，不只有以上基礎使用方法，例如 : 

1. 更新韌體後，下一次控制器重置，不啟用先前更新的韌體。
2. 不更新韌體，下一次控制器重置，指定啟用當前已存在的 Firmware Slot。

下列表格代表者執行 Firmware Commit 命令所需要指定的參數 :

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/admin_command_set/firmware_commit_dw10.png)



## 檢查控制器是否支援更新

說明 : 確認控制器是否有支援 `Firmware Image Download` and `Firmware Commit`，沒有支援代表控制器無法執行韌體更新。

Controller Attributes (CTRATT) :

* 257:256 Bytes :
  * Bit 2 : 
    * 1 : 支援韌體更新
    * 0 : 不支援韌體更新

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/identify_controller/Identify_Controller_OASC_Bit2.png)

執行命令 : 

~~~shell
nvme iden-ctrl /dev/nvme0 | grep oacs
# oacs : 0xf
~~~



## 檢查更新後控制器是否支援重置

說明 : 確認控制器有沒有支援 `without reset`  or  `with reset`。

目的 : 主要是為了確認韌體更新後，是否可以直接可以使用韌體而不需要控制器重置 (Controller Reset)。

* Controller Attributes (CTRATT) :
  * 260 Bytes :
    * Bit 4 : 
      * 1 : 控制器支援 without reset，不需要再執行 Controller Reset
      * 0 : 控制器不支援 without reset，需要執行 Controller Reset

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/identify_controller/Identify_Controller_FRMW.png)

執行命令 : 

~~~shell
nvme iden-ctrl /dev/nvme | grep FRMW
# FRMW : 0x16 (沒有支援 without reset)
~~~



## 檢查任韌體支援插槽數量

說明 : 確認控制器支援多少個 `firmware slot` (代表總共可以放多少個韌體)。

Controller Attributes (CTRATT) :

* 260 Bytes :
  * 3:1 Bits : 控制器支援多少個 slots，最少一定有一個，最大支援到七個

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/identify_controller/Identify_Controller_FRMW.png)

執行命令 : 

~~~shell
nvme iden-ctrl /dev/nvme | grep FRMW
# FRMW : 0x16 (支援 3 slots)
~~~



## 如何將新的韌體更新到控制器

### (1) Firmware Image Download

說明 : 首先準備好韌體的路徑，並且透過 nvme-cli 執行 Firmware Image Download 命令

執行命令 : 

~~~shell
nvme fw-download /dev/nvme0 -f firmware/fw_file_name.bin
~~~



### (2) Firmware Commit

說明 : 剛剛下載完成的韌體，還不算完成，接下來我們需要指定將韌體放在哪個 Firmware Slot ，並且下一次 Controller Reset 生效。

**參數 :** 

* slot = 0 (代表韌體要放在哪個 slot 地方)
* action = 1 (覆蓋現有韌體版本，並在下一次的 Controller Level Reset 生效)

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/admin_command_set/firmware_commit_dw10.png)

執行命令 : 

~~~shell
nvme fw-commit /dev/nvme0 --slot=0 --action=1
~~~



### (3) Firmware Reset

說明 : 根據剛剛的 CA 設定，要求要執行 reset 命令，才能真正啟用新的韌體，所以要再執行 Controller Reset 命令

執行命令 : 

~~~shell
nvme reset /dev/nvme0
~~~

取得 Identify Controller Firmware Revision (FR)，確認是否為最新的韌體版本

執行命令 : 

~~~shell
nvme iden-ctrl /dev/nvme0 | grep fr
~~~





