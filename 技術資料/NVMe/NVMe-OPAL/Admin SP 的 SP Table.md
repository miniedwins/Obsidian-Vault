**SP Table（Security Provider Table）** 是 TCG Opal 架構中的一個核心資料表，用於記錄所有 **Security Provider (SP)** 的組態與狀態。  
而 **Admin SP 的 SP Table** 是專門存放 **與 Admin SP 相關聯的其他 SP 資訊**，例如 Locking SP 或其他自訂 SP 的預設設定。

---

## **2. SP Table 的具體內容**

從您提供的 **Table 24** 和 **5.2.2.2.1 章節** 可歸納出以下關鍵欄位與用途：

|欄位名稱 (Column)|說明|
|---|---|
|**UID**|SP 的唯一識別碼（例如 `00 00 02 05` 是 Admin SP，`00 00 00 01` 是 Locking SP）。|
|**Name**|SP 的名稱（如 `"Admin"`、`"Locking"`）。|
|**LifeCycle**|SP 的生命週期狀態：  <br>• `Manufactured`：啟用狀態。  <br>• `Manufactured-Inactive`：停用狀態。|
|**Frozen**|若為 `TRUE`，表示 SP 的設定被凍結，無法修改（例如防止惡意篡改）。|
|**其他欄位**|如 `ORG`、`EffectiveAuth`、`DateOllssue` 等，可能用於記錄廠商資訊或認證時間（依實作而定）。|

---

## **3. 為什麼需要 Admin SP 的 SP Table？**

1. **集中管理其他 SP**
    
    - Admin SP 透過此表格監控和操作關聯的 SP（例如 Locking SP 的啟用/停用）。
        
    - 例如：當執行 **`Activate`** 方法時，Admin SP 會修改目標 SP 的 `LifeCycle` 狀態（如從 `Manufactured-Inactive` 改為 `Manufactured`）。
        
2. **保存關鍵憑證**
    
    - 根據 5.2.2.2.1 章節，當 Locking SP 被啟用時：
        
        - **當前 SID PIN（C_PIN_SID）** 會從 Admin SP 複製到目標 SP 的 **C_PIN_Admin1** 欄位。
            
        - 這確保管理員能用已知的 PIN 取得 SP 控制權（避免權限遺失）。
            
3. **維護功能範本（Templates）**
    
    - 表格中可能引用 **功能範本**（如 Locking Template），這些範本定義了 SP 的行為（例如加密範圍、鎖定規則）。
        
    - 當 SP 狀態變更時，相關範本功能會自動生效（例如啟用 Locking SP 後，鎖定範圍開始運作）。
        

---

## **4. 實際運作範例**

### **情境：啟用 Locking SP（從 Manufactured-Inactive 到 Manufactured）**

1. **Admin SP 的 SP Table 記錄**：
    
    - Locking SP 初始狀態為 `Manufactured-Inactive`。
        
2. **管理員執行指令**：
    
    python
    
    複製
    
    Activate(LockingSP_UID)  # 觸發狀態切換
    
3. **SP Table 的變化**：
    
    - Locking SP 的 `LifeCycle` 欄位更新為 `Manufactured`。
        
    - **C_PIN_SID** 的值複製到 Locking SP 的 **C_PIN_Admin1**（方便後續認證）。
        
4. **結果**：
    
    - Locking SP 開始運作，但 **不破壞用戶資料**（符合章節 5.2.2.2.1 的規範）。
        

---

## **5. 與其他表格的關聯**

- **Authority Table**：定義 SP 的權限（如哪些角色可修改 SP Table）。
    
- **Locking Table**：記錄鎖定範圍的詳細設定（需 Locking SP 啟用後才能管理）。
    

---

## **6. 關鍵結論**

- **Admin SP 的 SP Table 本質是「SP 的註冊表」**：  
    記錄所有關聯 SP 的 UID、名稱、生命週期狀態、凍結標記等基礎資訊。
    
- **核心功能**：
    
    - 提供 Admin SP **集中管理其他 SP 的介面**（如啟用/停用 Locking SP）。
        
    - 在狀態切換時 **自動處理憑證轉移**（如 SID PIN 複製到 Admin1）。
        
- **重要限制**：
    
    - 若 SP 的 `Frozen=TRUE`，即使 Admin SP 也無法直接修改其狀態。
        
    - 狀態變更需透過標準方法（如 `Activate`/`RevertSP`）觸發，且需符合 TCG Opal 規範。
        

此設計確保了 TCG 儲存設備的安全管理兼具彈性與可控性。