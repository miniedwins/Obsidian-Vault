### 1. **成功啟動會話的三個獨立要求**

成功啟動會話需要滿足以下三個獨立要求：

#### 1. **資源充足**

- **TPer** 和請求的 **SP（Security Provider）** 必須有足夠的資源來支持會話。
    
- 例如，足夠的內存、處理能力和會話槽（Session Slots）。
    

#### 2. **成功協商交換密鑰（如果需要）**

- 如果需要使用密鑰交換的安全通信（Secure Messaging with Key Exchange），則必須成功協商交換密鑰。
    
- 這通常涉及 **HostExchangeAuthority** 和 **SPExchangeAuthority** 的使用。
    

#### 3. **成功完成認證**

- 必須成功完成以下其中一種認證：
    
    - **a. 主機向 SP 認證**：主機向 SP 證明自己的身份。
        
    - **b. SP 向主機認證**：SP 向主機證明自己的身份。
        
    - **c. 雙向認證**：主機和 SP 互相認證。
        
    - **d. 無需認證**：某些會話可能不需要認證。
        

---

### 2. **會話啟動的流程**

會話啟動通過 **Session Manager** 協議層的兩個或四個方法交換完成：

#### 基本流程（兩個方法）：

1. **StartSession**：
    
    - 主機發送 **StartSession** 方法，請求啟動會話。
        
2. **SyncSession**：
    
    - TPer 返回 **SyncSession** 方法，確認會話啟動。
        

#### 擴展流程（四個方法，如果需要挑戰-回應或密鑰交換）：

3. **StartTrustedSession**（可選）：
    
    - 如果需要挑戰-回應或密鑰交換，主機發送 **StartTrustedSession** 方法。
        
4. **SyncTrustedSession**（如果使用 **StartTrustedSession** 則必須）：
    
    - TPer 返回 **SyncTrustedSession** 方法，確認挑戰-回應或密鑰交換完成。
        

---

### 3. **權限（Authorities）**

會話啟動過程中使用的權限決定了安全通信和認證的要求。以下是相關的權限：

#### a. **HostExchangeAuthority**

- 引用主機的 **Exchange Key**，用於會話密鑰的交換，並提供隱式認證（Implicit Authentication）。
    

#### b. **HostSigningAuthority**

- 引用主機的 **Signing Key**（用於挑戰-回應認證）或 **C_PIN** 憑證（用於密碼認證）。
    
- 用於主機的認證，並提供會話啟動方法的完整性。
    

#### c. **SPExchangeAuthority**

- 引用 SP 的 **Exchange Key**，用於會話密鑰的交換，並提供隱式認證。
    

#### d. **SPSigningAuthority**

- 引用 SP 的 **Signing Key**，用於 SP 向主機的認證，並提供會話啟動方法的完整性。
    

---

### 4. **權限的使用**

- **主機權限**：
    
    - 主機權限（例如 **HostExchangeAuthority** 和 **HostSigningAuthority**）在 **StartSession** 方法中傳遞。
        
- **SP 權限**：
    
    - SP 權限（例如 **SPExchangeAuthority** 和 **SPSigningAuthority**）可能被引用在主機權限的 **Authority Table** 中。
        
- **證書鏈**：
    
    - 如果權限是公鑰權限（PuK），則可以通過證書鏈提供額外信息。
        
    - 有效的權限（Effective Authority）是證書鏈的最終公鑰。
        

---

### 5. **挑戰-回應與安全通信**

- 如果 **HostSigningAuthority** 或 **SPSigningAuthority** 需要挑戰-回應（例如 PuK、SymK 或 HMAC 權限），或者需要使用安全通信，則必須在 **StartSession** 和 **SyncSession** 之後使用 **StartTrustedSession** 和 **SyncTrustedSession**。
    

---

### 6. **會話啟動的異步性**

- 由於會話啟動的異步性，**StartSession** 和 **StartTrustedSession** 的回應（分別是 **SyncSession** 和 **SyncTrustedSession**）被格式化為對主機的方法調用。
    

---

### 7. **總結**

- 成功啟動會話需要滿足資源充足、成功協商交換密鑰（如果需要）和成功完成認證。
    
- 會話啟動通過 **StartSession**、**SyncSession**、**StartTrustedSession** 和 **SyncTrustedSession** 方法完成。
    
- 權限（例如 **HostExchangeAuthority** 和 **SPSigningAuthority**）決定了安全通信和認證的要求。
    
- 如果需要挑戰-回應或密鑰交換，則必須使用 **StartTrustedSession** 和 **SyncTrustedSession**。