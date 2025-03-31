在這段描述中，**"outside of a transaction"** 指的是 **沒有包裹在任何明確的交易 (transaction) 操作內部** 的方法調用。這與 **"within a transaction"** (在交易內) 形成對比。

### **交易 (Transaction) 內部 vs. 外部**

1. **Within a transaction (在交易內)**
    
    - 當 SP (Security Provider) 相關操作是在一個交易範圍內執行時，這些操作只有在整個交易成功提交 (commit) 之後才會生效。
        
    - 如果交易失敗或回滾 (rollback)，則不會有任何變更被保存。
        
2. **Outside of a transaction (在交易外)**
    
    - 如果 SP 相關操作**沒有在交易內執行**，則 **TPer (Trusted Peripheral)** 會立即處理該方法，並在處理完成後回應結果。
        
    - 在這種情況下，一旦該操作完成並回應，SP 便被正式建立，而不需要透過交易提交 (commit)。
        

### **關鍵影響**

- **如果在交易內進行 SP 發行**
    
    - 只有當整個交易提交後，SP 才算正式建立。
        
    - 若交易回滾，則 SP 發行會被取消。
        
- **如果在交易外發行 SP**
    
    - **發行後立即生效**，不會受到交易機制影響。
        
    - 一旦 TPer 處理完成，SP 就無法再變更或回滾。
        

### **為何這很重要？**

該段規範還強調了一個重要概念：

> **"Once an SP is issued, it is not possible to add functionality to the SP from additional templates."**

這表示：

- **SP 必須在發行時決定所有功能，之後無法透過額外的模板來擴充。**
    
- 若 **SP 發行在交易內**，可以確保完整性，因為如果有問題可以回滾。
    
- 若 **SP 發行在交易外**，則一旦處理完畢，**不能再變更**，這會讓 SP 發行更加不可逆。
    

如果你要決定使用 **transaction** 或 **non-transactional issuance**，應該考慮：

- **是否需要回滾機制？**
    
- **是否需要確保所有操作一起提交？**
    
- **是否可以接受 SP 發行後不可變更？**
    

這樣可以決定是否應該使用交易機制來包裹 SP 發行的操作。

在 TCG Storage Security Subsystem Class (SSC) 規範中，**ComPacket、Packet、Data SubPacket、Data Payload** 是不同層級的封裝單位，而「交易內」與「交易外」的概念主要與 **Packet 的 Transaction Flag** 有關。讓我們逐步拆解這些概念：

---

## **封裝層級解釋**

1. **ComPacket (Communication Packet)**
    
    - 最高層級的封裝，通常用於封裝多個 Packet，提供通信的基本框架。
        
    - 它包含 **Packet**，但本身不涉及交易管理。
        
2. **Packet**
    
    - **交易 (Transaction) 的基本單位**，負責管理交易開始、提交 (Commit) 或回滾 (Rollback)。
        
    - **是否為交易內或交易外的關鍵點** 在於 **Transaction Flags**：
        
        - **如果 Packet 的 Transaction Flags 設定為開始交易 (Start Transaction)，則後續的操作都在交易內。**
            
        - **如果沒有 Transaction Flags，則屬於交易外 (即單獨執行的方法調用，不受交易影響)。**
            
3. **Data SubPacket**
    
    - Packet 的內部數據部分，負責分割數據，允許較大數據量的傳輸。
        
    - 它不影響交易機制，**僅用來封裝數據**。
        
4. **Data Payload**
    
    - 最底層的數據內容，真正要傳輸或操作的數據部分。
        
    - 這一層純粹是數據，不影響交易範圍。
        

---

## **交易內 vs. 交易外**

|**封裝層級**|**是否與交易機制相關**|**是否影響交易內/外**|
|---|---|---|
|**ComPacket**|❌ 只是一個封裝，不管理交易|❌|
|**Packet**|✅ 是交易的基本單位，取決於 Transaction Flag|✅ 決定是否為交易內|
|**Data SubPacket**|❌ 只用來傳輸數據，無交易概念|❌|
|**Data Payload**|❌ 只是數據內容，無交易概念|❌|

---

### **如何判斷某個操作是交易內還是交易外？**

1. **如果 Packet 設定了 Start Transaction (開始交易)**
    
    - **之後的所有操作 (方法調用、數據變更) 都在交易內，直到 Commit (提交) 或 Rollback (回滾)。**
        
    - 這樣可以確保多個操作一起執行，避免中途發生錯誤導致部分變更生效，部分失敗。
        
2. **如果 Packet 沒有 Transaction Flag (即沒有 Start Transaction)**
    
    - **該方法調用或操作就是交易外 (non-transactional)。**
        
    - **操作會立即生效，無法回滾 (Rollback)，也不需要 Commit。**
        

---

## **舉例**

假設你要執行某個方法：

### **交易內 (Transactional Execution)**

plaintext

複製編輯

`ComPacket  ├── Packet (Start Transaction)  ← **開始交易**  │    ├── Data SubPacket  │    │    ├── Data Payload (Method Invocation)  │    ├── Data SubPacket  │    │    ├── Data Payload (Method Invocation)  │    ├── Packet (Commit Transaction)  ← **提交**`

- 這種情況下，只有當 **Commit Transaction** 被執行後，所有變更才會生效。
    
- 如果中間某個操作失敗，可以執行 **Rollback Transaction** 來還原。
    

---

### **交易外 (Non-Transactional Execution)**

plaintext

複製編輯

`ComPacket  ├── Packet  ← **沒有 Start Transaction，單獨執行**  │    ├── Data SubPacket  │    │    ├── Data Payload (Method Invocation)`

- 這裡的 **方法調用會立即生效，無法回滾**。
    
- 不需要 Commit，也不支持 Rollback。
    

---

## **結論**

- **是否為交易內，取決於 Packet 的 Transaction Flags**。
    
- **ComPacket、Data SubPacket、Data Payload** 本身**與交易機制無關**，只是數據封裝的不同層級。
    
- **Packet 是關鍵，決定是否是交易內 (Transactional) 或交易外 (Non-Transactional)**。