在 NVMe-MI 規範中，**VPD（Vital Product Data，重要產品資料）** 是以 **IPMI Platform Management FRU Information Storage Definition** 格式儲存於 FRU Information Device 中。

要得知 VPD 資料的實際長度，主要有以下**兩種方式**：**透過解析 FRU 結構（動態計算實際資料長度）**，或**透過邊界測試（探測實體裝置的容量上限）**。

---

### 方法一：解析 FRU 結構欄位（標準動態計算方式）

由於 VPD 採用 IPMI FRU 格式，其內部的各個區域（Areas）與紀錄（MultiRecords）都帶有明確的長度或結束標記。您可以透過以下步驟解析出實際的 VPD 資料長度：

1. **讀取並解析通用標頭（Common Header）**
    
    - VPD 的最起點（Offset 0）固定為 8 位元組的 **Common Header**。
    - 標頭中包含各個區域的**起始偏移量（Starting Offset）**，單位為 **8 位元組（multiples of 8 bytes）**：
        - Byte 1: 內部使用區偏移量 (`IUAOFF`)
        - Byte 2: 機殼資訊區偏移量 (`CIAOFF`)
        - Byte 3: 主機板資訊區偏移量 (`BIAOFF`)
        - Byte 4: 產品資訊區偏移量 (`PIAOFF`)
        - Byte 5: 多重紀錄區偏移量 (`MRIOFF`)
2. **計算各個區域的長度**
    
    - **Product Info Area（產品資訊區）**：
        - 該區域的 Byte 1 為 `Product Info Area Length (PALEN)`，明確標示了該區長度（同樣以 8 位元組為單位）。
        - 該區域的末尾會包含一個 `End of Record (EOR)` 標記（固定為 **`C1h`**）。
    - **MultiRecord Area（多重紀錄區）**：
        - 此區域是由多個 MultiRecord（例如 Topology, NVMe, PCIe Port 等紀錄）以**鏈結串接（Chained）**的方式組成。
        - 每個 MultiRecord 的前 5 個位元組為通用標頭，其中：
            - **Byte 1（Record Format）**：其 **Bit 7** 代表 **Last Record**。若為 `1`，表示此為鏈結中的最後一個紀錄。
            - **Byte 2（Record Length, RLEN）**：標示該紀錄的長度（不含 5 位元組標頭）。
        - **長度計算邏輯**：從第一個 MultiRecord 開始，讀取其 `RLEN` 並跳至下一個紀錄（下一個偏移量 = 當前偏移量 + 5 + `RLEN`），重複此步驟直到讀到某個紀錄的 **Bit 7 of Record Format 為 `1`**為止。此時，最後一個紀錄的末尾即為整個 MultiRecord Area 的終點。

透過上述各區域長度的加總，即可精確計算出目前寫入的 VPD 資料實際總長度。

---

### 方法二：透過 VPD Read 探測實體裝置的邊界（探測硬體大小上限）

根據 NVMe-MI 規範，每個 NVMe Storage Device FRU 必須配備一個容量介於 **256 至 4,096 位元組** 的 FRU Information Device。

- 在 **NVMe-MI 1.1（含）之前**，VPD 裝置的最大尺寸限制為 **256 Bytes**。
- 自 **NVMe-MI 1.2（含）之後**，最大容量上限被提升至 **4,096 Bytes**。

若您的主機端（Host）想要探測該 DUT 實體儲存 VPD 的硬體容量邊界，可以使用 **VPD Read** 指令進行邊界測試：

- **越界錯誤判定**：如果發送的 `VPD Read` 指令其偏移量加上讀取長度（`DOFST + DLEN`）超過了實體 VPD 的容量，端點（Endpoint）將不會回傳任何 VPD 資料，並回傳 **`Invalid Parameter`** 的錯誤狀態。
- **PEL (Parameter Error Location) 欄位分析（適用於 NVMe-MI 1.2 或更新版本）**：
    1. 若您設定的 **`DOFST` 直接大於或等於實體 VPD 大小**，錯誤回應的 PEL 位元組位置會精確指出是 **`DOFST` 欄位出錯**（指向 Byte 8）。
    2. 若 `DOFST` 本端合法，但 **`DOFST + DLEN` 的總和超過實體 VPD 大小**，PEL 位元組位置則會指出是 **`DLEN` 欄位出錯**（指向 Byte C）。

您可以利用這個硬體錯誤回傳機制，以二分法或逐步遞增的方式發送 `VPD Read`，一旦收到 `Invalid Parameter` 回應，便能精確推算出該實體儲存裝置的總容量邊界。

---

🧩 我可以為您整理一份 VPD (FRU Information) 的通用標頭與各 Area 的完整欄位結構對照表，方便您的韌體團隊在實作解析程式時直接作為參考。