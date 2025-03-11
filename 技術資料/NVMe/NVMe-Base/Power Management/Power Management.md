# 電源管理說明
主要功能是允許主機 ( Host ) 可以靜態或是動態管理 **NVM Subsystem Power**。

下列說明靜態與動態之間的不同 : 
* `Static Power Management ` 
  靜態電源管理由主機 (Host) 決定分配 NVM subsystem 的最大電源，並將 NVM Express 的電源狀態設定成該耗電量或更少的電量模式。

* `Dynamic Power Management`
  動態電源管理由主機 (Host) 決定切換到最適合的電源狀態。Power Manager 會根據這 Power Objective & Performance Objective 做為參考標準，並動態的切換符合的電源模式。 