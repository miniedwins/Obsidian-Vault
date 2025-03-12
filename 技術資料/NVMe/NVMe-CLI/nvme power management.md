## 取得控制器支援的電源狀態

說明 : 發送 Identify Data Controller 命令，取得控制器最大支援電源狀態數量。
備註 : 控制器最少要支援一個電源狀態 PS0。

~~~shell
$ sudo nvme id-ctrl /dev/nvme0 | grep npss
# npss : 4
~~~

![[Pasted image 20250312073326.png]]

## 取得各個電源的狀態描述

說明 : 發送 Identify Data Controller 命令，取得所有電源狀態數量。

~~~shell
$ sudo nvme id-ctrl /dev/nvme0
~~~

執行結果 : 顯示目前控制器擁有五個電源狀態，每個狀態描述最大電源功耗 (MP)，以及進入或是退出的延遲 (Latency) 時間，以及其它等說明等。

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

說明 : 設定 `value=0x04` 將目前的電源狀態切換到 `PS4`。

~~~shell
$ sudo nvme set-feature /dev/nvme0 --feature-id=0x02 --value=0x04
# set-feature:02 (Power Management), value:0x000004
~~~

## 取得目前電源狀態

說明 : 設定 `feature-id=0x02` 取得目前控制器運行在哪一個電源狀態。

~~~shell
$ sudo nvme get-feature /dev/nvme0 --feature-id=0x02
# get-feature:0x2 (Power Management), Current value:0x000004
~~~

## 設定與查看 APST 屬性

~~~shell
$ sudo nvme get-feature -f 0x0c /dev/nvme0
~~~

執行結果 : 
- Current value : `0x000001` 取得目前的狀態是被啟用的。
* APST 狀態結構表，[[Autonomous Power State Transitions#Idle Time Prior to Transition（ITPT）|ITPT]]  以及 [[#Idle Transition Power State （ITPS）|ITPS]] 總共 64 Bits (8 Bytes)。
* 控制器回傳的值
	* 會根據支援多少個 `NPSS` 數量，當前 NPSS= 4（PS0-PS4）。
	* 返回的 APST Entry（8Bytes）* NPSS = 40 Bytes。

~~~shell
get-feature:0xc (Autonomous Power State Transition), Current value:0x000001
       0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
0000: 18 64 00 00 00 00 00 00 18 64 00 00 00 00 00 00 ".d.......d......"
0010: 18 64 00 00 00 00 00 00 20 b4 5f 00 00 00 00 00 ".d........_....."
0020: 20 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
~~~

![[Pasted image 20250311074058.png]]

## 設定啟用或停用 APST

說明 :  `value=1` 設定啟用 APST。

```shell
$ sudo nvme set-feature -f 0x0c /dev/nvme0 -v 0x01
# set-feature:0c (Autonomous Power State Transition), value:00000001
```

說明 :  `value=0` 設定停用 APST。

```shell
$ sudo nvme set-feature -f 0x0c /dev/nvme0 -v 0x00
# set-feature:0c (Autonomous Power State Transition), value:00000000
```
