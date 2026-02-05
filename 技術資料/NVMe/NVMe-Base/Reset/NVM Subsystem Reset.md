## 概要說明
當發生 `Subsystem Reset`，會間接執行 `Controller Level Reset`，其最後的目的就是重新初始化 PCIe 裝置，此時 PCIe 的狀態會回到 `LTSSM Detect State`，接下來就會重新開始建立起溝通橋梁。

![[../attachments/subsystem_reset/nvme_subsytem_reset.png]]

## 檢查是否支援 NVM Subsystem Reset
 `CAP.NSSRS` 設定為 `1` 則支援  `NVM Subsystem Reset`。

![[../attachments/subsystem_reset/nvme_subsystem_reset_supported.png]]

## 如何發起 NVM Subsystem Reset
  - `NSSR.NSSRC` 寫入 **"4E564D65h"**，這些 `ASCII HEX` 值表示 `NVMe`。
 - 若是寫入其它值則不會有任何影響。
 - 當讀取 `NSSR.NSSRC`，該回傳值則需為 `0`。
 
![[../attachments/subsystem_reset/nvme_subsystem_reset_control.png]]

# 主機端如何知道發生 NVM Subsystem Reset

***內容待確認***

![[../attachments/subsystem_reset/nvme_subsystem_reset_occurred.png]]