## 概要說明
當 Sanitize ( 例如 :  Block Erase ) 完成後，控制器自動將被抹除的區域重新寫入合法的資料樣式（如全 00 加上正確的 ECC）。

為了讓主機在設定 **No-Deallocate ( 保留映射 )** 時，讀取該區域不會因為 ECC Error 而報錯，能順利讀到資料。

## 為什麼需要 Additional Media Modification

一旦資料被清除後，主機端若是要讀取資料，會經過 ECC 機制計算糾錯碼，但是物理資料已經被控制器清除 ( 清除後的資料為 0xFF )，此時計算**當前資料**的糾錯碼並且比對**原有資料**，會發生不可修正的錯誤 **( Uncorrectable ECC Error )**。

 為了避免主機端收到大量的異常錯誤 ( UNC )，因此加入 **Additional Media Modification 機制**，一旦資料 ( User Data ) 清除完成後，控制器則會重新寫入資料全部為 0x00 或是 0xFF。

## 這個機制會造成什麼影響

1. 這個機制會破壞了物理抹除的原始痕跡（覆蓋了案發現場），導致無法進行數位鑑識。
2. 每一次的執行都會複寫資料到 NAND 所有區域，相對 NAND 使用壽命會所減少。

## 使用情境

分為兩個使用情境，主要參數影響的是 **EMVS=0/1** ，表示是否要進入Enter Media Verification State
這個參數會影響主機對於資料驗證的結果與行為。

- Identify Controller ( SANICAP )
	- **NODMMAS** ( No-Deallocate Modifies Media After Sanitize ) 欄位必須是 **10b**。

### 情境 A ( EMVS=0 )
- Sanitize – Command Dword 10  :
	- **EMVS** ( Enter Media Verification State ) bit 必須是 **0**。
	- **NDAS** ( No-Deallocate After Sanitize ) bit 必須設為 **1**。

>  - 寫入合法的 00 與 ECC。
>  - 主機可順利讀取不報錯，但無法證明是否真的執行過 Block Erase ( 證據被覆蓋 )。

### 情境 B ( EMVS=1 )
- Sanitize – Command Dword 10  :
	- **EMVS** ( Enter Media Verification State ) bit 必須是 **1**。
	- **NDAS** ( No-Deallocate After Sanitize ) bit 必須設為 **1**。

>- 保留物理抹除後的原始狀態 (Raw)。
>- 雖然 ECC 是錯的，但驗證模式允許讀取原始資料 ( Raw 0xFF )，讓主機親眼確認物理抹除的結果。

