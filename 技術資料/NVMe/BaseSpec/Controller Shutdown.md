# Controller Shutdown
## 介紹

由主機端發起通知，透過設定暫存器 ( Controller Property ) 方式進行關閉控制器。例如 : 設定暫存器`CC.SHN=01` ( Normal shutdown notification )，代表主機端通知控制器要進行正常關機流程。此時主機端會去觀察暫存器 Controller Status ( CSTS )，這個暫存器是由控制器更新，並且回報當前關閉進行的狀態，一旦 `CSTS.SHST`設定值為 `10b`，代表進行關閉控制器已經完成。

**Shutdown Notification ( SHN ) 三種類型通知** : 
* ( 00b ) : No notification; no effect
* ( 01b ) : Normal shutdown notification
* ( 10b ) : Abrupt shutdown notification

**Shutdown Status ( SHST ) 三種關機處理狀態 :**
* ( 00b ) : Normal operation (no shutdown has been requested
* ( 01b ) : Shutdown processing occurring
* ( 10b ) : Shutdown processing complete
## 關機操作流程

當進行 **Shutdown Processing** 主機端需要遵循協議規範的關機流程。

**Controller Shutdown 又可以分為兩種類型 :** 
* Memory-based Transport Controller Shutdown
	* Normal Controller Shutdown
	* Abrupt Shutdown
* Message-based Transport Controller Shutdown
### Memory-based Transport
 
如果控制器的暫存器被設定成 CC.EN=1，Normal & Abrupt 它們的操作流程如下 : 

**Normal Controller Shutdown**

 * 停止提交任何新的 I/O 命令給控制器，以及完成所有已經送出去的命令。
 * 若是控制器有建立 I/O Queues，主機端應該要發送命令刪除 I/O Queues ( Submission & Completion )，若是佇列中還有剩餘未完成命令會一併被中止。
 * 主機端設定 `CC.SHN=01b`，進行 **Controller shutdown operation**。
 * 當控制器會更新 `CSTS.SHST` 狀態直到 `CSTS.SHST=10b`，並且 `CSTS.ST` 該值被清除為０。

**Abrupt Shutdown**

這裡的操作流程與 `Normal Shudown` 沒有差異，僅有主機端設定 `CC.SHN=10b`。

>( 疑問 ) : 
 >(1) 一般只有不正常斷電的狀態下，才有可能發生 **Abrupt Shutdown**
 >(2) 若是不正常斷電，主機端還有時間可以立刻寫入`CC.SHN=10b` ?



### Message-based Transport

( 狀態 ) 暫定不寫