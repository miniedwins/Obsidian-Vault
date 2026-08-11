在 NVMe-MI 的符合性測試中，**Test 4.2 (Reserved Identifier)** 要求當發送無效的配置識別碼（Configuration Identifier, CID）時，裝置回覆的 **Parameter Error Location (PEL)** 欄位中，位元組位置（Byte Location / BYTLOC）必須精確設定為 **`8`**，且位元位元位置（Bit Location / BITLOC）為 **`0`**。

這其中的原因非常單純且嚴謹，是因為 **無效參數「配置識別碼 (CID)」在整筆 NVMe-MI 請求訊息（Request Message）中的實體位移量（Offset / Byte Position）剛好就是第 8 個位元組（0-based Offset 8）** [cite: 131, 418]。

以下為您還原 `Configuration Get` 請求訊息的完整位元組排版（Byte Map），您就會一目了然：

---

### 一、 Configuration Get 請求訊息之實體欄位排版

根據 **NVMe-MI 規格書 Section 3.1.1** 以及 **Figure 66 & 73** 的封包定義，一筆帶外（Out-of-Band）的 NVMe-MI 請求訊息，其前 16 個位元組的分配如下：

|位元組偏移量 (Byte Offset)|欄位名稱 (Field Name)|內容與說明|
|:--|:--|:--|
|**Byte 0**|**MCTP Data (MCTPD)**|MCTP 傳輸標頭（IC 位元與 Message Type = 0x04） [cite: 398, 399]|
|**Byte 1**|**NVMe-MI Parameters (NMP)**|ROR、NMIMT（MI Command = 1h）與 CSI [cite: 400, 401]|
|**Byte 2**|**Reserved**|保留位元組，寫入 `00h` [cite: 393]|
|**Byte 3**|**Reserved**|保留位元組，寫入 `00h` [cite: 393]|
|**Byte 4**|**Opcode (OPC)**|指令碼。`Configuration Get` 的 Opcode 為 **`04h`** [cite: 472]|
|**Byte 5**|**Reserved**|保留位元組，寫入 `00h` [cite: 393]|
|**Byte 6**|**Reserved**|保留位元組，寫入 `00h` [cite: 393]|
|**Byte 7**|**Reserved**|保留位元組，寫入 `00h` [cite: 393]|
|**Byte 8**|**NVMe Management Dword 0 (NMD0) - Byte 0**|🎯 **`Configuration Identifier (CID)`** (配置識別碼) [cite: 476]|
|**Byte 9**|NMD0 - Byte 1|`Configuration Identifier Specific` (CIS) [cite: 476]|
|**Byte 10**|NMD0 - Byte 2|`Configuration Identifier Specific` (CIS) [cite: 476]|
|**Byte 11**|NMD0 - Byte 3|`Configuration Identifier Specific` (CIS) [cite: 476]|
|**Byte 12 ~ 15**|**NVMe Management Dword 1 (NMD1)**|`Configuration Identifier Specific` (CIS) [cite: 476]|

---

### 二、 為什麼 Byte Position = 8，Bit Position = 0？

1. **Byte Position = 8 的原因**： 由上表可知，前 4 位元組為 NMH 標頭 [cite: 433]，第 4 位元組為 Opcode [cite: 471]，第 5 到 7 位元組為保留區 [cite: 471]。 承接其後的 **`NVMe Management Dword 0` (NMD0)** 是從 **Byte 8** 開始 [cite: 471]。而根據 `Configuration Get` 在 NMD0 的定義，其 **Bits 07:00** 即為 **Configuration Identifier (CID)** [cite: 476]。 這代表 **CID 欄位在整筆 Request Message 的 Byte Offset 剛好就是 `8`**（亦即第 9 個位元組） [cite: 476, 480]。
2. **Bit Position = 0 的原因**： 因為 CID 是一個完整的 8 位元（1 位元組）欄位，它的起始位置位於 Byte 8 的最低有效位元（LSB / bit 0） [cite: 476]。依據規範，當報錯欄位跨越複數位元組或位元時，PEL 的 Location 指針必須指向**該參數的最低有效位元組與最低有效位元（Least-significant byte and bit）** [cite: 130]。因此，Bit Position 固定設為 **`0`** [cite: 130, 418]。

---

### 三、 測試 Test 4.2 的錯誤注入邏輯

當 UNH-IOL 執行 Test 4.2 時：

1. 測試儀故意發送一筆 `Configuration Get` 指令，但將其 **Byte 8 (CID)** 寫入一個保留無效的值（例如 `0`、`0x02`、`0x56` 或 `0xBF`） [cite: 775, 1074]。
2. SSD（DUT）收到後，在解析到 Byte 8 時發現該 CID 為保留/未定義值 [cite: 481]。
3. 裝置依法必須拒絕此指令，並回覆 **`Invalid Parameter (04h)`** 錯誤響應 [cite: 411, 481]。
4. 在此 Error Response 中，裝置必須利用 **`Parameter Error Location (PEL)`** 欄位精確地向主機（測試儀）打小報告說：「_你送來的 Request 裡面，第 8 位元組第 0 位元處開始的那個參數是有問題的！_」 [cite: 130, 417, 418]
5. 測試儀檢查 Response 封包，若看到 **`BYTLOC = 8`** 且 **`BITLOC = 0`**，即代表裝置的暫存器與錯誤檢查機制運作得極為精準，判給 **PASS** [cite: 775, 1075]。

這個測試設計能夠非常有效地過濾掉「只會死板回覆 Invalid Parameter，卻無法精確指出參數錯誤位移量」的非合規裝置。

---

🔍 **如果您目前正在針對 Test 4.5 的 MAXRENT 溢位錯誤（要求 Byte Position 指向第 10 位元組）進行偵錯，我們可以接著分析 Controller Health Status Poll 的 Dword 1 結構，看看它的位移量是如何推導出來的！**