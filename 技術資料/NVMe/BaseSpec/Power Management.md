# Power Management



## 電源管理說明

主要功能是允許主機 (Host) 可以靜態或是動態管理 **NVM Subsystem Power**。

下列說明靜態與動態之間的不同 : 

* `Static Power Management ` 

  靜態電源管理由主機 (Host) 決定分配 NVM subsystem 的最大電源，並將 NVM Express 的電源狀態設定成該耗電量或更少的電量模式。

  

* `Dynamic Power Management`

  動態電源管理由主機 (Host) 決定切換到最適合的電源狀態。Power Manager 會根據這 Power Objective & Performance Objective 做為參考標準，並動態的切換符合的電源模式。

  

  ![](https://github.com/miniedwins/learning/blob/main/nvme/pic/dynamic_power_management.png)



## 電源階段描述 (Power State)

描述各個電源階段表格，說明每個階段有不同的最大電源消耗 (MP)，進入 (Enter) 或是離開 (Exit) 該電源階段的延遲時間，以及不同階段的 `I/O` 效能 (Performance) 與延遲 (Latency) 時間的處理能力。數字越小代表者效能越好，相對的功耗也會越大。

下圖表格是描述各個電源階段的功耗與效能 (參考表格並非真實數據)

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/power_state_descriptor_table.png)

一個控制器最大可以支援 32 個電源狀態，可以發送命令 identify controller 取得 **Number of Power States Supported (NPSS)** 控制器支援數量。目前現階段的應用並不會使用這麼多，根據目前大廠所支援的狀態大多都是 `PS0 ~ PS4`。 `PS0`模式代表最大電源消耗，意思就是說處在這個電源模式下可以發揮工作最大效率，`PS3 & PS4` 模式表示低電源消耗，又稱為 **Non-Operational Power States (NOPS)** ，若是處在 `PS4` 電源狀態下，則該電源消耗是最低的。

*備註 : 每個控制器最少都要支援一個電源狀態，那就是 PS0。*

> 補充 : 有些廠商的控制器韌體只有支援 PS0，可能的原因那就是客戶不考慮耗電量的問題，希望在工作效率上能夠全速運行，並且能夠維持在相對的效能。



若是要了解控制器提供表格的內容，可以發送命令 identify controller 取得電源資訊內容，以下是部份電源表格結構 : 

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/identify_controller/Identify_Controller_Power_State_Descriptor.png)

然後再去尋找每個電源狀態的資料結構的說明，如下圖是部份表格 :

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/identify_controller/Identify_Controller_Power_State_Descriptor_Data_Structure.png)



## 非操作電源模式 (NOPS)

**Non-Operational Power States (NOPS) :** 定義是當控制器沒有任何 I/O 命令需要處理，並且閒置了一段時間後，就會進入到非操作電源模式。因為是主機 (Host) 自動切換電源狀態，前提條件下必須要啟用 `APST`。

從主機的角度來看，就是沒有任何 `Pending I/O` 提交到控制器，主機就會發送 **Set Features Command** 切換目前的 **power state to non-operational power state**，在這段命令還沒執行完畢前，是不會再提交任何的 I/O 命令。因為控制器是平行處理 (parallel) 各種不同的命令，若是同時執行 `Admin & IO` 命令 ，可能會導致切換到不可預期電源狀態。

值得注意的一點，無論 `APST`是否有被啟用， 一旦電源狀態位在 `NOPS` 狀態下，當有任何的 I/O 命令被提交，控制器必須要切換到最近的 **operational power state**。

例如 : 電源狀態位在 `PS4` 的時候，若是控制器有收到 I/O 命令，就可能會將目前的電源狀態切換到 `PS0` 或其它能夠運行 I/O 命令的電源狀態，因為`NOPS` 狀態是不允許處理 I/O 命令 。比較正確的說法，當有一個 **I/O Submission Queue Tail Doorbell** 暫存器的值被主機寫入，代表有 I/O 命令需要被控制器提取以及處理。

當位在 NOPS 狀態，控制器還是可以運行其它非 I/O 命令，例如 : 閒置時候的背景操作，這個時候可能會超過控制器宣告該電源狀態的最大功耗(MP)，以下的操作是可以在 NOPS 狀態中運行 :

- servicing a memory-mapped I/O (MMIO) 
- configuration register access
- processing a command submitted to the Admin Submission Queue 

根據上述的結論，若是控制器有支援 **Non-Operational Power State Permissive Mode**，是可以允許控制器暫時超過該電源階段所宣告的最大功耗 (MP)。它的條件是在 `NOPS` 狀態下，允許背景執行以上所說的非 I/O 操作。

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/non_operational_power_state_config.png)

*備註 : Non-Operational Power State Permissive Mode Disable (待續 ...)*



## 自動電源狀態切換 (APST)

**Autonomous Power State Transitions (APST) :** 提供主機一個電源狀態自動切換的機制，能讓主機可以切換電源階段 (a non-operational power state may autonomously transition to another non-operational power state)。它的進入的條件是當控制器連續閒置 (Idle) 一段時間，並且超過所指定的閒置時間，主機就會轉換電源狀態到 NOPS。

注意 : 如果電源階段是在 **Non-Operational States (NOPS)**，這個時候控制器可能會去運行像是 **Device Self-Test (DST)** 操作，那就可能會超過控制器所宣告該電源階段的最大功耗值 (MP)，此時控制器不應該切換到 NOPS。

*備註 : Controller idle means that there are no commands outstanding to any I/O Submission Queue*



## 如何執行命令

### 取得控制器支援的電源狀態

說明 : 發送 identify controller 命令， 取得控制器最大支援電源狀態數量。

注意 : 控制器最少要支援一個電源狀態 PS0。

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/identify_controller/Identify_Controller_NPSS.png)

執行命令 :

~~~shell
nvme id-ctrl /dev/nvme0 | grep npss
# npss : 4
~~~



### 取得各個電源的狀態描述

說明 : 發送 identify controller 命令， nvme-cli 會回傳整理好的資訊。

執行命令 :

~~~shell
nvme id-ctrl /dev/nvme0
~~~

執行結果 : 

顯示目前控制器擁有五個電源狀態，每個狀態描述最大電源功耗 (MP)，以及進入或是退出的延遲 (Latency) 時間，以及其它等說明等。

~~~shell
ps    0 : mp:3.00W operational enlat:0 exlat:0 rrt:0 rrl:0
          rwt:0 rwl:0 idle_power:- active_power:-
ps    1 : mp:2.00W operational enlat:0 exlat:0 rrt:1 rrl:1
          rwt:1 rwl:1 idle_power:- active_power:-
ps    2 : mp:2.00W operational enlat:0 exlat:0 rrt:2 rrl:2
          rwt:2 rwl:2 idle_power:- active_power:-
ps    3 : mp:0.1000W non-operational enlat:1000 exlat:1000 rrt:3 rrl:3
          rwt:3 rwl:3 idle_power:- active_power:-
ps    4 : mp:0.0050W non-operational enlat:400000 exlat:90000 rrt:4 rrl:4
          rwt:4 rwl:4 idle_power:- active_power:-
~~~



### 如何設定電源狀態

說明 : nvme-cli 指定參數 (Power States)，即可設定或是取得電源狀態。

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/feature/power_management_id_02.png)

**設定電源狀態**

說明 : 給定一個 `value=0x04` 將目前的電源狀態切換到 `PS4`。

~~~shell
nvme set-feature /dev/nvme0 --feature-id=0x02 --value=0x04
# set-feature:02 (Power Management), value:0x000004
~~~

**取得目前電源狀態**

說明 : 給定一個 `feature-id=0x02` 取得目前控制器運行在哪一個電源狀態，目前電源模式是在 `PS4`。

~~~shell
nvme get-feature /dev/nvme0 --feature-id=0x02
# get-feature:0x2 (Power Management), Current value:0x000004
~~~



### 設定與查看 APST 屬性

#### 取得目前狀態

說明 : nvme-cli 會將所有的資料顯示出來，不過可以從回傳值 Current value : `0x000001` 取得目前的狀態是被啟用的。

* 每個電源狀態會有一個 `Entry`，總共 64 Bits (8 Bytes)
* 因為控制器最大可以支援 `32` 個電源狀態，所以才會回傳 8*32=256 Bytes 
* 目前控制器只支援五種狀態，所以之後的值都會是 `0x00`

**APST 狀態結構表**

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/feature/autonomous_power_state_transition_data_structure.png)

執行命令 :

~~~shell
nvme get-feature -f 0x0c /dev/nvme0
~~~

執行結果 : 

~~~shell
# 執行結果
get-feature:0xc (Autonomous Power State Transition), Current value:0x000001
       0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
0000: 18 64 00 00 00 00 00 00 18 64 00 00 00 00 00 00 ".d.......d......"
0010: 18 64 00 00 00 00 00 00 20 b4 5f 00 00 00 00 00 ".d........_....."
0020: 20 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
0030: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
0040: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
0050: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
0060: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
0070: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
0080: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
0090: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
00a0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
00b0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
00c0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
00d0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
00e0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
00f0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
~~~



#### 設定啟用或停用功能

說明 : 發送命令 set-feature 設定 APST

* `value` : 
  * APSTE=1 (Enable) 
  * APSTE=0 (Disable)

**啟用 APST**

說明 : 給定一個 `value=1` 設定為啟用功能

~~~shell
nvme set-feature -f 0x0c /dev/nvme0 -v 0x01
# set-feature:0c (Autonomous Power State Transition), value:00000001
~~~

**停用 APST**

說明 : 給定一個 `value=0` 設定為停用該功能

~~~shell
nvme set-feature -f 0x0c /dev/nvme0 -v 0x00
# set-feature:0c (Autonomous Power State Transition), value:00000000
~~~
