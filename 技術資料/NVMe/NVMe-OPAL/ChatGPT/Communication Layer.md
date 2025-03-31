### 1. **通信層的定位**

- **雙向通信**：
    
    - 通信層是主機（Host）與 **TPer（Trusted Platform Module Enhanced Reset）** 之間進行雙向通信的第一個層次。
        
- **使用 ComID**：
    
    - 在通信層，主機已經分配了一個 **ComID（Communication ID）**，用於標識通信會話。
        
- **封包化與令牌化**：
    
    - 通信層的數據是 **封包化（Packetized）** 和 **令牌化（Tokenized）** 的。
        

---

### 2. **通信層的特性**

- **命令類型**：
    
    - 通信層處理 **IF-SEND** 和 **IF-RECV** 命令，且這些命令的 **Protocol ID** 必須為 **0x01**。
        
- **有效的 ComID**：
    
    - 通信層的命令必須使用一個 **有效的、活動的 ComID**。
        
- **控制會話（Control Session）**：
    
    - 通信層的通信發生在 **TPer 會話管理器（TSM, TPer Session Manager）** 和 **主機會話管理器（HSM, Host Session Manager）** 之間。
        
    - 每個 **ComID** 對應一個 **控制會話**，控制會話在 **ComID** 被分配時開始，在 **ComID** 變為非活動狀態時終止。
        

---

### 3. **通信層的功能**

- **管理常規會話（Regular Session）的啟動**：
    
    - 通信層的主要任務之一是管理常規會話的啟動。
        
    - 在啟動過程中，**TSM** 和 **HSM** 分別分配 **TSN（TPer Session Number）** 和 **HSN（Host Session Number）**，這些編號組成了會話的 **SN（Session Number）**。
        
- **流控制（Flow Control）**：
    
    - 通信層的流控制方式與常規會話的流控制方式相同，但通信發生在 **TSM** 和 **HSM** 之間。
        
    - **TSM** 和 **HSM** 負責管理流控制。
        

---

### 4. **常規會話的啟動流程**

以下是常規會話的啟動流程：

#### 步驟 1：分配 HSN

- **HSM** 分配一個新的 **HSN（Host Session Number）**。
    
- **HSM** 可以確保新的 **HSN** 與其他會話的 **HSN** 不同，但這不是強制要求。
    

#### 步驟 2：發送 StartSession 方法

- **HSM** 通過 **IF-SEND** 命令發送 **StartSession** 方法給 **TSM**。
    

#### 步驟 3：TSM 處理 StartSession 方法

- **TSM** 處理 **StartSession** 方法，並分配一個 **TSN（TPer Session Number）**。
    

#### 步驟 4：返回 SyncSession 回應

- **TSM** 返回 **SyncSession** 回應給 **HSM**。
    
- 對於不需要挑戰-回應（Challenge-Response）或密鑰交換（Key Exchange）的會話，常規會話在 **SyncSession** 回應返回後被視為開啟。
    

#### 步驟 5：處理 StartTrustedSession 方法（可選）

- 對於需要挑戰-回應或密鑰交換的會話，**HSM** 發送 **StartTrustedSession** 方法給 **TSM**。
    
- **TSM** 處理 **StartTrustedSession** 方法，並準備 **SyncTrustedSession** 回應。
    
- 常規會話在 **SyncTrustedSession** 回應返回後被視為開啟。
    

---

### 5. **控制會話的生命週期**

- **開始**：
    
    - 控制會話在 **ComID** 被分配時開始。
        
- **結束**：
    
    - 控制會話在 **ComID** 變為非活動狀態時終止。
        

---

### 6. **總結**

- **通信層** 是主機與 TPer 之間進行雙向通信的第一個層次，使用 **ComID** 標識通信會話。
    
- 通信層的主要任務是管理常規會話的啟動，並處理 **IF-SEND** 和 **IF-RECV** 命令。
    
- 常規會話的啟動流程包括分配 **HSN**、發送 **StartSession** 方法、處理 **SyncSession** 回應，以及可選的 **StartTrustedSession** 和 **SyncTrustedSession** 處理。