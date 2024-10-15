TODO : 
* 筆記大概功能的行為
	* 正常 & 不正常 
	* RTD3
備註 : 不同情況會有複雜的行為 因此暫時不要太過於關注
# Controller Shutdown
## 介紹

由主機端發起通知，透過設定暫存器  ( Controller Property ) 方式進行協議規範。例如 : 設定暫存器`CC.SHN=01` ( Normal shutdown notification )，代表主機端通知控制器進行正常關機流程。

暫存器 `CC.SHN` 關機通知


**主機端什麼後會進行  Controller Shutdown Processing ?**
* 正常關機
* 不正常關機
* 進入到 RTD3

## 操作流程







