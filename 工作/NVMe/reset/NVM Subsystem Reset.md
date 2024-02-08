## 檢查是否支援 NVM Subsystem Reset

- `CAP.NSSRS` 設定為 `1` 則支援  `NVM Subsystem Reset`。

![[nvme_subsystem_reset_support.png]]

## 如何發起 NVM Subsystem Reset
 
 - `NSSR.NSSRC` 寫入 **"4E564D65h"**，這個值表示 `NVMe`。
 - 若是寫入其它值則不會有任何影響。
 - 當讀取 `NSSR.NSSRC`，該回傳值則需為 `0`。
 
![[nvm_subsystem_reset.png]]

## 主機端如何知道發生 NVM Subsystem Reset

***內容待確認***

![[nvme_subsystem_reset_occurred.png]]