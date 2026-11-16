
在 NVMe Base Specification（Revision 2.3）中，**LID 07h（Telemetry Host-Initiated）與 LIDSP 的關聯在規範中有完整且嚴謹的鏈結**。

以下透過規格書的條文、圖表編號與機制流程，證明這兩者是如何緊密關聯的：

---

### 一、 怎麼知道 LID 07h 有特定擴充能力？

要判斷控制器是否支援 LID 07h 的特定擴充能力，必須透過 **`Supported Log Pages (LID 00h)`** 來檢查：

1. **查閱 LID 00h 內對應 LID 07h 的項目**：
    - 每個 LID 在 LID 00h 中佔用 4 個 Bytes（Figure 207: LIDS7，位於 Offset `1Ch～1Fh`）。
    - 結構為 **Figure 208: LID Supported and Effects Data Structure**：
        - **Bits 00**：`LSUPP`（LID 07h 是否支援）。
        - **Bits 31:16**：**`LIDSP`（LID Specific Parameter，專屬特定參數）**。
2. **LID 07h 的 LIDSP 內部定義（Figure 219）**：
    - 規格書 Section 5.2.12.1.8 特別定義了 **Figure 219: Telemetry Host-Initiated Log Page - LID Specific Parameter Field**：
        - **Bit 0 — `MCDAS`（Maximum Created Data Area Support，最大建立資料區支援能力）**：
            - **`1`**：控制器支援主機在請求收集 Telemetry 時，**指定限制建立的資料區範圍**（例如只產生 Data Area 1，或 Area 1～2，避免每次都耗時產生龐大的 Area 3/4）。
            - **`0`**：不支援此限制建立功能。
        - **Bits 15:01**：保留填 0。

**白話判斷**：若讀取 LID 00h 時，Offset `1Eh～1Fh`（即 LIDS7 的 Bits 31:16）回傳的數值其 **Bit 0 為 `1`**，就證明此裝置具備此特定擴充能力。

---

### 二、 Telemetry Host-Initiated Log Page 本身有寫嗎？

這取決於您問的是**「能力宣告」**還是**「實際產生的資料」**：

1. **Log Page 本身的資料內容（Figure 218: Bytes 00～511 Header）**：
    - **裡面沒有 `MCDAS` 這個位元**。Figure 218 記錄的是**「當次擷取的狀態與結果」**，例如：
        - `THDA1LB` ～ `THDA4LB`（Data Area 1 到 Area 4 的實際最後區塊編號）。
        - `THDGN`（Telemetry 資料產生世代計數器）。
        - `THS`（Scope：Controller 還是 NVM Subsystem 範圍）。
2. **規格書的章節編排**：
    - **Figure 219（LIDSP 定義）正是寫在 Section 5.2.12.1.8（Telemetry Host-Initiated）章節的最末尾**！
    - 規格書將各 Log Page 的 LIDSP 定義緊附在該 Log Page 的章節最後，作為其延伸能力的依據。

---

### 三、 規格書證明鏈（如何證明 LIDSP 與 Telemetry 產生關聯？）

在 NVMe Base Specification 內，這是一條**環環相扣的三步驟規格關聯鏈**：

```
[步驟 1: 宣告能力]
Supported Log Pages (LID 00h) -> Figure 208 的 Bits 31:16 (LIDSP)
對應 Section 5.2.12.1.8 的 Figure 219：宣告 MCDAS = 1
        │
        ▼ (關聯橋樑)
[步驟 2: 指令下發控制]
Get Log Page (LID 07h) SQE CDW10 -> Figure 217 的 Bits 11:09 (MCDA)
SPEC 明文強制綁定：只有 MCDAS = 1 時，MCDA 才生效！
        │
        ▼
[步驟 3: 執行結果反饋]
Telemetry Host-Initiated Log Page -> Figure 218
控制器依照 MCDA 限制，僅建立指定 Data Area 的 Last Block (THDAxLB)
```

#### 規格條文直接證據：

在 Section 5.2.12.1.8 的 **Figure 217（Telemetry Host-Initiated Log Specific Parameter Field）** 中，規格書明確將它們綁定在一起：

> _"**Maximum Created Data Area (MCDA): If the MCDAS bit is set to ‘1’ in the LID Specific Parameter field (refer to Figure 219)** and the Create Telemetry Host-Initiated Data bit is set to ‘1’, then this field specifies the data areas the host is requesting to be created in the log page... **If the MCDAS bit is cleared to ‘0’... then this field shall be ignored by the controller.**"_

同時在該章節內文也有強制規範：

> _"If the **MCDAS bit (refer to Figure 219) is set to ‘1’** and a Get Log Page command with the Create Telemetry Host-Initiated Data bit is set to ‘1’, then the maximum data area to be created in the Telemetry Host-Initiated log page **shall be less than or equal to the MCDA field in the Log Specific Parameter field** in Command Dword 10 (refer to Figure 217)."_

---

### 四、 結論

1. **怎麼知道？**：讀取 **LID 00h 的 Offset `1Ch～1Fh`（LIDS7）**，檢查高 16 位元（LIDSP）的 **Bit 0 是否為 `1`（MCDAS）**。
2. **Log Page 有寫嗎？**：Log Page 回傳的資料內容（Payload）記錄的是產生的結果（Data Area 1~4 Last Block），而**擴充能力的定義規則寫在 Section 5.2.12.1.8 的 Figure 219 中**。
3. **如何證明關聯？**：規格書 **Figure 217 的條文明確指名「參照 Figure 219 的 MCDAS」**；若 `MCDAS = 0`，Host 在下指令時（CDW10.LSP）填寫的 `MCDA` 參數將直接被硬體忽略，只有 `MCDAS = 1` 時，裝置才會受限並僅建立指定範圍的 Telemetry Data Area。

🔍 需要我為您列出當 `MCDAS = 1` 時，如何下發帶外 NVMe-MI 指令指定只採集 Data Area 1 的完整 Hex 封包範例嗎？