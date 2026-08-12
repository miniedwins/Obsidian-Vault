這是一份針對 **UNH-IOL NVMe-MI Conformance Test Plan** 中 **Test 8.5 – NVMe-MI Controller Health Status Poll** 的 Case 1 至 Case 6 的完整深度解析與規範書筆誤校正指南。本指南將以最嚴謹的工程口吻，為您逐一剖析各個測試案例（Case）的測試目標、流程、觀察結果，並**直接指出並修正 UNH-IOL 規範書中的邏輯與步驟對應錯誤**，最後為您進行總結與提供實戰開發建議。

---

### 🔍 Test 8.5 總體測試目的 (Test Purpose)

驗證待測物 (DUT) 的 **Controller Health Status Poll (控制器健康狀態輪詢)** 指令是否能正確執行。

- 確認回應的長度與管理回應中的 **RENT (Response Entries)** 欄位完全對應。
- 確認每個控制器健康資料結構 (Controller Health Data Structure, CHDS) 中的保留位元（Bytes 15:9 以及 CSTS 欄位中的 Bits 15:8）皆被正確保留並清零。

> **⚠️ 規範書總體勘誤 1**：IOL v22.0 原文目的寫到 _"bits 15:8 in bytes 322 are reserved"_，其中的 **"bytes 322" 實為 bytes 3:2 的嚴重排版筆誤**（代表 Controller Status, CSTS 暫存器欄位，佔 2 Bytes），此錯誤已於 v25.0 版本中修正為 _"bytes 3:2"_。

---

### 🛠️ Case 1 至 Case 6 逐案深度解析

#### 📌 Case 1: NVMe-MI 1.0 ECN 003 or NVMe-MI 1.0a or higher Not Implemented (M)

- **測試目標**：針對**僅支援 NVMe-MI 1.0 且未實作 ECN 003**（或未實作 1.0a 以上版本）的早期設備，驗證其保留位元清零狀態，並確認其 **RENT 欄位是以 0 為基底 (0-based)** 的舊版規範定義。
- **測試流程**：
    1. 確認 DUT 為僅支援 NVMe-MI 1.0 且未實作 ECN 003 之設備。
    2. 進行 MCTP 初始化與端點偵測 (Endpoint Discovery)。
    3. 對每個管理端點 (Management Endpoint) 發送 `Controller Health Status Poll` 指令，參數設定為：`Report All (ALL)` = 1、`Include PCI Functions` = 1、`Controller Status Changes` = 1、`MAXRENT` = 0x01，其餘欄位設為 0。
    4. 等待並解析回應訊息。
- **觀察結果**：
    1. Poll 指令必須成功執行且回應狀態為 `Success`。
    2. 確認回應中以下保留位元皆被清零：
        - DWORD 1 的 Bits 15:8
        - DWORD 2 的 Bits 31:24
        - DWORD 4 的 Bits 31:5
        - DWORD 5 的 Bits 31:0
    3. **關鍵預期結果**：若回應中包含 1 個 Controller Health Data Structure，則 **RENT 欄位（DWORD 1 的 Bits 23:16）必須為 `0h`**（即 0-based 代表有 1 個 Entry）。

---

#### 📌 Case 2: NVMe-MI 1.0 ECN 003 or NVMe-MI 1.0a or higher Implemented (M)

- **測試目標**：針對支援 **NVMe-MI ECN 003 或 NVMe-MI 1.0a（及以上）** 的新版設備，驗證保留位元清零狀態，並確認其 **RENT 欄位已修正為 1-based (非 0 為基底)** 的新版定義。
- **測試流程**：
    1. 確認 DUT 實作了 ECN 003 或支援 NVMe-MI 1.0a 以上版本。
    2. 進行 MCTP 初始化與端點偵測。
    3. 發送 `Controller Health Status Poll` 指令，參數與 Case 1 相同：`Report All` = 1、`Include PCI Functions` = 1、`Controller Status Changes` = 1、`MAXRENT` = 0x01。
    4. 等待並解析回應訊息。
- **觀察結果**：
    1. Poll 指令必須成功執行且回應狀態為 `Success`。
    2. 確認與 Case 1 相同的保留位元（DWORD 1/2/4/5 的特定位元）皆正確清零。
    3. **關鍵預期結果**：若回應中包含 1 個控制器健康資料結構，則 **RENT 欄位必須為 `1h`（非零值）**，符合新版 1-based 的條目數定義。
- **規範書筆誤校正**：
    - IOL v25.0 中，本案測試流程第 1 步寫有 _"1. T The following procedure..."_，其中 **"T" 為排版殘留的無意義字元，應予忽略並修正為 "The following procedure..."**。

---

#### 📌 Case 3: Controller Health Status Poll Filtering by Controller Selection (M)

- **測試目標**：驗證設備是否能根據 Poll 請求中的 **Controller Selection (控制器功能篩選類型)**，正確進行資料過濾。當對應類型的控制器被啟用時，才返回其資料結構。
- **測試流程**（適用於支援 ECN 003/1.0a 以上之裝置）：
    1. 進行 MCTP 初始化與端點偵測。
    2. 對每個管理端點執行以下三次健康輪詢：
        - **Poll A (篩選虛擬功能 VF)**：`ALL` = 0、`INCVF` = 1、`INCPF` = 0、`INCF` = 0、`MAXRENT` = 255、`SCTLID` = 0，錯誤選擇欄位皆為 0。等待並解析回應。
        - **Poll B (篩選實體功能 PF)**：`ALL` = 0、`INCVF` = 0、`INCPF` = 1、`INCF` = 0、`MAXRENT` = 255、`SCTLID` = 0，錯誤選擇欄位皆為 0。等待並解析回應。
        - **Poll C (篩選一般控制器 F)**：`ALL` = 0、`INCVF` = 0、`INCPF` = 0、`INCF` = 1、`MAXRENT` = 255、`SCTLID` = 0，錯誤選擇欄位皆為 0。等待並解析回應。
- **觀察結果**：
    1. 驗證每次 Poll 回應，**僅包含與篩選條件完全相符** 的控制器健康資料結構（例如：Poll A 僅能返回虛擬功能控制器的資料，其餘皆被過濾排除）。
    2. 每一次過濾輪詢的回應狀態皆為 `Success`，且 RENT 欄位正確顯示 1-based 的回傳個數。

---

#### 📌 Case 4: Controller Health Status Poll Filtering by Error Selection Fields (M)

- **測試目標**：驗證當 `ALL` = 0 時，設備是否能根據請求中的 **Error Selection (健康狀態與錯誤篩選欄位)**（CWARN、SPARE、PDLU、CTEMP），正確過濾出有對應狀態變更的控制器。
- **測試流程**：
    1. 進行 MCTP 初始化與端點偵測。
    2. 對每個管理端點發送四次輪詢，其中 `ALL` = 0、`MAXRENT` = 255、`SCTLID` = 0：
        - **Poll A**：僅設定 `CWARN` = 1，其餘為 0。
        - **Poll B**：僅設定 `SPARE` = 1，其餘為 0。
        - **Poll C**：僅設定 `PDLU` = 1，其餘為 0。
        - **Poll D**：僅設定 `CTEMP` = 1，其餘為 0。
- **觀察結果**：
    1. 確保每次 Poll 的回應狀態皆為 `Success`。
    2. **關鍵驗證**：每一次 Poll 的回應資料中，**僅包含健康狀態發生了對應變更** 且觸發 Changed Flags 的控制器。
- **⚠️ 規範書邏輯與測試漏洞修正 (重要)**：
    - **IOL 原文嚴重錯誤**：IOL 規範書在 Case 4 的 Procedure 步驟中，將這四次 Poll 的參數皆寫為 `INCVF=0, INCPF=0, INCF=0`。
    - **修正解析**：根據 NVMe-MI 第 5.3.1 節定義，**如果 `INCVF`、`INCPF`、`INCF` 三者皆為 0，則所有控制器都會被排除在回應之外 (Excluded)**。如此一來，不論健康狀態是否有變更，裝置皆會返回空的回應（RENT=0），導致無法實際測試 Error Selection 的過濾功能。
    - **正確修正**：開發或測試工程師在實作測試腳本時，**必須至少將其中一個 Controller Selection 欄位設為 1**（例如，針對一般的 Physical Function 設備，設定 `INCPF=1`），否則本測試案將直接因邏輯錯誤而失效或 Fail。

---

#### 📌 Case 5: Controller Health Status Poll Data Verification (FYI)

- **測試目標**：進行控制器健康資料結構 (CHDS) 中關鍵健康位元（如 NAC、FA、TCIDA）的資料精確度驗證，並確認 **Clear Changed Flags (CCF, 清除變更旗標)** 欄位能確實將狀態旗標清零。
- **測試流程**：
    1. 進行 MCTP 初始化，讀取 `DTYP` = 0x00 確定 NNSC 狀態（若不支援或為新版且不符合 SRE 規範則略過此案）。
    2. **第一步輪詢 (CCF = 1)**：發送 `ALL` = 0、`MAXRENT` = 254、`SCTLID` = 0，且將 **`Clear Changed Flags (CCF)` 設為 1** 的 Poll 指令。記錄此時返回的 CHDS 資料。
    3. **第二步輪詢 (CCF = 0)**：發送完全相同參數之 Poll 指令，但 **`CCF` 設為 0**。
    4. **第三步輪詢 (全選 + CCF = 1)**：發送 `ALL` = 0、`MAXRENT` = 254、`SCTLID` = 0，且將 `CCF`、`CWARN`、`SPARE`、`PDLU`、`CTEMP`、`CSTS` 皆設為 1 的 Poll 指令。
- **觀察結果**：
    1. 驗證第一次 Poll 返回的控制器資料中，`NAC`、`FA` 與 `TCIDA` 欄位皆已正確初始化且為 0。
    2. 在執行過 `CCF=1`（清除旗標）之後，第二次 Poll (CCF=0) 返回的資料結構應與前次相符（清零後無新增變化，故不應有額外觸發）。
    3. 回報的控制器數量最多不能超過 255 個，且其 **Controller ID 必須按升冪 (ascending order) 排列**。
- **⚠️ 規範書步驟對應錯誤修正**：
    - **IOL 原文錯誤**：在 Observable Results 中，原文寫到 _"Verify the returned data structure from **step 2** contains NAC..."_，並且寫到 _"Verify the returned data structure from **step 3** is identical to the data structure returned in **step 2**."_
    - **修正解析**：在 Procedure 中，**Step 2 其實是發送 `Read NVMe-MI Data Structure`**，此指令回傳的資料結構**根本不含**這些健康狀態欄位。真正的健康狀態是在 **Step 3（第一步輪詢）** 中返回的。
    - **正確修正**：
        - Result 1 所指的 step 2 **應修正為 step 3**（第一步輪詢所得 CHDS）。
        - Result 2 中所稱的 step 3 與 step 2 對比，**應修正為「確認 step 4（第二步 Poll）與 step 3（第一步 Poll）的基礎狀態資料一致」**。

---

#### 📌 Case 6: Controller Health Data Structure Matches SMART/Health Log Page (FYI)

- **測試目標**：驗證 out-of-band（帶外，透過 NVMe-MI）輪詢取得的健康資訊，與待測物內部 in-band（帶內）執行 NVMe Admin 指令取得的 **`SMART/Health Information Log Page`（LID 02h）之 Critical Warning（臨界警報）位元完全一致**。
- **測試流程**：
    1. 進行 MCTP 初始化並檢測端點。
    2. **Poll 1 (ALL = 1)**：發送 `ALL` = 1、`MAXRENT` = 254、`SCTLID` = 0、`CCF` = 0 的 Poll，記錄回傳的 CHDS 健康資訊。
    3. 發送 `Configuration Get` 讀取 `Health Status Change (02h)` 以獲取當前組態。
    4. **Poll 2 (CCF = 1)**：發送 `ALL` = 0、`MAXRENT` = 254、`SCTLID` = 0、`CCF` = 1 的 Poll 以清除旗標並記錄資料。
    5. 透過帶內 Admin Queue 發送 `Get Log Page (LID 02h)`，記錄其 `Critical Warning` 欄位值。
- **觀察結果**：
    1. 驗證在第二步 Poll (CCF=1) 中，前次 Poll (step 3) 中曾被設為 1 的 `TCIDA`、`FA`、`NAC`、`CECO`、`NSSRO` 欄位在清除後已變為 0。
    2. **關鍵對照**：從 in-band 取得的 `Critical Warning` 欄位數值，必須與 out-of-band CHDS 中的 `Critical Warning` 欄位（Byte 8）**二進制數值完全相同**。
- **⚠️ 規範書步驟對應錯誤修正**：
    - **IOL 原文錯誤**：Observable Result 1 原文寫到 _"cleared to 0 in the second Controller Health Status Poll command in **step 4**"_。
    - **修正解析**：在 Procedure 中，**Step 4 其實是發送 `Configuration Get` 指令**，真正的第二步 Poll 是在 **Step 5** 才發送。
    - **正確修正**：此處的 "step 4" **應校正為 "step 5"**。

---

### 📋 關鍵測試規範錯誤與修正總結 (Summary of Corrections)

|勘誤位置|IOL 規範書原文錯誤|正確修正與工程解析|
|:--|:--|:--|
|**Test 8.5 目的描述**|bit 15:8 in **bytes 322** are reserved|修正為 **bytes 3:2**（即 2 空間位元組的 Controller Status CSTS 欄位）。|
|**Case 2 第一步**|**T** The following procedure...|清除多餘無意義的排版字元 "T"。|
|**Case 4 篩選機制**|測試參數設為 **INCVF=0, INCPF=0, INCF=0**|**嚴重邏輯漏洞。** 三者皆為 0 會將所有控制器排除，導致無法驗證 Error Selection。工程師在撰寫腳本時，**必須將對應控制器類型（如 INCPF）設為 1**。|
|**Case 5 觀察結果 1**|Verify returned data structure from **step 2** contains...|**步驟對應錯誤。** Step 2 為唯讀資訊 DTYP 00h，**應修正為 step 3（第一步健康輪詢）**。|
|**Case 5 觀察結果 2**|Verify step 3 is identical to **step 2**|**步驟對應錯誤。** 應修正為對比第二次健康輪詢與第一次 Poll 的基礎狀態（即對比 **step 4 與 step 3**）。|
|**Case 6 觀察結果 1**|...cleared to 0 in the Poll command in **step 4**|**步驟對應錯誤。** Step 4 實為 Config Get 指令，**應修正為 step 5（第二步健康輪詢）**。|

---

### 💡 給測試與開發工程師的實戰建議

在撰寫與偵錯自動化 Conformance 測試腳本時，請特別注意：

1. **避開 Case 4 的零控制器回應陷阱**：許多商用測試儀器（如 Teledyne-LeCroy）若直接依照 UNH-IOL 規範書原文編寫，會因為 `INCVF=0/INCPF=0/INCF=0` 而一直回傳空的健康結構，進而判定測試失敗。請務必手動在腳本中將 Controller Selection type 改成能與您 SSD 控制器匹配的設定。
2. **確保 1-based RENT 位元計算**：若您的韌體是基於較新的 NVMe-MI 1.1d/1.2d 或 2.0 以上規格開發，請確保 `RENT` 在回傳 1 個健康結構時填入 `1h`（非零值，即 Case 2）；若您是在維護舊版相容代碼，則需根據版本切換為 0-based（Case 1）。

---


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