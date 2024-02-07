- 這一個可選的屬性，主要提供 Host 能夠發起 `NVM Subsytem Reset`
- 若是沒有支援，則屬性位址範圍就會保留
- 如何發起 `NVM Subsystem Reset`
	- 對屬性 `NSSRC` 寫入 **"4E564D65h"**
	- 若是寫入其它值則不會有任何影響

![[nvm_subsystem_reset.png]]
