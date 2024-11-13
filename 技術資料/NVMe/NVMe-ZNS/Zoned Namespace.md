# Zoned Namesapce



## 基本介紹

(未完成 ...)

Active Zone

* ZSIO:Implicitly Opened state,
* ZSEO:Explicitly Opened state
* ZSC:Closed state

---

Zone Descriptor : The data structure that contains information about a zone.

(說明) 每一個 zone 都會有一個 Descriptor，描述該 zone 的狀態

Each zone has an associated **Zone Descriptor** that contains a set of attributes. **A Zone Management Receive command** may be used to retrieve one or more Zone Descriptors

(說明) 使用 Zone Management Receive 命令 取得 一個或是多個 Zone Descriptor 

The host may use the **Zone Management Receive** command to determine the current write pointer for a zone.

(說明) Host 發送 Zone Management Receive 可以取得目前的 write pointer (a zone) 位置

The write pointer for a zone in the ZSE:Empty state, the ZSIO:Implicitly Opened state, the ZSEO:Explicitly Opened state, or the ZSC:Closed state shall be increased by the number of logical blocks written on successful completion of a write operation.

(說明) 在這幾個狀態下若是寫入操作成功，write pointer 會增加

---

## Zone Characteristics 

(未完成 ...)

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/zone/zone_characteristics.png)

---

(未完成 ...)

## Zone State Machine

### Empty state (ZSE) 

### Closed state (ZSC) 

### Full state (ZSF) 

### Read Only state (ZSRO)

### Offline state (ZSO)

### Implicitly Opened (ZSIO)  

### Explicitly Opened (ZSEO) 

---

以下狀態 (zone state)，控制器會中止寫入命令 :

(未完成 ...)

* Zone Full
* Zone Read Only
* Zone Offline
* ZSE ZSIO ZSEO ZSC 

---

## Zone Resources

*  Rsource
  * Active : 表示最大有可以使用多少 Active Zones
  * Open : 表示最大可以打開 (Implicitly & Explicitly) 多少個 Active Zones

如果控制器處理一個命令，需要將 zone 轉態到 ZSIO、ZSEO、ZSC，如果 Resource 已經沒有可使用空間，若是打開超過 Active 或是 Opend 的最大限制，則控制器會終止命令，並且回傳錯誤的狀態碼 (例如：Too Many Active Zones or Too Many Open Zones)

若是 zoned namespace 轉變成寫入保護 (write protected) 的狀態， 則在活動區所有的 Zones 都會轉態成 ZSF。

如果打開的區域數量達到最大值，並且它們都是顯式打開的，那麼任何打開新區域的嘗試都將失敗。但是，如果其中一些區域只是隱式打開的，那麼嘗試打開一個新區域將導致SSD關閉其中一個隱式打開的區域。

---

## Zone Transition

(未完成 ...)

一個命令被控制器處理也會造成不同狀態轉換，例如 : 處理一個寫入命令後，會從 ZSC:ZSIO，然後再從 ZSIO:ZSF (可以參考 Zone State Machine)。

一個zone只有在Open狀態下才可以寫入數據；擦除可以使寫滿的zone回退到Empty狀態；在zone的內部Nand介質達到磨損極限後處於Offline狀態。它的正常工作狀態變化過程為：
Empty → Open → Full → Empty

ZM（Zone Management，zone管理）command 有ZM Open, ZM Close, ZM Reset, ZM Finish等，可以控制zone的狀態變化。例如，在正常工作過程中，zone的狀態變化需要ZM命令的參與：
Empty → → Explicitly Opened → / → Full → → Empty

(未完成 ...)

### ZSE:Empty state

* ZSE 可以轉變到到任何的 zone state

### ZSIO:Implicitly Opened state

### ZSEO:Explicitly Opened state

### ZSC:Closed state

### ZSF:Full state

### ZSRO:Read Only state

### ZSO:Offline state

* 沒有任何狀態可以從 `ZSO` 轉到其它的 `zone state`

---

## Zone Management Send 

說明 : Host 可以透過 `Zone Management Send` 控制 `Zone State` 切換到不同的狀態。

命令參數 : 

* `Select All` : 該值會影響 Zone State 轉換成功或是失敗 (Reference : Zone Send Actions)
* `Zone Send Action (ZSA)` : 指定切換 Zone State

### Zone Send Actions

(未完成 ...)

---

## Zone Management Receive

(未完成 ...)

### Zone Receive Actions

---

A ZNS SSD may impose a limit on the maximum number of zones that can be active. This limit is always equal or larger than the limit on the maximum number of open zones.

This new limit imposes new constraints on user applications. While the maximum number of open zones of a namespace only limits the number of zones that an application can simultaneously write, the maximum number of active zones imposes a limit on the number of zones that an application can choose for storing data. If the maximum number of active zones is reached, the application must either reset or finish some active zones before being able to chose other zones for storing data.

(說明) ZNS 限制  an applications 可以同時寫入 open zones 最大數量，以及 an applications 可以選擇 active zones 最大數量。如果 active zones 已經達到最大數量，若是該應用程式想要選擇其它的 zones 操作， 必須要先執行 `reset` 或是 `finish` some active zones 

Similar to the limit on the maximum number of open zones, a limit on the maximum number of active zones for a namespace does not affect read operations. Any zone that is not offline can always be accessed for reading regardless of the current number of open and active zones.

(說明) 最大 active zones 數量的限制，並不會影響讀取操作。無論目前是 open and active zones 數量是多少，任何一個 zone 只要不是在 offline 狀態下，都可以讀取資料。


