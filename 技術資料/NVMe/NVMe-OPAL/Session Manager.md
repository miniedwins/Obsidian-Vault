### 1. **Control Session（控制會話）**

- **定義**：
    
    - **Control Session** 是與 **ComID（Communication ID）** 綁定的一個會話，用於管理會話的建立、維護和終止。
        
- **生命週期**：
    
    - **Control Session** 的生命週期與 **ComID** 的生命週期綁定：
        
        - 當 **ComID** 被分配時，**Control Session** 開始。
            
        - 當 **ComID** 被釋放時，**Control Session** 終止。
            
- **流控制**：
    
    - **Control Session** 的流控制方式與 **Regular Session（常規會話）** 相同，但通信發生在 **TPer Session Manager (TSM)** 和 **Host Session Manager (HSM)** 之間。
        
- **唯一性**：
    
    - 每個 **ComID** 只能有一個 **Control Session**。
        

---

### 2. **Session Manager 中的其他會話類型**

- **Session Manager** 層處理多種會話類型，包括：
    
    1. **Control Session**：
        
        - 用於管理會話的建立、維護和終止。
            
    2. **Regular Session（常規會話）**：
        
        - 用於數據傳輸和高級操作（例如加密、身份驗證）。
            
    3. **Trusted Session（可信會話）**：
        
        - 用於需要挑戰-回應（Challenge-Response）或密鑰交換（Key Exchange）的操作。
            

---

### 3. **Session Manager 層的方法**

- **Session Manager** 層的方法包括：
    
    - **Properties**：獲取或設置會話屬性。
        
    - **StartSession**：啟動一個新的會話。
        
    - **SyncSession**：同步會話狀態。
        
    - **StartTrustedSession**：啟動一個可信會話。
        
    - **SyncTrustedSession**：同步可信會話狀態。
        
    - **CloseSession**：關閉會話。
        
- **傳輸要求**：
    
    - 所有 **Session Manager** 層的方法必須在 **Packet.Session = 0x00000000_00000000** 的數據包中傳輸。
        

---

### 4. **會話的啟動與數據傳輸**

- **會話啟動**：
    
    - 會話啟動協議完成後，會話被視為開啟。
        
    - **Packet.Session** 的值是 **TSN（TPer Session Number）** 和 **HSN（Host Session Number）** 的組合。
        
- **數據傳輸**：
    
    - 會話開啟後，數據可以在該會話中傳輸。
        
    - **Packet.Session** 的值用於標識數據包屬於哪個會話。
        

---

### 5. **Control Session 與 Regular Session 的區別**

|特性|Control Session|Regular Session|
|---|---|---|
|用途|管理會話的建立、維護和終止|數據傳輸和高級操作|
|生命週期|與 ComID 綁定|與會話綁定|
|流控制|由 TSM 和 HSM 負責|由會話雙方負責|
|唯一性|每個 ComID 只能有一個 Control Session|每個會話有一個唯一的 SN|

---

### 6. **總結**

- **Control Session** 是與 **ComID** 綁定的一個會話，用於管理會話的建立、維護和終止。
    
- **Session Manager** 層處理多種會話類型，包括 **Control Session**、**Regular Session** 和 **Trusted Session**。
    
- 所有 **Session Manager** 層的方法必須在 **Packet.Session = 0x00000000_00000000** 的數據包中傳輸。
    
- 會話啟動後，數據可以在該會話中傳輸，**Packet.Session** 的值用於標識數據包屬於哪個會話。