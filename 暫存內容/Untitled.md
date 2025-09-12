### UDID 的核心作用

**UDID (Unique Device Identifier)**，中文是「唯一設備識別碼」。您可以將它想像成**裝置的「身分證號碼」**。

一個典型的 UDID 通常由幾個部分組合而成，以確保其唯一性：

1. **廠商 ID (Vendor ID):** 一個標準化的代碼，用於識別製造該裝置的公司（例如 Intel, Samsung, Kioxia 等）。
    
2. **廠商特定 ID (Vendor-specific ID):** 由製造商自行定義和分配的部分，可能是裝置的序號 (Serial Number) 或一個內部唯一的編號，用以區分其生產的每一個單獨產品。

### SMBus 設備類型
#### 最優先關注 (且最希望採用) 的裝置
(1) 動態且持續性位址 (PTA - Persistent Target Address)
說明：擁有永久不變的 UDID (身分證)，位址重開機後不會改變。

(2) 動態且揮發性位址 (Dynamic and volatile address device)
說明：擁有永久不變的 UDID，位址在重開機後會遺失。

#### 需要特別注意 (且可能要避免) 的裝置
(3) 固定位址設備 (DTA - Default Target Address)
說明：UDID 和位址可能重複，在系統中安裝多個相同裝置時，會導致的位址衝突，無法管理。

(4) 隨機數設備 (Random number device)
說明：UDID 每次重開機都隨機改變，如同每天換身分證。

### 討論的重點
1. UDID 需要規劃一個規則來自定義不同的裝置編號並免發生衝突
2. 每一個設備都會有一個地址類型，出廠基本類型會是屬於哪一種？
3. 客戶不一定選擇哪一種，UDID 以及設備位置是否提供可選

