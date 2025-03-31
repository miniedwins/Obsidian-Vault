### 1. **TPer Session Manager (TSM)**

- **定義**：
    
    - **TSM** 是 **TPer（Trusted Platform Module Enhanced Reset）** 中的一個組件，負責管理與主機之間的會話。
        
- **功能**：
    
    - 處理會話的建立、維護和終止。
        
    - 分配 **TPer Session Number (TSN)**，用於標識 TPer 端的會話。
        
    - 與 **Host Session Manager (HSM)** 協調，確保會話的正確執行。
        

---

### 2. **Host Session Number (HSN)**

- **定義**：
    
    - **HSN** 是主機端分配的一個會話標識符，用於標識主機端的會話。
        
- **功能**：
    
    - 用於區分主機端的不同會話。
        
    - 在會話建立過程中，**HSN** 與 **TSN** 組合形成 **Session Number (SN)**，用於唯一標識一個會話。
        

---

### 3. **TSM 與 HSN 的關係**

- **會話建立**：
    
    - 在會話建立過程中，**HSM** 分配一個 **HSN**，並將其發送給 **TSM**。
        
    - **TSM** 分配一個 **TSN**，並將其返回給 **HSM**。
        
    - **HSN** 和 **TSN** 組合形成 **SN**，用於唯一標識該會話。
        
- **會話管理**：
    
    - **TSM** 和 **HSM** 共同管理會話的生命週期，包括會話的建立、維護和終止。
        
- **流控制**：
    
    - **TSM** 和 **HSM** 負責會話的流控制，確保數據的正確傳輸。
        

---

### 4. **Host Session Number 的範圍**

- **主機端**：
    
    - **HSN** 是主機端分配的一個標識符，用於標識主機端的會話。
        
    - 每個主機端會話都有一個唯一的 **HSN**。
        
- **多主機環境**：
    
    - 在多主機環境中，每個主機可以獨立分配 **HSN**，並與 **TSM** 協調管理會話。
        

---

### 5. **會話建立的示例**

以下是會話建立的典型流程：

#### 步驟 1：HSM 分配 HSN

- **HSM** 分配一個新的 **HSN**，例如 **HSN = 0x1234**。
    

#### 步驟 2：HSM 發送 StartSession 方法

- **HSM** 通過 **IF-SEND** 命令發送 **StartSession** 方法給 **TSM**，並提供 **HSN**。
    

#### 步驟 3：TSM 分配 TSN

- **TSM** 接收 **StartSession** 方法，並分配一個 **TSN**，例如 **TSN = 0x5678**。
    

#### 步驟 4：TSM 返回 SyncSession 回應

- **TSM** 返回 **SyncSession** 回應給 **HSM**，並提供 **TSN**。
    

#### 步驟 5：會話建立完成

- **HSM** 和 **TSM** 使用 **SN = (HSN, TSN)** 標識該會話。
    
- 會話建立完成，主機與 TPer 可以開始進行數據交換。
    

---

### 6. **總結**

- **TPer Session Manager (TSM)** 是 TPer 端的會話管理組件，負責管理會話的建立、維護和終止。
    
- **Host Session Number (HSN)** 是主機端分配的一個會話標識符，用於標識主機端的會話。
    
- **TSM** 和 **HSM** 共同管理會話的生命週期，並通過 **HSN** 和 **TSN** 組合形成 **SN**，用於唯一標識一個會話。