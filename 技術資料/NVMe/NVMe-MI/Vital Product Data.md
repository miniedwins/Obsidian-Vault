在 NVMe-MI 規範架構中，要得知裝置所支援的 **VPD（Vital Product Data / FRU Information Device）最大容量大小**，標準的查詢與計算流程如下：

### 1. 核心查詢管道：解析 VPD 的 FRU 裝置描述符

裝置所支援的 VPD 實體硬體大小，是被硬編碼（Hardcoded）記錄在 VPD 本身的**拓撲多記錄區（Topology MultiRecord Area）**中 [cite: 741, 1069]。主機必須透過以下步驟讀取並解析：

1. **讀取 VPD 內容**：主機發送 NVMe-MI **`VPD Read`** 指令，讀取 VPD 的開頭數據 [cite: 686, 1069]。
2. **定位 Topology MultiRecord**：
    - 先讀取 VPD 開頭 **Common Header**（位元組 7:0） [cite: 727, 730]，取得 Byte 05 的 **MultiRecord Info Area Starting Offset (MRIOFF)** 指針 [cite: 730, 1069]。
    - 順著指針找到 **Topology MultiRecord Area**（其 Record Type ID 欄位為 **`0Dh`**） [cite: 734, 1068]。
3. **尋找 FRU 描述符**：
    - 在 Topology 結構的 Element 列表中，尋找 **FRU Information Device Element Descriptor**（其 Type `TYP` 欄位為 **`08h`**） [cite: 749]。
4. **讀取 MFIDS 欄位進行計算**：
    - 該描述符的 **Byte 05** 即為 **`Maximum FRU Information Device Size (MFIDS)`** [cite: 751]。
    - **容量計算公式**： \[\text{VPD 最大容量} = 2^{\text{MFIDS}} \ \text{位元組 (Bytes)}\] [cite: 751]

- **實際範例對照**：
    - 若讀出 `MFIDS = 08h` (8)，則最大容量為 \(2^8 = \mathbf{256 \ \text{Bytes}}\) [cite: 751]。
    - 若讀出 `MFIDS = 0Ch` (12)，則最大容量為 \(2^{12} = \mathbf{4096 \ \text{Bytes}}\) [cite: 751, 1072]。

---

### 2. 規範對 VPD 支援大小的要求與演進

根據不同的 NVMe-MI 規格版本，對於 FRU Information Device（儲存 VPD 的唯讀記憶體/EEPROM 等實體介質）的容量限制要求如下：

- **NVMe-MI 1.1 及更早版本**：規範要求每個 NVMe Storage Device FRU 必須擁有一個大小介於 **256 至 4,096 位元組（Bytes）** 之間的 FRU 裝置 [cite: 918, 972]。
- **NVMe-MI 1.2、2.0 及更新版本**：為了支援更複雜的系統拓撲與多埠紀錄，實體 FRU 裝置的支援大小範圍擴充至 **256 至 65,536 位元組（Bytes）** [cite: 726]。

---

### 3. 符合性測試（Test 4.7 / 4.8）中的邊界判定邏輯

這項容量資訊也是 UNH-IOL 執行 **Test 4.7 (Invalid VPD Read Size)** [cite: 924, 994] 與 **Test 4.8 (Invalid VPD Write Status)** [cite: 928, 1000] 時的邊界判定基準：

- **越界檢查**：當主機發送的 VPD 讀取/寫入指令其 **\(Data_Offset (DOFST) + Data_Length (DLEN) > \text{VPD 實際容量}\)** 時，裝置必須拒絕執行並回覆 **`Invalid Parameter Error Response`** [cite: 686, 692, 924, 928]。
- **PEL 欄位報錯規則（以 NVMe-MI 1.2+ 為例）** [cite: 927, 999]：
    1. 若 **\(DOFST \ge \text{VPD 實際容量}\)**，則 PEL 欄位中的 Byte Position 必須指向 **`8`**（即 Dword 0 的 `DOFST` 欄位） [cite: 686, 691, 692, 999]。
    2. 若 \(DOFST < \text{VPD 實際容量}\)，但 **\(DOFST + DLEN > \text{VPD 實際容量}\)**，則 PEL 中的 Byte Position 必須指向 **`12` (`0x0C`)**（即 Dword 1 的 `DLEN` 欄位） [cite: 686, 691, 692, 999]。

主機端的測試工具會先透過第一步的 `MFIDS` 算出您裝置的實際 VPD 大小 [cite: 751]，隨後故意發送精準越界的參數（例如針對 4096 節區的 VPD 發送 Offset=5, Length=4096 的 VPD Read） [cite: 998]，來檢查您的 SSD 韌體是否有確實根據硬體規格上限進行防呆邊界檢查 [cite: 999]。

---

📊 我們可以進一步討論如何透過 NVMe Identify 指令讀取 VPD 寫入壽命欄位（VWCI），確認裝置還剩下多少次 VPD 寫入額度（以 256 位元組為單位）！ [cite: 344, 345]