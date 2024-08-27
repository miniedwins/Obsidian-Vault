# Endurance Groups


## 基本介紹

Endurance Groups 可以管理 Single NVM Set 或是管理多個 NVM Sets，每一個 Group 都會有一個 ID 編號，標示目前有哪些 NVM Sets 是位在該哪一個 Group，而每一個 NVM Set 的屬性 (Endurance Group Identifier)，描述是屬於哪一個 Endurance Group。


>  備註 : Endurance Group Identifier value of 0h is reserved


NVM Group ID 的設置，這個可以讓SSD進行磨損均衡的管理。如果只有一個NVM Set 和 Endurance Group ID關聯，磨損均衡范圍不能跨越該 Set，也就是多個 Sets 只能可以被一個 Group 管理，但是主機端可以選擇跨 Set 進行壽命管理。

由下圖可以得知 : Groups Y 管理了 NVM Set A and Set B，Groups Z 只能管理 NVM Set C。

**Endurance Group and Associated NVM Sets**

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/endurance_gorup_and_associated_nvm_sets.png)



## 檢查控制器是否支援

說明 : 發送 Identify Controller 命令來確認是否有支援 Endurance Groups。

* Controller Attributes (CTRATT) : 
  * 99:96 Bytes : Bit 4 (Endurance_Groups)
    * 0 : Don't Support
    * 1 : support

![endurance_group](https://github.com/miniedwins/learning/blob/main/nvme/pic/identify_controller/Identify_Controller_CTRATT_Bit4_Endurance_Groups.png)

發送命令 : 

~~~shell
# 備註: 尚未驗證命令是否有誤 !!!

nvme id-ctrl | grep ctratt
~~~



## 確認最大支援數量

說明 : 每個 Groups 都會擁有一組 Id 編號，發送 Identify Controller 命令來確認該控制器最大支援多少個數量。

* 341:340 Bytes : Endurance Group Identifier Maximum (ENDGIDMAX)

![Endurance Group Identifier Maximum](https://github.com/miniedwins/learning/blob/main/nvme/pic/identify_controller/Identify_Controller_ENDGIDMAX.png)

發送命令 : 

~~~shell
# 備註: 尚未驗證命令是否有誤 !!!

nvme id-ctrl | grep endgidmax
~~~



## 查詢日誌資訊內容 (log page)

說明 :  每個 Endurance Group 都有會一個 log page (512 Bytes) 描述已使用空間、可用空間、或是壽命資訊等等。

**簡單示意圖畫面** : 

![示意圖](https://github.com/miniedwins/learning/blob/main/nvme/pic/log_page/log_page_endurance_group.png)

發送命令 :  

~~~python
# 備註: 尚未驗證命令是否有誤 !!!

# for human readable format
nvme endurance-log /dev/nvme0

# for raw Endurance log to a file
nvme endurance-log /dev/nvme0 --output=binary > endurance_log.raw

# for get-log command
nvme get-log /dev/nvme0 -log-id=0x09 --log-len=512 --raw-binary > log_page_2.raw
~~~
