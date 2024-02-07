- 這一個可選的屬性，主要提供 `Host` 能夠發起 `NVM Subsytem Reset`

## 檢查是否支援 NVM Subsystem Reset

- `CAP.NSSRS` 設定為 `1` 則支援  `NVM Subsystem Reset`

![[nvme_subsystem_reset_support.png]]

## 如何發起 NVM Subsystem Reset
 
 - `NSSR.NSSRC` 寫入 **"4E564D65h"**
 - 若是寫入其它值則不會有任何影響
 - 當讀取 `NSSR.NSSRC` 回傳值需為 `0`
 
![[nvm_subsystem_reset.png]]
