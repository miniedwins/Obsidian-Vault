## PRP 概述

PRP 是 NVMe 主機控制器用於描述資料緩衝區物理位址的機制。它提供了一種方法來告訴 NVMe 控制器，主記憶體中哪一部分包含要讀取或寫入的資料。
## PRP 的兩種主要方式

PRP 設計允許主機控制器描述資料緩衝區的位址。這些位址可以是**連續的或分散**。PRP 支援兩種描述方法：

1. **PRP Entry**:
    - 包含一個 64 位元的記憶體位址，用來描述主機記憶體中資料緩衝區的物理位址。
	- 每個 PRP Entry 對應一個資料頁（Memory Page = 4kB）
	- PRP Entry 指向緩衝區的位址必須對齊到一個頁面大小（MPS）的邊界。
2. **PRP List**:    
    - 當資料大小超過 **Memory Page Size**，就會使用 PRP List 描述多個 **PRP Entry**。 
    - PRP List 內容存放後續每個傳輸資料的記憶體位址。 

>如何定義 Memory Page Size  ( MPS ) ? 
>1.  **Controller Configuration** ( CC ) 暫存器裡的 **Memory Page Size** ( MPS ) 欄位來決定。
>2.  計算方法為 **( 2 ^ ( 12 + MPS ) )**，當設定為 0 表示 4096 bytes。

## **PRP List 的運作方式**

1. **PRP1 Entry**：
    - 第一個 PRP1 Entry 通常描述第一個頁面 ( Memory Page ) 的物理位址。
2. **PRP2 Entry**：    
    - 當資料量超過一頁面，PRP2 Entry 會指向一另個 PRP List。
    - PRP List 每個條目是 64 位元的記憶體位址，依序指向後續頁面。
3. **多層結構**：
    - 如果 PRP List 本身無法容納所有頁面，則可以鏈接到另一個 PRP List，形成多層結構。
    - 

## **PRP List 的應用場景**

- **大資料塊傳輸**：當資料量超過單一頁面（例如大於 4 KB）時，使用 PRP List 是必要的。
- **分散記憶體緩衝區**：資料可能存儲在不連續的記憶體區域，PRP List 能有效描述這些分散的區域。