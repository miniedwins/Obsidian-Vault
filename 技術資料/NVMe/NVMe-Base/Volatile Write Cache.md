# Volatile Write Cache

## 基本介紹

* 一般都會是啟用狀態，若是關閉 ( Disable Write Cache )，寫入速度則會大幅降低。
* 掉電的時候若是控制器可以保證資料不會遺失，再啟用該功能。
## 檢查控制器支援

說明 : 執行 **Identify Ctrl** 命令確認控制器是否有支援 **Volatile Write Cache**

- Controller Attributes (CTRATT) :
  - 525 Bytes : Volatile Write Cache (VWC)
    - Bit 0
	    - 0 : Don't Support
	    - 1 : Support

~~~shell
$ nvme id-ctrl /dev/nvme0 -H | grep vwc
vwc     : 0x7
~~~

## 如何使用功能 ( Feature )

### 啟用 Write Cache

設定啟用 **Write Cache**

~~~shell
$ nvme set-feature -f 0x06 -v 0x01 /dev/nvme0
set-feature:0x06 (Volatile Write Cache), value:0x00000001, cdw12:00000000, save:0
~~~

### 停用 Write Cache

設定停用 **Write Cache**

~~~shell
$ nvme set-feature -f 0x06 -v 0x00 /dev/nvme0
set-feature:0x06 (Volatile Write Cache), value:00000000, cdw12:00000000, save:0
~~~
### 查詢當前的狀態

取得 **Write Cache** 功能是否啟用或停用

~~~shell
$ nvme get-feature -f 0x06 /dev/nvme0
get-feature:0x06 (Volatile Write Cache), Current value:0x00000001
~~~