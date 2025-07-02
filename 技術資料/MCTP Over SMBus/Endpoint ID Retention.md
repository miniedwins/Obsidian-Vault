Devices should retain their EID assignments for as long as they are in their normal operating state.

1. 只要沒發生重大變更，裝置不應該自行改變或忘記它的 EID

2. 某些「非同步情況」Bus Owner 必須偵測並重新分配 EID
	- 異常重開機
    - 突然斷電
    - 裝置重設（reset）
    - 韌體更新後資料丟失

3. 裝置應盡可能保留 EID，即使暫時無法回應
	- 裝置在重設時暫時不能通訊
	- 暫時錯誤導致不回應