## **1. Subpacket Types（子封包類型）**

**Subpacket** 是 **Packet（封包）** 的細分單位，每個 Subpacket 具有不同的用途，例如：

|**子封包類型**|**用途**|
|---|---|
|**Data Subpacket**|傳輸數據，例如 Opal 命令或參數。|
|**Credit Control Subpacket**|控制訊息，例如流量控制，確保 TPer 有足夠的資源處理 Host 的請求。|
|**其他控制子封包**|用於握手、錯誤回應等。|

---

## **2. Data SubPacket Format（數據子封包格式）**

**Data Subpacket** 主要用來傳輸 **Opal 命令** 和 **參數**，格式如下：

pgsql

複製編輯
+------------------------+
| Subpacket Header (2 bytes) |
+------------------------+
| Payload Data (變長)       |
+------------------------+

- **Subpacket Header**（2 Bytes）：包含子封包的類型、長度等資訊。
- **Payload Data**（變長）：實際的命令或數據內容。

例如：

plaintext

複製編輯

`0x01 0x10  [Data Payload]`

- `0x01` → Subpacket 類型（Data Subpacket）
- `0x10` → Payload 長度（16 bytes）
- `[Data Payload]` → 實際的 TCG Opal 命令數據

---

## **3. Credit Control Subpacket（信用控制子封包）**

這類子封包的主要作用是進行流量控制，確保 TPer 在處理請求時不會超載。

📌 **運作方式：**

1. **Host 發送請求**：請求可能包含多個 Data Subpacket。
2. **TPer 回應 Credit Control Subpacket**：
    - **回應 Host**：「還可以傳輸多少數據？」
    - **如果資源不足**，TPer 可能會要求 Host 暫停傳輸。
3. **Host 根據 Credit 調整傳輸速率**。

**格式範例**：

lua

複製編輯
+------------------------+
| Credit Subpacket Header (2 bytes) |
+------------------------+
| Remaining Credit (1 byte) |
+------------------------+

- **Header**：標記這是一個 Credit Control Subpacket
- **Remaining Credit**（剩餘可用資源）：TPer 告知 Host 剩餘多少傳輸資源

舉個例子：

plaintext

複製編輯

`0x02 0x01 0x10`

- `0x02` → 表示這是 Credit Control Subpacket
- `0x01` → Header 長度
- `0x10` → 剩餘 Credit（Host 只能再發送 16 bytes 的數據）

---

## **總結**

1. **Subpacket** 是封包內的數據單元，不同類型有不同用途：
    - **Data Subpacket**：傳輸 Opal 命令和數據。
    - **Credit Control Subpacket**：控制流量，避免 TPer 超載。
2. **Credit Control 機制**：
    - **TPer 回應 Host：「還可以發送多少數據？」**
    - **Host 根據 Credit 決定繼續傳輸或等待**

這樣的機制確保 Host 和 TPer 之間的溝通順暢，不會因為過量請求導致 TPer 無法處理。 ✅