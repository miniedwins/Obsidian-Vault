# Controller Shutdown
## 介紹

由主機端發起通知，透過設定暫存器 ( Controller Property ) 方式進行關閉控制器。例如 : 設定暫存器`CC.SHN=01` ( Normal shutdown notification )，代表主機端通知控制器要進行正常關機流程。此時主機端會去觀察 Controller Status ( CSTS )　

**Shutdown Notification (SHN) 協議規範定義三種類型通知** : 
* No notification; no effect
* Normal shutdown notification
* Abrupt shutdown notification
## 關機操作流程

當進行 `Shutdown Processing` 主機端會需要遵循協議規範的關機流程。

**Controller Shutdown 又可以分為兩種類型 :** 
* Memory-based Transport Controller Shutdown
* Message-based Transport Controller Shutdown









