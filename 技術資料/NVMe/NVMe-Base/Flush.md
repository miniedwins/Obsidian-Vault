# 基本介紹

**Volatile Write Cache** 啟用時，寫入的資料可能暫時停留在控制器的快取中 ( DRAM or SRAM )，而未立即寫入到 NAND FLASH。因此Flush 命令主要功能是，當主機需要將快取的資料寫回 **NAND FLASH** 就會發出 Flush 命令，並且指定所有或是特定命名空間 ( Namespace ) 的相關資料 ( Data and Metadata )，寫入到 **NAND FLASH**，以確保資料的持久性。

> 主機發出 Flush 命令可能基於，準備要 "關機系統" 或是 "固定排程" 等其他因素考量。

如果 **Volatile Write Cache** 沒有被 **Enabled ( 啟用 )**，則 **Flush（刷新）** 命令將不會產生任何效果，Flush 命令雖然不執行實際的快取刷新操作，但仍然會回應該命令執行成功。

* Sanitize operation is not in progress
* Sanitize operation is in progress.

**如何確認是否支援指定刷新 "所有" 或是 "指定" 的 Namespace ?**
* 查詢 Volatile Write Cache ( VWC ) 所定義的 Bit
	* Bit 2 : 1
		- 10b : 不支援 NSID=0xFFFFFFFFh **( 只能指定單一的NSID )**
		- 11b : 支援 NSID=0xFFFFFFFFh

![[idenitfy_volatile_write_cache.png]]