- Resets 
	- Controller Reset
	- NVM Subsystem Reset
	- Controller Level Reset
	- Queue Level Reset

# NVM Subsystem Reset

目的 : 重新初始化 PCIe 裝置，因此當發生 `NVM Subsystem Reset`，就會執行 `Controller Level Reset`。

> ***待確認 : 尚未了解該 Subsytem Reset，是屬於哪一種 PCIe Reset (Hot or FLR) ?***

`NVM Subsystem Reset` 觸發後，PCIe 的狀態會回到 `LTSSM Detect State`，接下來就會重新開始初始化與設置，並且與裝置建立起溝通橋梁。

>***LTSSM : 需要參考 PCIe SPEC***

![[Pasted image 20240213192100.png]]
## 檢查是否支援 NVM Subsystem Reset

- `CAP.NSSRS` 設定為 `1` 則支援  `NVM Subsystem Reset`。

![[nvme_subsystem_reset_support.png]]

## 如何發起 NVM Subsystem Reset
 
 - `NSSR.NSSRC` 寫入 **"4E564D65h"**，這些 `ASCII HEX` 值表示 `NVMe`。
 - 若是寫入其它值則不會有任何影響。
 - 當讀取 `NSSR.NSSRC`，該回傳值則需為 `0`。
 
![[nvm_subsystem_reset.png]]

## 主機端如何知道發生 NVM Subsystem Reset

***內容待確認***

![[nvme_subsystem_reset_occurred.png]]


# Controller Level Reset