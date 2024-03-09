當發生 `Subsystem Reset`，會間接執行 `Controller Level Reset`，其最後的目的就是重新初始化 PCIe 裝置，此時 PCIe 的狀態會回到 `LTSSM Detect State`，接下來就會重新開始裝置建立起溝通橋梁。

***備註 :*** 
- ***待確認 : 尚未了解該 Subsytem Reset，是屬於哪一種 PCIe Reset (Hot or FLR) ?***

![[nvme_substem_reset.png]]
## 檢查是否支援 NVM Subsystem Reset

- `CAP.NSSRS` 設定為 `1` 則支援  `NVM Subsystem Reset`。

![[nvme_subsystem_reset_nssrs.png]]

## 如何發起 NVM Subsystem Reset
 
 - `NSSR.NSSRC` 寫入 **"4E564D65h"**，這些 `ASCII HEX` 值表示 `NVMe`。
 - 若是寫入其它值則不會有任何影響。
 - 當讀取 `NSSR.NSSRC`，該回傳值則需為 `0`。
 
![[nvm_subsystem_reset_nssrc.png]]

## 主機端如何知道發生 NVM Subsystem Reset

***內容待確認***

![[nvme_subsystem_reset_nssro.png]]