## PRP 概述
PRP 是 NVMe 主機控制器用於描述資料緩衝區物理位址的機制。它提供了一種方法來告訴 NVMe 控制器，主記憶體中哪一部分包含要讀取或寫入的資料。

Host Software 在提交 Command之前，需要在主機端預先分配一塊 **Memory Buffer**，告知控制器要去哪裡拿取或是寫入資料。控制器是如何知道 Memory Buffer 的位置呢 ? 主要透過命令中的 **PRP 或是 SGL**，將緩衝區 ( Memory Buffer Address ) 填入所提交的命令中的 **DPTR 欄位**，控制器就能夠知道要去哪裡取得資料 ( Host Write ) 或是將資料放置在正確的位置 ( Host Read )。

![[../attachments/physical_region_page/prp_entry_layout.png]]

## PRP 兩種主要方式
PRP 設計允許主機控制器描述資料緩衝區的位址。這些位址可以是**連續的或分散**。PRP 支援兩種描述方法：

1. **PRP1 Entry** :
    - 一個 64 位元記憶體位址 ( Page Base Address )，用來描述主機資料緩衝區的記憶體位址。
	- 每個 PRP Entry 對應一個資料頁（預設 : Memory Page Size = 4kB）
	- PRP Entry 指向緩衝區的位址必須對齊到一個頁面大小（MPS）的邊界。
2. **PRP2 Entry** :
	- 若是傳輸資料沒有超過 MPS，PRP2 Entry 內容則保留。
	- 如果傳輸的資料超過了第一個頁面大小，PRP2 用於描述剩餘的資料。
		- PRP2 指向 **第二個連續頁面**
		- PRP2 指向一個 **PRP List**。
3. **PRP List** :
    - PRP List 用於存放多個 PRP Entry。
    - 每一個PRP Entry會再指向一個 **Page Base Address**
    - 若是 PRP List 無法描述所有要傳輸的記憶體位址，**最後一個 PRP Entry** 會是存放下一個可以鏈接 PRP List，形成多層結構。	

**這張圖解釋，從提交 Command 包含 PRP1 and PRP2， 以及 PRP List 存放多個 PRP Entry。**
![[../attachments/physical_region_page/prp_list_describing_data_to_comapre.png]]

>如何定義 Memory Page Size  ( MPS ) ? 
>1.  **Controller Configuration** ( CC ) 暫存器裡的 **Memory Page Size** ( MPS ) 欄位來決定。
>2.  計算方法為 **( 2 ^ ( 12 + MPS ) )**，當設定為 0 表示 4096 bytes。

## PRP 結構說明
PRP Entry 格式，主要由 **Page Base Address** 以及 **Offset** 欄位所組成

- **Page Base Address**
	- 主機端要寫入或是讀取資料的位址 **( Memory Page Address )**
- **Offset**
	- MPS=4 KiB，bits [11:00] 必須要為 0
	- MPS=8 KiB，bits [12:00] 必須要為 0

舉例說明 :  MPS=4k，Page Base Address : `0x0000004:1D811000`，協議規範 bits [11:00] 必須要全部為 0，因此尾數會是 `1000h`。每個 PRP Entry 都必須要對齊，若是有多個資料，代表會有下一個 PRP Entry，則記憶體位址因該為 `0x0000004:1D812000`，符合 MPS=4k 邊界對齊。

## **PRP Entry 與 PRP List 的 Offset 要求**
- 偏移量為 `0h` 表示，資料總是從該頁面的起始處開始。
- 每個 PRP Entry 都必須具有 **頁面偏移為 0h** 的地址。
- 一個命令包含兩個 PRP Entry，則第二個 PRP Entry 的地址也必須具有 **頁面偏移為 0h*。
- PRP List 中的每個 PRP Entry 位址必須對齊到記憶體頁面的起始地址（例如 4 KB 邊界）。
- 如果控制器收到 **PRP Entry 頁面偏移不為 0**，則控制器應傳回 **PRP Offset Invalid**。

![[../attachments/physical_region_page/page_base_address_offset.png]]

## **PRP 運作範例**
1. 假設頁面 ( MPS ) 大小為 4 KB，資料大小為 4 KB，並且只有使用 PRP1 Entry：
	- **PRP1 Entry**
		- 描述第一個記憶體頁面。
		- 指向記憶體位址： `0x0000004:1D810000`（對齊到 4 KB 的邊界）。
	- **PRP2 Entry**
		- 因為沒有超過 MPS 大小，該記憶體位址保留 `0x0000000:00000000`。

| 條目            | 地址                   | 偏移量  |
| ------------- | -------------------- | ---- |
| 第一個 PRP Entry | `0x0000004:1D810000` | `0h` |
| 第二個 PRP Entry | `0x0000000:00000000` | `0h` |

2. 假設頁面 ( MPS ) 大小為 4 KB，傳輸資料大小為 8 KB，當前資料量大於 MPS，因此需要使用 PRP2 Entry **描述第二筆資料**的記憶體位址空間：
	- **PRP1 Entry**
		- 描述第一個記憶體頁面。
	    - 指向記憶體位址： `0x0000001:09BFD000`。
	- **PRP2 Entry
	    -  描述第二個記憶體頁面。
	    - 指向記憶體位址： `0x0000001:09BFE000`。

| 條目            | 地址                     | 偏移量  |
| ------------- | ---------------------- | ---- |
| 第一個 PRP Entry | ``0x0000001:09BFD000`` | `0h` |
| 第二個 PRP Entry | `0x0000001:09BFE000`   | `0h` |

3.  假設頁面 ( MPS ) 大小為 4 KB，傳輸資料大小為 16KB，當前資料量大於 MPS，因此需要使用PRP2 Entry **描述多筆資料**記憶體位址空間：
	- **PRP1 Entry**
	    - 描述第一個記憶體頁面。
		- 指向記憶體位址：`0x0000004:1EDF2000`。
	- **PRP2 Entry
	    - 描述剩餘的記憶體頁面。
		- 指向一個 PRP List 的起始地址：`0x0000001:2CE91000`。
	- **PRP List**
		- PRP List 的內容用於補充 PRP1 Entry，描述連續的記憶體空間。
		- 包含 **三筆記憶體位址**，每個位址均需對齊 **4 KB 邊界**。
	- **資料傳輸計算**
	    - PRP1 + PRP2 總共使用 **4 組記憶體位址**。
	    - 每一組記憶體位址對應一個頁面，且每頁傳輸大小為 **4 KB**。
	    - 記憶體總共可以描述的資料大小為： 4 組記憶體位址×4 KB/頁=16 KB。
	- **備註**
		- 從主機端發出讀取命令 ( NVM Read )，PRP List 存放的記憶體位址是不連續。
		- 關於讀取命令的記憶體位址沒有連續 *( SPEC 暫時未看到相關說明 )*

| 條目            | 地址                                                             | 偏移量  |
| ------------- | -------------------------------------------------------------- | ---- |
| 第一個 PRP Entry | `0x0000004:1EDF2000`                                           | `0h` |
| 第二個 PRP Entry | `0x0000001:2CE91000`                                           | `0h` |
| PRP List 內容   | `0x0000004:1EDF3000` `0x0000001:1EDF4000` `0x0000004:1EDF5000` | `0h` |
