## 概要說明

由主機端發起通知，透過設定暫存器 ( Controller Property ) 方式進行關閉控制器。例如 : 設定暫存器`CC.SHN=01` ( Normal shutdown notification )，代表主機端通知控制器要進行正常關機流程。此時主機端會去觀察暫存器 Controller Status ( CSTS )，這個暫存器是由控制器更新，並且回報當前關閉進行的狀態，一旦 `CSTS.SHST`設定值為 `10b`，代表進行關閉控制器已經完成。
## 關機類型與狀態

### 三種類型通知

* ( 00b ) : No notification; no effect
* ( 01b ) : Normal shutdown notification
* ( 10b ) : Abrupt shutdown notification
### 三種關機處理狀態

* ( 00b ) : Normal operation ( no shutdown has been requested )
* ( 01b ) : Shutdown processing occurring
* ( 10b ) : Shutdown processing complete
## 操作流程

Controller Shutdown 又可以分為兩種類型
* **Memory-based Transport Controller Shutdown**
	* Normal Controller Shutdown
	* Abrupt Shutdown
	* RTD3 with Normal Controller Shutdown
* **Message-based Transport Controller Shutdown**
	* 這裡是說明的是另外一種通訊協議 ( 例如 : TCP/IP over PCIe )
### Memory-based Transport
 
如果控制器的暫存器被設定成 CC.EN=1，Normal & Abrupt 它們的操作流程如下 : 
#### (1) Normal Controller Shutdown

 * 停止提交任何新的 I/O 命令給控制器，以及完成所有已經送出去的命令。
 * 若是控制器有建立 I/O Queues，主機端應該要發送命令刪除 I/O Queues ( Submission & Completion )，若是佇列中還有剩餘未完成命令會一併被中止。
 * 主機端設定 `CC.SHN=01b`，通知控制器進行 Controller shutdown operation。
 * 控制器會更新 `CSTS.SHST` 狀態直到 `CSTS.SHST=10b`，並且 `CSTS.ST` 該值被清除為 "0"。
#### (2) Abrupt Shutdown

這裡的操作流程與 `Normal Shudown` 沒有差異，僅有主機端設定 `CC.SHN=10b`。

>( 疑問 ) : 
 >(1) 一般只有不正常斷電的狀態下，才有可能發生 "Abrupt Shutdown"
 >(2) 為什麼主機端可以設定通知 "Abrupt Shutdown"
 >(3) 若是不正常斷電，主機端還有時間可以立刻寫入`CC.SHN=10b` ?
#### (3) RTD3 with Normal Controller Shutdown

控製器進入低功耗狀態（RTD3）的時間。在關閉操作完成之前，主機需要等待至少RTD3進入延遲時間，可以從 Identify Controller 取得 **"D3 Entry Latency"** 。如果 **D3 Entry Latency=0h**，那麼主機至少應該等待1秒鐘。**"不建議"** 通過 CC.EN 欄位停用控製器，通過這種方式停用控製器會導致 `Controller Reset`，這可能會影響完成關閉處理所需的時間。

當 `CSTS.ST=0` 被清除為 "0" 時，以及 `CSTS.SHST=10b`被設定 "10b"，表明控製器不再處於活動狀態，已完成所有必要的處理。 無論 CC.EN 的值如何，這個時候斷電都是安全的。

>備註 : 關閉處理進行時，控制器會中止任何命令，並返回 "Power Loss Notification" 的狀態程式碼。

**控製器報告關閉處理完成後，如何重新啟動控製器** 

以下描述是若是當前 CC.EN 設定‘1’或是‘0’主機端要如何設定 ?

- **如果 CC.EN 被設定為‘1’**：那麼必須執行**Controller Reset**，即將**CC.EN**從‘1’清除為‘0’（停用控製器），然後再重新啟用它。
    
- **如果 CC.EN 已經清除為‘0’**：那麼控製器必須被**啟用**，即將 **CC.EN**從‘0’設定為‘1’（啟用控製器）。