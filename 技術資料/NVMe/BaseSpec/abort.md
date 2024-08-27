# Abort Command



## 基本介紹

主要使用在取消先前提交命令到 Admin Submission Queue 或者是 I/O Submission Queue。該命令可以取消已經完成的命令 (have already completed)，目前正在執行的命令 (currently be in execution)，或是更深層尚未執行的命令。

若是要取消很大量的 I/O 命令 (例如: 刪除的數量比 ACL 還要來的大)，就需要透過 Delete IO Submission Queue 命令刪除目前的 I/O SQ，然後再使用 Create I/O Submission 命令重新建立 I/O SQ。**(註 : 詳細的說明需要參考 Queue level and Queue Management)**

> 小叮嚀 : Admin Queue 無法被刪除，因為只會有一組 Admin SQ / CQ。



## 如何發送命令

說明 : 指定 SQID 以及哪一個 CID 需要被取消

命令參數 : 

* SQID : 指定哪個 Submission Queue Identifier 
  * Example : 
    * Admin SQ=0x0000
    * I/O SQ=0x0001
* CID : 指定哪個命令需要被取消 
  * Example : 0x0001

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/admin_command_set/abort_cmd_dw10.png)

執行命令 : 

~~~shell
nvme admin-passthru --opcode=0x08 --cdw10=0x00010000 /dev/nvme0
~~~



## 取得控制器最大支援取消數量

說明 : 發送 `Identify Controller` 命令，取得該支援最大取消數量。

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/identify_controller/Identify_Controller_ACL.png)

執行命令 : 

~~~shell
nvme id-ctrl /dev/nvme0 | grep acl
~~~

