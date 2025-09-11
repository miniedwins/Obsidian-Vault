### ARP 設備類型總整理

根據提供的資料，具備 ARP 功能的設備主要可透過其「位址類型」欄位（`Capabilities` 暫存器的 `Bit[7:6]`）分為四大類。每種類型在通電重置 (Power-On Reset) 時有不同的內部狀態，並且對其 UDID (唯一設備識別碼) 有特定的要求。

#### 1. 固定位址設備 (Fixed Address device)

- **位址類型碼:** `00b`
    
- **對應設備類型 (Table 9):** DTA (Default Target Address / 預設目標位址)
    
- **特性總結:**
    
    - **地址特性:** 擁有一個由硬體或韌體決定的固定 SMBus 位址，通常寫死在 ROM 中。此位址在設備生命週期內不會改變。
        
    - **啟動時狀態:**
        
        - `AR Flag` (位址已解析): **CLEAR** (未解析)
            
        - `AV Flag` (位址有效): **SET** (有效)
            
        - `SMB Address`: **預設位址** (從 ROM 讀取)
            
        - `UDID`: **NO CHANGE** (固定不變)
            
    - **UDID 規則:**
        
        - 必須實作 UDID 欄位，但其內容**不需要是唯一的**。
            
        - 由於位址是固定的，UDID 中的廠商特定 ID (Vendor-specific ID) 應為一個**常數**，不能是隨機數，以確保 ARP 解析順序的一致性。
            

#### 2. 動態且持續性位址設備 (Dynamic and persistent address device)

- **位址類型碼:** `01b`
    
- **對應設備類型 (Table 9):** PTA (Persistent Target Address / 持續性目標位址)
    
- **特性總結:**
    
    - **地址特性:** 設備位址可由主機 (Host) 動態分配，分配後會儲存在非揮發性記憶體 (NVR) 中，斷電後依然能保存。
        
    - **啟動時狀態:**
        
        - `AR Flag`: **CLEAR** (未解析)
            
        - `AV Flag`: **從 NVR 讀取** (若之前已儲存有效位址，則為 SET)
            
        - `SMB Address`: **從 NVR 讀取** (若 `AV Flag` 為 SET)
            
        - `UDID`: **NO CHANGE** (固定不變)
            
    - **UDID 規則:**
        
        - 由於支援位址指派，其 UDID **必須是唯一的**。
            
        - 通常使用一個預先設定的唯一 ID (pre-assigned unique ID)，建議至少 32-bit，最低要求 16-bit 必須唯一。
            

#### 3. 動態且揮發性位址設備 (Dynamic and volatile address device)

- **位址類型碼:** `10b`
    
- **對應設備類型 (Table 9):** Non-PTA / Non-Random Number (非持續性 / 非隨機數)
    
- **特性總結:**
    
    - **地址特性:** 設備位址可由主機動態分配，但不會儲存下來。每次斷電後，位址就會遺失，需要重新分配。
        
    - **啟動時狀態:**
        
        - `AR Flag`: **CLEAR** (未解析)
            
        - `AV Flag`: **CLEAR** (無效)
            
        - `SMB Address`: **undefined** (未定義)
            
        - `UDID`: **NO CHANGE** (固定不變)
            
    - **UDID 規則:**
        
        - 與「動態且持續性位址設備」相同，其 UDID **必須是唯一的**，且通常是預先設定好的。
            

#### 4. 隨機數設備 (Random number device)

- **位址類型碼:** `11b`
    
- **對應設備類型 (Table 9):** Non-PTA / Random Number (非持續性 / 隨機數)
    
- **特性總結:**
    
    - **地址特性:** 位址是動態分配的，且斷電後會遺失（揮發性）。
        
    - **啟動時狀態:**
        
        - `AR Flag`: **CLEAR** (未解析)
            
        - `AV Flag`: **CLEAR** (無效)
            
        - `SMB Address`: **undefined** (未定義)
            
        - `UDID`: **產生新的隨機數** (Generate Random Number)
            
    - **UDID 規則與限制:**
        
        - UDID 中的廠商特定 ID 是一個隨機數。
            
        - 此隨機數**必須至少為 16-bit**。
            
        - 只要設備保持通電，此隨機數必須**維持不變**。
            
        - 此類設備**不允許**支援持續性目標位址 (PTA)。
            
        - 此類設備**不允許**支援固定位址模式。
            

---

### 其他共通能力

- **PEC (Packet Error Code) 支援:**
    
    - 在 `Capabilities` 暫存器的 `Bit[0]`。
        
    - 若此位元為 `1` (SET)，表示該設備在其 SMBus 位址上支援的所有指令都支援封包錯誤碼校驗。
        
    - 若為 `0` (CLEAR)，則表示其 PEC 支援能力未知。
        
    - 這是一個獨立的能力，與上述四種位址類型無直接關聯。