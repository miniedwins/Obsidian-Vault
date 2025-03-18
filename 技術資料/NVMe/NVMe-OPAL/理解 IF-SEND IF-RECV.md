### **🚀 簡單理解 IF-SEND / IF-RECV**

1. **Host 使用 IF-SEND**
    
    - **將方法呼叫（Method Invocation）** 轉換為 **Token 並封裝成 ComPacket**。
    - **透過 IF-SEND 命令** 將 ComPacket 傳送到 **TPer**。
    - **如果數據量太大，需要多個 IF-SEND 才能發送完整的請求**。
2. **TPer 處理請求**
    
    - **TPer 解析收到的 ComPacket**，執行對應的方法。
    - **當計算完成後，準備回應結果**。
3. **Host 使用 IF-RECV 來獲取回應**
    
    - **Host 持續使用 IF-RECV 輪詢（polling）TPer**，確認是否有結果。
    - **當 TPer 準備好回應後，透過 IF-RECV 回傳 Tokenized 結果**。
    - **如果結果數據較大，可能需要多個 IF-RECV 來完整獲取**。

---

### **📌 具體流程舉例**

假設 **Host** 想要查詢 **TPer** 的最大可傳輸封包大小（MaxComPacketSize），流程可能如下：

1️⃣ **Host 透過 IF-SEND 傳送請求**

csharp

複製編輯

`Host → TPer IF-SEND: [Method Invocation Tokenized Data]`

2️⃣ **TPer 收到請求，開始處理**

nginx

複製編輯

`TPer 解析 ComPacket，執行對應的方法`

3️⃣ **Host 透過 IF-RECV 輪詢，等待結果**

makefile

複製編輯

`Host → TPer IF-RECV: Host: "TPer，你準備好回應了嗎？"`

4️⃣ **TPer 回應查詢結果**

yaml

複製編輯

`TPer → Host IF-RECV: Response Data: MaxComPacketSize = 4096`

5️⃣ **如果結果較大，Host 可能需要多次 IF-RECV 來完整接收**

python-repl

複製編輯

`IF-RECV (第一次)  → 先回傳部分資料 IF-RECV (第二次)  → 回傳剩餘資料 ...`

---

### **🔍 FAQ：這種機制有什麼好處？**

✅ **支援大數據傳輸**：

- 因為方法請求和回應可能很大，允許 **多個 IF-SEND / IF-RECV** 來完成資料傳輸。

✅ **減少 TPer 負擔**：

- Host **不會一直佔用 TPer**，而是透過 IF-RECV 輪詢，**讓 TPer 有足夠的時間準備回應**。

✅ **符合 TCG 設計標準**：

- IF-SEND / IF-RECV 是 **TCG Storage 標準通訊方式**，支援 **Opal、Enterprise SSC** 等規範。

---

### **💡 結論**

- **IF-SEND** 是 **用來傳送請求** 給 TPer。
- **IF-RECV** 是 **用來查詢/接收** TPer 的回應。
- **為了傳輸大數據，可能需要多個 IF-SEND / IF-RECV** 來完成一次完整的交互。
- 這套機制可以讓 **Host 非同步地請求 TPer**，確保 TPer 不會因為請求過載而卡住。