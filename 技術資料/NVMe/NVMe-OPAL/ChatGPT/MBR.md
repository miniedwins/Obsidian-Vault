這個欄位**與 MBR (Master Boot Record) 保護機制有關**，確保當 TPer (Trusted Peripheral, 即 Self-Encrypting Drive 的安全處理單元) **尚未完成 MBR 表處理時，主機只能讀取 MBR 表內的數據**。

---

### **1. `Done` 欄位的作用**

- **當 `Done == False` (未完成狀態)**：
    
    - **LBA 0 ~ MBR 表範圍內的區塊**，**主機只能讀取 MBR 表的內容**，無法存取真正的磁碟數據。
        
    - 這通常發生在 **裝置重置 (Reset Event) 之後**，TPer 尚未完成處理 MBR 表。
        
- **當 `Done == True` (完成狀態)**：
    
    - TPer 表示已處理完成，**主機可以正常存取 LBA 0 ~ MBR 範圍內的實際磁碟數據**。
        
    - **主機需要手動設定 `Done = True` 才能解除限制**。
        

---

### **2. `MBRDoneOnReset` 的影響**

- 當發生 **Reset 事件** (例如重新上電、裝置初始化等)，如果 `MBRDoneOnReset` **設定為特定條件**，則 `Done` 會自動變為 `False`，這時候主機的 LBA 請求將被限制。
    
- 直到 **主機手動將 `MBRControl` 表內的 `Done` 欄位設為 `True`，限制才會解除**。
    

---

### **3. `Done` 欄位的行為流程**

1. **發生 Reset (根據 `MBRDoneOnReset` 設定)** → `Done` 設為 `False`。
    
2. **TPer 處理 MBR 表，確保開機安全**。
    
3. **主機無法直接存取 LBA 0 ~ MBR 範圍，TPer 只回應 MBR 表內的數據**。
    
4. **主機需手動設定 `Done = True`，恢復 LBA 正常存取**。
    

---

### **4. `Done` 欄位的設計目的**

這個機制的主要目的包括：

- **確保裝置 Reset 後，MBR 的安全性**。
    
- **防止未經授權的 LBA 讀取或修改** (可能是為了安全開機機制)。
    
- **讓主機有機會確認並設定 MBR 的狀態，確保設備正常運作**。