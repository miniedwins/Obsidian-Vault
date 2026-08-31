驗證 **Message Integrity Check (MIC)** 時，其計算範圍是**從 NVMe-MI 訊息本體（Message Body）的第一個位元組（Byte 0）開始，一直計算到最後一個位元組（Byte Y-1，即 MIC 欄位的最後一個位元組，Byte N+3）結束**。

以下為該驗證與計算範圍中各個位元組與欄位的詳細對應說明：

### 1. 起始與結束位置的定義

- **起始位元組：Byte 0** — 這是整個 NVMe-MI Message Body 的起點，亦即訊息標頭（Message Header）的第一個 Byte。
- **結束位元組：Byte Y - 1**（若不包含 MIC 的訊息長度為 \(N\) 位元組，則結束於 **Byte N + 3**）— 這是整個訊息的終點，即 32-bit MIC 欄位本身的最後一個位元組。在計算或驗證 CRC 時，此 4 位元組的 MIC 欄位會先被**清零 (cleared to 0h)**，再將包含此清零欄位在內的完整 \(Y\) 位元組當作整體投入多項式計算。

---

### 2. 計算範圍內的逐一欄位解析（Byte 0 至 Byte N+3）

根據 **NVMe-MI 規格書** 的訊息格式定義，MIC 的計算完全覆蓋了以下區段：

#### **Byte 0：MCTP Data (MCTPD)**

這是 Message Header 的第一個位元組，包含以下關鍵控制位元：

- **Bit 7 - Integrity Check (IC)**：**完整性檢查啟用位元**。在 out-of-band 機制中，此位元必須設為 `1b`，代表該訊息受 MIC 保護。
- **Bit 6:0 - Message Type (MT)**：**MCTP 訊息類型**。對於所有 NVMe-MI 訊息，此欄位必須固定設為 `4h`（代表 NVMe-MI 協議）。

#### **Byte 1：NVMe-MI Message Parameters (NMP)**

- **Bit 7 - Request or Response (ROR)**：定義此訊息為請求（`0b`）或回應（`1b`）。
- **Bit 6:3 - NVMe-MI Message Type (NMIMT)**：指定 NVMe-MI 的具體訊息類型（例如：Control Primitive、NVMe-MI Command 等）。
- **Bit 2:0**：其他參數定義（如 MEB 位元等）。

#### **Byte 2 & Byte 3：Message Header 的剩餘欄位**

- 包含 **Command Slot Identifier (CSI)** 或是保留位元，與 Byte 0 和 Byte 1 共同組成 4 位元組的 **Message Header (Dword 0)**。

#### **Byte 4 到 Byte N - 1：Message Data**

- 此區段為**訊息的實際負載（Payload）**，其長度依據不同指令而異（例如 Get Log Page 的傳回數據或指令參數等）。

#### **Byte N 到 Byte N + 3：Message Integrity Check (MIC)**

- 這是 **32-bit 的 CRC 欄位**，採用 **CRC-32C (Castagnoli)** 演算法（其生成多項式為 `1EDC6F41h`）。
- **計算/驗證時的特殊處理**：在將整個訊息（Byte 0 至 Byte N+3）送入 CRC 計算前，必須先將 Byte N 至 Byte N+3 **全部填入 0h**。

---

### 3. MIC 完整性驗證的核心步驟

當接收端（Endpoint）收到 NVMe-MI 訊息並欲進行 MIC 驗證時，底層的運作流程如下：

1. **暫存原始 MIC**：先將收到的 4 位元組 MIC 值（Byte N 至 N+3）存入臨時變數。
2. **暫存器初始化**：將 CRC 暫存器初始化為 `FFFFFFFFh`。這相當於直接將 NVMe-MI 訊息的第一個 Dword（即 Byte 0 至 3 的 Message Header）進行位元反轉處理。
3. **清零 MIC 欄位**：將訊息尾部的 MIC 欄位暫時清空為 `0h`。
4. **多項式除法**：將整包已清零 MIC 且經過位元映射（reflected）的 \(Y\) 位元組資料，除以 `1EDC6F41h` 得到 32-bit 餘數。
5. **反轉與反相**：對該餘數進行位元反轉（reflected）與反相（inverted，即取其 1 的補數）處理，產生新的 32-bit CRC 值。
6. **比對確認**：將新計算出的值與步驟 1 備份的原始 MIC 值比對，若兩者完全相同則通過校驗，代表資料完整無損。

---

💡 想要我為您提供一份符合 CRC-32C (Castagnoli) 演算法的 Python 驗證範例程式碼，以便您在自動化測試腳本中快速計算或比對 MIC 的正確性嗎？