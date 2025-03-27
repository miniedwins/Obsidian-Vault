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