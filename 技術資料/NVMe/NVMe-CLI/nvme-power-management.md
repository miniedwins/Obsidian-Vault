




# 如何執行命令

## 取得控制器支援的電源狀態

說明 : 發送 identify controller 命令， 取得控制器最大支援電源狀態數量。

注意 : 控制器最少要支援一個電源狀態 PS0。

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/identify_controller/Identify_Controller_NPSS.png)

執行命令 :

~~~shell
nvme id-ctrl /dev/nvme0 | grep npss
# npss : 4
~~~



## 取得各個電源的狀態描述

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



## 如何設定電源狀態

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



## 設定與查看 APST 屬性

### 取得目前狀態

說明 : nvme-cli 會將所有的資料顯示出來，不過可以從回傳值 Current value : `0x000001` 取得目前的狀態是被啟用的。

* 每個電源狀態會有一個 `Entry`，總共 64 Bits (8 Bytes)
* 因為控制器最大可以支援 `32` 個電源狀態，所以才會回傳 8 x 32=256 Bytes 
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



### 設定啟用或停用功能

說明 : 發送命令 set-feature 設定 APST

* `value` : 
  * APSTE = 1 ( Enable ) 
  * APSTE = 0 ( Disable )

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
