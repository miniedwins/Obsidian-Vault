# NVM Set

## 基本介紹

NVM Set 就是一組邏輯上與物理上的集合，每一個 Set 可以集合單一個 namespace 或是多個不同的 namespaces。而一個 namesapce 只允許在一個 NVM Set 裡面，不能同時存在多個 Set 之中。還有一點必須要注意的是，每一個被建立的 NVM Set 都一定會關聯一個 Enudrance Group (非常重要的知識)。

**網路上所得到的資料說明 (待確認)**

Set是一組Flash LUN的集合，所以稱之為一個Set。比如說我們可以知道我們現在一個固態硬盤有4通道、8通道、10通道，每個通道上還會有4個、8個、10個LUN，這些LUN可以拆分成一個一個Set，在Set上通過協議劃分成不同的Namespace，可以在協議中確定的要求每一個Namespace只屬於一個Set或者多個Set。這樣當用戶訪問其中一個Namespace，這部分空間是必須要落在一個確定的Flash LUN上面，也就是一個確定的Set上面。

下圖顯示不同 NVM Set 所包含的 namespaces，NVM Set A 包含了 (NS A1, NS A2, NS A3)，而 NVM Set B 包含了 (NS B1 and NS B2)，最後 NVM Set C 只包含了 (NS C1)。而且每一個 Set 都可以包含未分配的 namespace 空間。

> 備註 : An NVM Set Identifier value of 0h is reserved and is not a valid NVM Set Identifier

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/nvm_sets_and_associated_namespaces.png)



## 檢查控制器是否支援

說明 : 發送 **Identify Controller** 命令來確認是否有支援 NVM Set。

- Controller Attributes (CTRATT) :
  - 99:96 Bytes : Bit 2 (NVM Sets)
    - 0 : Don't Support
    - 1 : Support

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/identify_controller/Identify_Controller_CTRATT_Bit2_NVM_Sets.png)

發送命令 : 

~~~shell
# 沒有樣品測試，尚未驗證命令是否有誤!
nvme id-ctrl | grep ctratt
~~~



## 確認最大支援數量

說明 : 每個 NVM Set 都會擁有一組 Id 編號，發送 **Identify Controller** 命令來確認該控制器最大支援多少個數量。

* 339:338 Bytes : NVM Set Identifier Maximum (NSETIDMAX)

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/identify_controller/Identify_Controller_NSETIDMAX.png)

發送命令 :

~~~shell
# 沒有樣品測試，尚未驗證命令是否有誤!
nvme id-ctrl | grep nestidmax
~~~



## 建立 NVM Set

說明 : 建立 NVM Set 需要透過主機端 (Host) 發送 **Namespace Management** 命令，並且在建立 **NS** 的時候指定 NVM Set Identifier **(NVMSETID)** 屬性值，設定前需要確認控制器最大支援的數量 **(NSETIDMAX)**，以及該屬性值不能超過 `0xFF` 。

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/admin_command_set/namespace_management_host_software_fields.png)

發送命令 : 

~~~shell
# 沒有樣品測試，尚未驗證命令是否有誤!
nvme create-ns /dev/nvme0 -s 976773168 -c 976773168 -f 0 -d 0 -m 0 -i 1
~~~



## 列出 NVM Set 

說明 : 執行 **Identify NVM Set list** 命令，可以列出目前所有啟用的 NVM Set，並且查看每個 **NVM Set Attributes**。

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/identify_nvm/Identify_NVM_Set_Attributes%20Entry_.png)

發送命令 :

~~~shell
# 沒有樣品測試，尚未驗證命令是否有誤!

# for human readable format
nvme id-nvmset /dev/nvme0

# for binary format to file
nvme id-nvmset /dev/nvme0 --output-format=binary > id_nvmset.raw
~~~



## 顯示 NVM Set  Identifier

說明 : 執行 **Identify NS** 命令，找出當前的 NS 所屬的 **NVM Set Identifer**。

* 101:100 Bytes : NVM Set Identifier (NVMSETID)

發送命令 :

~~~shell
# 沒有樣品測試，尚未驗證命令是否有誤!
nvme id-ns /dev/nvme0 | grep nvmsetid
~~~



## 顯示 Endurance Group Identifier

說明 : 執行 **Identify NS** 命令，找出當前的 NS 所屬的 **Endurance Group Identifer**。

* 103:102 Bytes : Endurance Group Identifier (ENDGID)

發送命令 : 

~~~shell
# 沒有樣品測試，尚未驗證命令是否有誤!
nvme id-ns /dev/nvme0 | grep endgid
~~~
