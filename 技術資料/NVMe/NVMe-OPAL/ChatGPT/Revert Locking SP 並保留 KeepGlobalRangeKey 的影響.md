當您對 **Locking SP** 執行 **Revert** 操作並設定 **KeepGlobalRangeKey = True** 時，以下是關鍵行為與狀態說明：

---

## **1. Locking SP 的狀態變化**

- **Locking SP 會進入 "Manufactured-Inactive" 狀態**
    
    - 此狀態表示 Locking SP 已被停用（類似關閉鎖定功能），但 **不觸發加密抹除（Cryptographic Erase）**。
        
- **Global Range 的媒體加密金鑰（Media Encryption Key）會被保留**
    
    - 使用者資料仍可透過原有金鑰存取（前提是 Global Range 已解鎖）。
        

---

## **2. Admin SP 的狀態**

- **Admin SP 的狀態不受直接影響**
    
    - Revert Locking SP **不會自動** 將 Admin SP 設為 Inactive。
        
    - Admin SP 的狀態（Active/Inactive）取決於其自身的生命週期設定（例如是否被單獨執行 Revert）。
        
- **例外情況**：
    
    - 若 Locking SP 和 Admin SP 有相依性（例如某些廠商實作），需查閱設備規格書確認。但根據 **TCG Opal 標準**，兩者預設為獨立運作。
        

---

## **3. 保留 KeepGlobalRangeKey 的條件**

- **必須滿足以下條件**，否則 RevertSP 會失敗（狀態 `FAIL`）：
    
    - **Global Range 在執行 RevertSP 時處於解鎖狀態**（Read Unlocked 或 Write Unlocked）。
        
    - 若 Global Range 仍被鎖定，TPer 將拒絕保留金鑰，且 Locking SP 狀態不變。
        

---

## **4. 對 SSD 實際運作的影響**

|操作|結果|
|---|---|
|**Revert Locking SP + KeepGlobalRangeKey=True**|• Locking SP 停用（Manufactured-Inactive）  <br>• **資料不被抹除**（加密金鑰保留）  <br>• Admin SP 狀態維持不變|
|**Global Range 未解鎖**|RevertSP 失敗，Locking SP 維持原狀態|

---

## **5. 常見應用場景**

- **停用 TCG 鎖定功能，但保留資料**：  
    企業可能需要暫時關閉硬碟加密管理（如移交設備），但避免觸發資料抹除。
    
- **維護或故障排除**：  
    在需重設 Locking SP 時，確保使用者資料可被恢復。
    

---

## **總結**

- **Admin SP 不會自動變為 Inactive**，除非明確對其執行 Revert。
    
- **KeepGlobalRangeKey=True 的作用**：
    
    - 僅停用 Locking SP 的鎖定功能，**不影響 Admin SP**。
        
    - 保留加密金鑰，避免資料損失（需 Global Range 已解鎖）。
        
- 若操作失敗，請檢查 Global Range 的鎖定狀態。
    

若有進一步的廠商特定行為（如 Admin SP 連動），建議查閱設備的 **TCG Opal 實作檔案**。

Global Range 已解鎖 ? Global Range 本身有 RLocked, WLocked ?

### **繁體中文解釋：Global Range 的鎖定狀態（RLocked / WLocked）**

---

## **1. Global Range 的鎖定類型**

在 **TCG Opal 架構**中，**Global Range**（全域鎖定範圍）的存取權限由兩種獨立鎖定狀態控制：

- **RLocked (Read Locked)**：
    
    - 若為 `True`，禁止**讀取** Global Range 內的資料。
        
    - 若為 `False`，允許讀取（即使 WLocked 為 `True` 仍可讀）。
        
- **WLocked (Write Locked)**：
    
    - 若為 `True`，禁止**寫入**或修改 Global Range 內的資料。
        
    - 若為 `False`，允許寫入（需 RLocked 也為 `False` 才能完整讀寫）。
        

---

## **2. 如何判斷 Global Range 是否「已解鎖」？**

- **完全解鎖（Fully Unlocked）**：
    
    - `RLocked = False` **且** `WLocked = False`
        
    - 此時可自由**讀取和寫入**資料。
        
- **部分解鎖（Partially Unlocked）**：
    
    - `RLocked = False` **但** `WLocked = True` → 可讀但不可寫。
        
    - `RLocked = True` **但** `WLocked = False` → 不可讀但可寫（罕見，因寫入前通常需讀取）。
        

### **執行 RevertSP + KeepGlobalRangeKey 的條件**

- **必須滿足以下任一狀態**，否則操作會失敗（`FAIL`）：
    
    - `RLocked = False`（Read Unlocked）
        
    - `WLocked = False`（Write Unlocked）
        
- **最佳實踐**：  
    建議確保 **RLocked 和 WLocked 均為 `False`**，避免因部分鎖定導致不可預期的行為。
    

---

## **3. 鎖定狀態的實際影響**

|情境|RLocked|WLocked|資料存取權限|RevertSP + KeepGlobalRangeKey 是否成功？|
|---|---|---|---|---|
|**完全解鎖**|`False`|`False`|可讀可寫|✅ 成功|
|**只讀模式**|`False`|`True`|可讀不可寫|✅ 成功（因 Read Unlocked）|
|**只寫模式**|`True`|`False`|不可讀可寫|⚠️ 可能失敗（因 Read Locked）|
|**完全鎖定**|`True`|`True`|不可讀寫|❌ 失敗|

---

## **4. 檢查與設定鎖定狀態的方法**

- **透過 TCG Opal 指令查詢**：  
    使用 `GetAceessingRangeStartRow` 或類似指令讀取 Global Range 的 `RLocked`/`WLocked` 值。
    
- **解鎖方式**：
    
    - 若 Locking SP 已啟用，需透過 **SID 或 Admin SP** 認證後解除鎖定。
        
    - 範例指令：
        
        python
        
        複製
        
        # 偽代碼，解鎖 Global Range
        SetLockingState(RangeUID=GlobalRange, RLocked=False, WLocked=False)
        

---

## **5. 關鍵結論**

1. **「Global Range 已解鎖」的定義**：
    
    - 至少 `RLocked` 或 `WLocked` 之一為 `False`，但建議兩者均解鎖以確保相容性。
        
2. **KeepGlobalRangeKey 的運作前提**：
    
    - Global Range 不得處於 **完全鎖定（RLocked=True + WLocked=True）** 狀態。
        
3. **若 RevertSP 失敗**：
    
    - 檢查鎖定狀態，並先手動解鎖後重試。
        

此機制確保在停用 Locking SP 時，不會因誤鎖定導致資料無法存取或加密金鑰被意外清除。

停用 Locking SP, 代表者沒有 GlobalRange 那是誰要負責解鎖 GlobalRange ? Admin SP

### **繁體中文解釋：停用 Locking SP 後，誰負責管理 Global Range？**

---

## **1. 停用 Locking SP 後的權限轉移**

當您執行 **`RevertSP`** 停用 Locking SP（並保留 `KeepGlobalRangeKey=True`）後：

- **Locking SP 進入 "Manufactured-Inactive" 狀態**，喪失所有鎖定管理功能。
    
- **Global Range 的媒體加密金鑰（MEK）仍保留**，但 **Locking SP 不再能控制鎖定狀態**。
    

此時，**解鎖 Global Range 的權限會轉移給 Admin SP**，原因如下：

---

## **2. 為什麼是 Admin SP 負責解鎖？**

1. **Admin SP 是最高權限管理者**
    
    - 根據 TCG Opal 架構，Admin SP 的權限高於 Locking SP，負責全域設定（如 SP 生命週期、存取控制）。
        
    - 當 Locking SP 被停用，Admin SP **自動繼承其殘留權限**（例如解除 Global Range 鎖定）。
        
2. **技術實作的強制性**
    
    - Locking SP 停用後，TPer（硬體）會將 Global Range 的鎖定狀態標記為 **「需由 Admin SP 管理」**。
        
    - 若無 Admin SP 介入，Global Range 可能維持鎖定狀態，導致資料無法存取。
        
3. **例外情況**
    
    - 若 Admin SP **也被停用（Inactive）**，則需透過 **製造商權限（MSID 或 PSID）** 解鎖。
        
    - 部分廠商可能實作特殊後門機制（非標準 Opal 行為）。
        

---

## **3. 實際操作流程**

若要解鎖 Global Range 停用 Locking SP 後：

1. **確認 Locking SP 已停用**
    
    - 檢查 Locking SP 狀態是否為 `Manufactured-Inactive`。
        
2. **使用 Admin SP 認證**
    
    - 透過 **SID 或 Admin PIN** 登入 Admin SP。
        
    - 執行解鎖指令（範例偽代碼）：
        
        python
        
        複製
        
        # 解鎖 Global Range 的讀寫權限
        SetLockingState(RangeUID=GlobalRange, RLocked=False, WLocked=False)
        
3. **若 Admin SP 不可用**
    
    - 需使用 **MSID（製造商預設密碼）** 或 **PSID（物理安全識別碼）** 強制解鎖。
        

---

## **4. 權限繼承關係圖**

mermaid

複製

graph TD
    A[Locking SP] -->|停用後| B(Global Range 鎖定狀態)
    B --> C{誰能解鎖?}
    C -->|預設| D[Admin SP]
    C -->|備援| E[MSID/PSID]
    C -->|廠商特殊機制| F[Vendor-Specific Backdoor]

---

## **5. 關鍵結論**

- **正常情況下**：  
    **Admin SP** 是停用 Locking SP 後解鎖 Global Range 的唯一合法途徑。
    
- **特殊情況**：
    
    - 若 Admin SP 也失效，需依賴 **MSID/PSID** 或廠商支援。
        
- **安全提醒**：
    
    - 停用 Locking SP 前，請確保 **Admin SP 可用**，避免資料永久鎖死。
        
    - 部分企業環境可能預先綁定 AD/LDAP 認證至 Admin SP，需聯繫 IT 部門解鎖。
        

此設計確保了 TCG Opal 設備在管理權限變更時，仍能透過最高權限層級（Admin SP）維持資料可存取性。