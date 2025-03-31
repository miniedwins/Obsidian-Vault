### **1. Admin SP C_PIN**

📌 **用途**：管理整個設備的安全策略和存取權限  
📌 **影響範圍**：設備層級（全域設定）  
📌 **主要 C_PIN 類型**：

- **C_PIN_SID**：最高管理者，通常是初始設備擁有者 (SID)
    
- **C_PIN_MSID**：製造商預設的 MSID（用於重設安全設定）
    
- **C_PIN_Admin1**：設備管理者帳戶
    

📌 **特點**：

- **控制整體安全性**，如啟用 OPAL 加密、變更 SP 設定
    
- 只有 **Admin SP C_PIN** 才能修改 **Locking SP** 的權限
    
- **影響 Locking SP 的啟用/停用**，但不直接影響個別 LBA 的鎖定狀態
    

---

### **2. Locking SP C_PIN**

📌 **用途**：管理特定範圍（LBA範圍）的存取控制  
📌 **影響範圍**：LBA 鎖定範圍（特定區塊）  
📌 **主要 C_PIN 類型**：

- **C_PIN_Admin1~Admin4**：Locking SP 的管理帳戶
    
- **其他 C_PIN**：可能代表用戶帳戶，控制某些 LBA 區域的存取
    

📌 **特點**：

- **負責管理 LBA 的鎖定/解鎖**
    
- 不能修改 **Admin SP** 層級的安全性
    
- 必須有 **Admin SP** 允許後，Locking SP 才能運作
    

---

### **主要區別**

|項目|**Admin SP C_PIN**|**Locking SP C_PIN**|
|---|---|---|
|**控制範圍**|整體設備安全|特定 LBA 區域存取|
|**影響層級**|設備層級（全域）|LBA 範圍（區塊級）|
|**主要帳戶**|C_PIN_SID, C_PIN_MSID, C_PIN_Admin1|C_PIN_Admin1, C_PIN_Admin2, ...|
|**能否影響 Locking SP？**|✅ 是，可以啟用/停用|❌ 否，需 Admin SP 授權|
|**能否影響 Admin SP？**|❌ 否|❌ 否|
|**典型用途**|設備擁有者或系統管理員控制權限|管理 LBA 鎖定，如 ReadLock/WriteLock|

---

### **結論**

- **Admin SP C_PIN** 是設備層級的最高管理權限，可修改所有 Locking SP 設定
    
- **Locking SP C_PIN** 則只負責 LBA 的存取權限，不影響設備的全域安全設定
    
- **要解除某個 LBA 的鎖定，可能需要 Admin SP 來授權 Locking SP 進行修改**