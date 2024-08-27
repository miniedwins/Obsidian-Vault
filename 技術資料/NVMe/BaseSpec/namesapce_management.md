# Namesapce Management



## Introduction

主要目的用來管理 NS 空間建立的大小，掛載，刪除以及其它對 NS 空間的屬性定義等設定，這些設定可以從 Namespace Management - Host Software Filed 來設定所有屬性值，前提控制器也必須要支援 **Namespace Management Command**。

## Namespace

`Namespace` 是一個對使用者硬碟空間的邏輯劃分的表示方法。可以代表一個完整的區塊 (whole blocks) 或是某一個區塊 (blocks)，也就是我們可以劃分多個使用者空間，來應對不同場景的變化。這些被劃分的空間是由 `logical block address (LBA)`。每個空間 (namespace) 都會擁有一個 `identifier` 來標示，而控制器會透過這個 NSID (Namespace ID) 讀寫該空間的資料內容。



### Valid and Invalid NSIDs

**Valid NSIDs**

每個 namespace 都擁有自己唯一的 NSID。有效的範圍 : `1~NN`，要注意的是，起始空間都是由 `NSID=1` 開始，最大支援空間數量是由控制器決定，可由 `Identify Ctrl Data` 取得。

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/namespace_management_nn.png)



**Invalid NSIDs**

* 無效範圍是 `NSID=0` 以及 `NN+1`
* `FFFFFFFFh` 表示 `broadcast` 可以由該值來指定所有的 Namespace。



### Allocated and Unallocated NSID

當透過 `Namespace Management` 成功建立 Namespace，此時狀態就會是 `Allocated` ，表示該邏輯區塊範圍已經劃分給該空間。另外那些沒有沒有分配的邏輯塊以及 NSID 就是 `Unallocated`。



### Active and Inactive NSID

當我們已經建立好 `Allocated namesapce`，除了不能被作業系統識別外，也不能拿來讀寫資料，必須還要執行 `Namesapce Attach`命令掛載在某一個控制器上，成為一個 `Active Namesapce`，該空間才可以被讀寫，也稱為 `Active NSID`。也就是說任何一個 Allocated NSID 只要沒有被控制器掛載，都是 `Inactive`，`Unallocated NSID` 因為本身就是一個 `Inactive NSID`。

> 注意 :  如果只指定一個 `Inactive NSID` 讀寫資料，控制器會返回一個 `Abort Command with status Invalid Namespace or Format`



**下圖表示：Namespace Id Types:** 

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/namespace_management_nsid_type.png)



## 如何執行命令

### 確認控制器 ID

目的 : 確認目前的控制器的 ID 編號，才能針對哪個控制器執行命令 (假設有兩個以上的控制器)。

說明 : 若是有多控制器支援共用同一個 Namesapce 關係，所以需要指定 Controller Id 才可以掛載或是卸載 Namesapce。

執行 : 發送 Identify Ctroller 命令，取得 `cntlid` 資訊

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/identify_controller/Identify_Controller_CNTLID.png)

~~~Shell
nvme id-ctrl /dev/nvme0 | grep cntlid
# cntlid : 1
~~~



###  檢查控制器是否支援

說明 : 檢查 Controller 是否有支援 Namespace Management

執行 : 發送 Identify Controller 命令， 取得 `Optional Admin Command Support (OACS)`

- Controller Attributes (CTRATT) :
  - 257:256 Bytes : Optional Admin Command Support (OACS)
    - Bit 3 :
      - 0 : Don't Support
      - 1 : Support

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/identify_controller/Identify_Controller_OASC_Bit3.png)

發送命令 : 

~~~Shell
nvme id-ctrl /dev/nvme0 | grep oacs
# oacs : 0xf
~~~



### 如何取得硬碟空間容量

目的 : 需要先取得該硬碟空間大小，確定目前使用容量使用狀況，才可以正確的建立 Namsespace。

執行 : 發送 Identify Controller 命令， 取得 `tnvmcap & unvmcap` 資訊

下列參數描述建立 `Namespace` 可使用空間與未配置空間大小

* `tnvmcap` : 總共可用空間大小 ( Bytes )
* `unvmcap` : 未分配空間大小 ( Bytes )



*提示 : 若需要再重新分配所有空間，需要先刪除目前已使用的 Namespace*

發送命令 : 

~~~Shell
nvme id-ctrl /dev/nvme0
~~~

執行結果 : 基本上原廠出貨都只會只建立一個 Namespace，因此未分配空間 (unvmcap) 就會是 `zero`。

~~~bash
tnvmcap : 960998932480
unvmcap : 0
~~~

所以當未分配空間為零的時候，但是又想要建立多個 Namespaces，就必須要先刪除目前已經建立的 Namespace。

此時未分配空間 (unvmcap) 就會有未配置的容量可以建立新的 Namespace

~~~shell
tnvmcap : 960998932480
unvmcap : 960998932480
~~~



### 如何建立多個空間

* 需要先取得該硬碟空間大小，確定目前使用容量使用狀況，才可以正確的建立 NS
* 若是沒有可用空間，必須要先刪除既有的空間，才可以建立新的空間
* 需要了解屬性定義 (Host Software Specified Fields)



下圖表格 `Namesapce Management` 設定，詳細說明需要參考SPEC，以下為基本參數說明 : 

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/namespace_management_host_software_specified_fields.png)

**參數說明 :** 

* nsze (-s) : The namespace size ( unit : Block，描述此NS最大邏輯空間)
* ncap (-c) : The namespace capacity (unit : Block，最大可以被分配使用空間，通常設定的大小會與 `NSZE` 相同)
* flbas (-f) : The namespace formatted logical block size setting (指定該空間的 block size)
  * set 0 : 512 Bytes 
  * set 1 : 4096 Bytes 
* dps (-d) : The data protection settings (端對端資料保護)
  * Bits 2:0 : 000b (Protection information is not enabled)
  * Bits 2:0 : 001b (Protection information is enabled, Type 1)
  * Bits 2:0 : 010b (Protection information is enabled, Type 2)
  * Bits 2:0 : 011b (Protection information is enabled, Type 3)
  * Bits 2:0 : 100b to 111b (Reserved)
* nmic (-m) : Namespace multipath and sharing capabilities (支援多個控制器)
  * Bit 0 : 0 (Doesn't Support) 
  * Bit 0 : 1 (Support)



#### (1) Create Namespace

透過 `IDMA` 計算要建立的容量大小，我們建立兩個空間大小 500GB and 460GB，並且指定每個空間的 Block size : `512 Bytes`

不啟用端對端資料保護 (dps=0)，以及不共享這個空間給其它控制器使用 (nmic=0)。

>*備註 : 不同的空間的 block size 可以設定不同，例如 :* 
>
>1. *Namaspace 1 : 512 Bytes*
>2. *Namesapce 2: 4096 Bytes*

~~~shell
# Create a Namespace 500GB
sudo nvme create-ns /dev/nvme0 -s 976773168 -c 976773168 -f 0 -d 0 -m 0

# Create a Namespace 460GB
sudo nvme create-ns /dev/nvme0 -s 898633008 -c 898633008 -f 0 -d 0 -m 0
~~~



#### (2) Attach Namespace

此時建立完成後還無法使用該空間，需要控制器掛載該空間才可以被作業系統使用

~~~shell
# Attach a Namespace ID 1
sudo nvme attach-ns /dev/nvme0 -n 1 -c 1

# Attach a Namespace ID 2
sudo nvme attach-ns /dev/nvme0 -n 2 -c 1
~~~

 可以使用 `nvme list` 命令，確認目前掛載的 Namespaces ID

~~~shell
# List All Attached NSID
sudo nvme list /dev/nvme0
~~~



#### (3) Detach Namespace

移除控制器所掛載的空間，被移除的空間就不會被作業系統所使用

*備註 : 不代表這些空間已被刪除，也可以再被控制器重新掛載*

~~~shell
# Detach Namespace ID 1
sudo nvme detach-ns -n 1 -c 1 /dev/nvme0

# Detach Namespace ID 2 
sudo nvme detach-ns -n 2 -c 1 /dev/nvme0
~~~

Namespaces ID 不會被顯示出來

~~~shell
# List All Attached NSID
sudo nvme list /dev/nvme0
~~~



#### (4) Delete Namespace

將建立的空間刪除，此時該空間的資料會被清除

~~~shell
# Delete Namespace ID 1
sudo nvme delete-ns -n 1 -c 1 /dev/nvme0

# Delete Namespace ID 2 
sudo nvme delete-ns -n 2 -c 1 /dev/nvme0
~~~

這個時候可以發送 Identify Controller  確認 `tnvmcap & unvmcap`

~~~shell
nvme id-ctrl /dev/nvme0
~~~

執行結果 :  因為刪除了所有建立的空間，所以`tnvmcap & unvmcap` 應該要相等

~~~shell
tnvmcap : 960998932480
unvmcap : 960998932480
~~~



## IDEMA 

以下公式可以選擇 Block Size 大小換算，這裡分別為 512 Bytes 以及 4096 Bytes。

### 公式計算

#### 512 Bytes

LBA counts :  (97,696,368) + (1,953,504 * (GBytes – 50))

#### 4096 Bytes

LBA counts :  (12,212,046) + (244,188 * (GBytes – 50))



### 範例教學

Total Bytes : 960,998,932,480 (960GB)

**512 Bytes** 

* 500GB : 97,696,368 + (1,953,504 * (500 – 50)) = 976,773,168
* 460GB : 97,696,368 + (1,953,504 * (460 – 50)) = 898,633,008

**4096 Bytes**

* 500GB : 12,212,046 + (244,188 * (500 – 50)) = 122,096,646
* 460GB : 1,2212,046 + (244,188 * (460 – 50)) = 112,329,126
