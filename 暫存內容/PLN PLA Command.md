根據腳本 [SBSUPPORT_10381_PLN_PLA_Power_Loss_Signaling.py](file:///C:/Users/edwin/Desktop/Workspace/sanblaze/scripts/NVMe_PLN_PLA/SBSUPPORT_10381_PLN_PLA_Power_Loss_Signaling.py#L68-L127) 內的實作，SANBlaze 透過 `sb_i2c2` 指令操作 M.2 轉接卡上的 I/O Expander 腳位。

以下假設你的目標插槽（Slot）編號為 `<slot>`（例如 Slot 0 就代換為 `0`）：

---

### 1. 查詢轉接卡支援的所有信號名稱
在開始前，可先列出該 Slot 轉接卡上所有可用的 `IOX_M2_*` 腳位名稱（[L79](file:///C:/Users/edwin/Desktop/Workspace/sanblaze/scripts/NVMe_PLN_PLA/SBSUPPORT_10381_PLN_PLA_Power_Loss_Signaling.py#L79)）：
```bash
sb_i2c2 -d <slot> -U -f ?
```

---

### 2. `PLN#` 控制指令（Read / Write）
`PLN#` 對應的腳位名稱為 **`IOX_M2_PLN_L`**（Low Active，低電位觸發，[L68](file:///C:/Users/edwin/Desktop/Workspace/sanblaze/scripts/NVMe_PLN_PLA/SBSUPPORT_10381_PLN_PLA_Power_Loss_Signaling.py#L68)、[L105-L113](file:///C:/Users/edwin/Desktop/Workspace/sanblaze/scripts/NVMe_PLN_PLA/SBSUPPORT_10381_PLN_PLA_Power_Loss_Signaling.py#L105-L113)）：

* **Write — 觸發 `PLN#` (Assert / 拉低電位)**：
  ```bash
  sb_i2c2 -d <slot> -U -f IOX_M2_PLN_L -w 0
  ```
* **Write — 釋放 `PLN#` (Deassert / 拉高電位)**：
  ```bash
  sb_i2c2 -d <slot> -U -f IOX_M2_PLN_L -w 1
  ```
* **Read — 讀取目前 `PLN#` 狀態**（看輸出中的 `Cur=0x...`）：
  ```bash
  sb_i2c2 -d <slot> -U -f IOX_M2_PLN_L
  ```

---

### 3. `PLA#` 讀取指令（Read）
`PLA#` 是由 SSD 輸出的狀態腳位（唯讀），依轉接卡硬體/韌體版本不同，名稱通常為 **`IOX_M2_PLA_DETECT`**（舊版或特定板子可能是 `IOX_M2_PLA_DETECT_L` 或 `IOX_M2_PLA_L`，可由步驟 1 確認，[L69](file:///C:/Users/edwin/Desktop/Workspace/sanblaze/scripts/NVMe_PLN_PLA/SBSUPPORT_10381_PLN_PLA_Power_Loss_Signaling.py#L69)、[L91-L97](file:///C:/Users/edwin/Desktop/Workspace/sanblaze/scripts/NVMe_PLN_PLA/SBSUPPORT_10381_PLN_PLA_Power_Loss_Signaling.py#L91-L97)）：

* **Read — 讀取 `PLA#` 電位**（看輸出中的 `Cur=0x0` 或 `Cur=0x1`）：
  ```bash
  sb_i2c2 -d <slot> -U -f IOX_M2_PLA_DETECT
  ```
  *(註：因為不同轉接卡的極性可能相反，腳本會先在 `PLN# = 1` 時讀一次當作 `idle` 基準值，只要讀出來的值與 `idle` 不同就代表 `PLA#` Asserted。)*

---

### 4. `Clear` 清除 `PLA#` 鎖存器（Latch）指令
因為轉接卡上的 `IOX_M2_PLA_DETECT` 帶有硬體鎖存（Latch）功能（用來捕捉極短暫的 `PLA#` 脈衝），如果想讀取**當下即時**的 `PLA#` 狀態（例如確認 `PLA#` 是否已經 Deassert 回到閒置狀態），必須先對 **`IOX_M2_CLEAR_PLA_L`** 送出一個 **`0` $\rightarrow$ `1` 的脈衝**來清除 Latch（[L115-L127](file:///C:/Users/edwin/Desktop/Workspace/sanblaze/scripts/NVMe_PLN_PLA/SBSUPPORT_10381_PLN_PLA_Power_Loss_Signaling.py#L115-L127)）：

* **Write — 清除 `PLA#` Latch（需連續下兩行，先拉低再拉高）**：
  ```bash
  sb_i2c2 -d <slot> -U -f IOX_M2_CLEAR_PLA_L -w 0
  sb_i2c2 -d <slot> -U -f IOX_M2_CLEAR_PLA_L -w 1
  ```

---

### 5. 手動測試完整順序範例（以 Slot `0` 為例）

```bash
# Step A: 確保 PLN# 釋放，並清除一次 Latch 後讀取 PLA# 初始值 (Idle)
sb_i2c2 -d 0 -U -f IOX_M2_PLN_L -w 1
sb_i2c2 -d 0 -U -f IOX_M2_CLEAR_PLA_L -w 0
sb_i2c2 -d 0 -U -f IOX_M2_CLEAR_PLA_L -w 1
sb_i2c2 -d 0 -U -f IOX_M2_PLA_DETECT

# Step B: 拉低 PLN# (Assert)，觸發斷電通知
sb_i2c2 -d 0 -U -f IOX_M2_PLN_L -w 0

# Step C: 不清除 Latch 直接讀 PLA#，確認是否有捕捉到 PLA# Assert (Processing)
sb_i2c2 -d 0 -U -f IOX_M2_PLA_DETECT

# Step D: 清除 Latch 後再讀 PLA#，確認 PLA# 是否已回到初始值 (Complete)
sb_i2c2 -d 0 -U -f IOX_M2_CLEAR_PLA_L -w 0
sb_i2c2 -d 0 -U -f IOX_M2_CLEAR_PLA_L -w 1
sb_i2c2 -d 0 -U -f IOX_M2_PLA_DETECT

# Step E: 測試完畢，釋放 PLN# (Deassert)
sb_i2c2 -d 0 -U -f IOX_M2_PLN_L -w 1
```