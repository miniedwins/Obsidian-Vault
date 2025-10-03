### 1️⃣ 為什麼 Revert SP 後要斷掉 Session？

根據 **TCG Opal 規範 (2.01 / 2.02, §3.3.7 RevertSP)**：

- RevertSP 會把 **該 SP 的所有狀態恢復到出廠值**（包含 LockingInfo、Authorities、Table contents 等）。
    
- 當 SP 被 reset 之後，**現有的 session context 對應的 SP 就不再存在了**。
    
    > 因為 session 綁定的是一個特定 SP instance（例如 Locking SP），一旦這個 SP 被 revert，session 的安全上下文就失效，規範規定必須強制中止 session。
    
- 所以：RevertSP 成功後，host 不該繼續使用原本的 session，而應該重新走 StartSession。
    

👉 也就是說「斷掉 session」其實是 **規範要求**，不是 implementation bug。

---

### 2️⃣ 為什麼 Revert 後還能送 Get 方法？

這部分要分兩個層次來看：

- **傳輸層 (ComPacket/Session header)**  
    NVMe/TPer 只是單純收你的 ComPacket，把它 decode 成 TCG tokens，然後才決定是否回應。  
    如果你在 RevertSP 之後還用同一個 TSN/HSN 送 Get，TPer 可能還會「接受並解析」你的封包。
    
- **語意層 (TCG Method Execution)**  
    規範要求：
    
    - RevertSP 成功後，**SP LifeCycle 應該回到 Manufactured / Inactive 狀態**。
        
    - 如果你對一個已經 Revert 的 SP 再呼叫 method（例如 Get），應該要回覆「Command not valid in this state」或乾脆不回資料（像你 trace 裡的情況：response payload 為空，Method Status Code 成功，但沒有任何物件）。
        

👉 所以，你看到「還能送 Get」只是因為 **session 的封包通道還在**，但實際上 SP 已經 reset，Get 根本查不到東西，等同於 session 已經失效。

---

### 3️⃣ 為什麼不是直接報錯 (Method Status Fail)？

這取決於不同廠商的實作：

- 有些 TPer 會在 RevertSP 後對任何舊 session request 都回 `FAIL`。
    
- 有些（像你測到的）會回 `SUCCESS` 但資料是空的，等於告訴你「我收到了，但這個 SP 已經沒內容」。
    
- 規範沒有強制錯誤碼要怎麼回，只是規定 session 必須無效化。
    

---

✅ 總結：

- RevertSP **必須中止該 SP 的所有 sessions** → 這是規範要求，不是 bug。
    
- 你之所以還能送 Get，只是因為傳輸 session 還在，但 SP 已 reset → 所以才會回空資料。
    
- 更嚴謹的實作應該會直接回 `FAIL` 或斷掉 session。