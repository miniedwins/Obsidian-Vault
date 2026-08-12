Case 1: NVMe-MI 1.0 ECN 003 or NVMe-MI 1.0a or higher Not Implemented (M)

這四項驗證規則是 UNH-IOL 測試規範（在 Test 8.5 Case 1 & 2）中，針對 **Controller Health Status Poll** 命令回傳之 Response 封包進行的**「保留位元（Reserved Bits）清零」**安全檢查。

這也是韌體工程師在過 Conformance 測試時最常漏掉的細節。以下為您逐一拆解這 4 個 Dword 區務的位元，對照 NVMe-MI 規格書的真實欄位：

---

### i. Bits 15:8 in DWORD 1 為什麼是 Reserved？

- **對應封包位置**：整個 Response 封包的 **Byte 5**。
- **欄位原委**：
    - **DWORD 1**（Bytes 7:4）包含了 1 個 Byte 的 `STATUS`（Byte 4）與 3 個 Bytes 的 `NMRESP`（Bytes 7:5）。
    - 根據 NVMe-MI 規格書（Figure 80），`NMRESP` 欄位中，Bits 15:00 是 **Reserved (保留位元)**，只有高位元的 Bits 23:16 被用作 `RENT`（Response Entries，即 CHDS 數量）。
    - 因此，`NMRESP` 的 LSB（即封包的 Byte 5，對應到 DWORD 1 的 **Bits 15:8**）在規範中屬於保留位元，必須清零。

---

### ii. Bits 31:24 in DWORD 2 為什麼是 Reserved？

- **對應封包位置**：第一筆 Controller Health Data Structure (CHDS) 的 **Byte 3**（即整個封包的 Byte 11）。
- **欄位原委**：
    - **DWORD 2**（Bytes 11:8）對應 CHDS 的前 4 個 Bytes（Bytes 3:0）。
    - 其中 **Bytes 1:0** 是 `CTLID`（Controller ID），**Bytes 3:2** 是 `CSTS`（Controller Status）。
    - 根據規格書定義（Figure 81），**`CSTS` 的 Bits 15:08 是 Reserved（保留）**，Bits 07:00 才是狀態旗標（如 FA, NAC, CECO, NSSRO, SHST, CFS, RDY 等）。
    - 因為 `CSTS` 佔用 DWORD 2 的高半部（Bits 31:16），其高位元組（CSTS Bits 15:08）正好對應到 **DWORD 2 的 Bits 31:24**。所以這 8 個 bits 必須清零。

---

### iii. Bits 31:5 in DWORD 4 為什麼是 Reserved？

這是一個非常精彩的**版本演進歷史細節**（也是最容易讓工程師困惑的地方）：

- **對應封包位置**：CHDS 的 **Bytes 11:9** 以及 **Byte 8** 的高位元（即整個封包的 Bytes 19:16）。
- **欄位原委**：
    - **DWORD 4** 對應 CHDS 的 Bytes 11:8。
    - 根據規格書，**CHDS Bytes 11:9 全都是 Reserved（保留）**，對應到 DWORD 4 的 **Bits 31:8**。
    - **CHDS Byte 8** 是 `Critical Warning`（CWARN，對應 DWORD 4 的 Bits 7:0）。
    - 在後來的 NVMe-MI 版本中，CWARN Byte 8 的位元定義為：Bit 5 是 PMRE（PMR Error）、Bit 4 是 VMBF、Bit 3 是 RO、Bit 2 是 RD、Bit 1 是 TAUT、Bit 0 是 ST。
    - **但在早期 NVMe-MI 1.0 時代**，PMRE（Bit 5）尚未存在，所以 **CWARN Bits 7:5 全都是 Reserved**。
    - 因此，在測試不支援 ECN 003 的 1.0 設備時（Case 1），整個 DWORD 4 中，除了有用的 CWARN 旗標（Bits 4:0）以外，其餘的 **Bits 31:5（包含保留的 Bytes 11:9 與 CWARN Bits 7:5）全部都視為 Reserved 並必須清零**！

---

### iv. Bits 31:0 in DWORD 5 為什麼是 Reserved？

- **對應封包位置**：CHDS 的 **Bytes 15:12**（即整個封包的 Bytes 23:20）。
- **欄位原委**：
    - 根據 CHDS 格式定義（Figure 81 / Figure 83），**CHDS 的 Bytes 15:9 全部都是 Reserved（保留）**。
    - 由於 DWORD 5 正好完全裝載 CHDS 的最後 4 個 Bytes（Bytes 15:12），這代表**整個 DWORD 5 完全沒有任何有效的資料欄位**，必須 100% 清零。

---

### 💡 給測試與開發工程師的總結

UNH-IOL 的測試腳本在抓取到 `Controller Health Status Poll Response` 後，會對封包進行嚴格的 bit-mask 檢查。若您的韌體沒有將這些 Reserved 欄位填入 `0`，就會在測試 Log 中直接吐出 `FAIL`。

在編寫回傳結構體時，最安全的方式是**在填充資料前，先對整個傳送 Buffer 進行 `memset(buf, 0, sizeof(buf))` 清零**，然後僅針對有定義的 bits 進行 `|=` 賦值，這樣就能輕鬆規避這些因規格書版本更迭產生的 Reserved 欄位檢查失敗。

📊 如果您需要，我可以為您提供一份符合這些 Reserved 規則的 C 語言 CHDS 結構體 (Struct) 與 bit-mask 定義，幫助您直接在韌體中精確避坑。