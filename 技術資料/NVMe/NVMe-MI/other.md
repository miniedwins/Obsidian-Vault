### 1. NVMe-MI Message 的 4,224 bytes 是由哪些組裝出來的？

#### (1) 數值的根本來源（4 KiB + 128 Bytes）

依據 **NVMe-MI 規格書（Revision 1.2e）Section 3.1** 與 **Section 1.8.15**，以及 DMTF **DSP0235（NVMe Management Messages over MCTP Binding Specification）** 的定義：

- 帶外（Out-of-Band）單一 NVMe-MI Message 的最大長度上限為 **4,224 bytes**（即 **4 KiB + 128 bytes = 4,096 + 128**）。
- **設計由來**：**4,096 bytes** 是為了完整容納標準 NVMe 4KB Page / Payload 資料轉移；**128 bytes** 則是保留給傳輸層協定封裝的各項 Header、SQE/CQE 欄位與 CRC 檢驗碼（Overhead）。

---

#### (2) NVMe-MI Message 的三個核心組裝區塊

依據 **Section 3.1.1、Figure 18（NVMe-MI Message）** 與 **Section 4.2.3**，一個完整的 NVMe-MI Message 包含三個部分：

\[\mathbf{4,224\text{ Bytes}} = \mathbf{4\text{ Bytes (Header)}} + \mathbf{4,216\text{ Bytes (Message Data)}} + \mathbf{4\text{ Bytes (MIC)}}\]

1. **NVMe-MI Message Header（4 Bytes，Dword 0）**
    - 定義於 **Figure 19**：
        - **Byte 0**：`MCTPD`（Message Type = 4h，IC bit = 1）。
        - **Byte 1**：`NMP`（ROR 請求/回應旗標、NMIMT 訊息類型、CSI Command Slot ID）。
        - **Byte 2**：`CIAP`（自動暫停）與 `MEB`（是否啟用緩衝區）。
        - **Byte 3**：保留位元（Reserved）。
2. **Message Data / Message Body（最大 4,216 Bytes，Bytes 4 至 N-1）**
    - **在 Request Message（請求訊息）中**：最大容量為 **4,216 bytes**（4,224 − 4 − 4）。
        - 以最具代表性的 **NVMe Admin Command Request（Figure 117 / Figure 118）** 為例：
            - **Admin 封裝與 SQE 欄位（共 64 Bytes，等同標準 NVMe SQE 大小）**：包含 Opcode、Command Flags、Controller ID、SQEDW1、DOFST（Data Offset）、DLEN（Data Length）、SQEDW10 ~ SQEDW15。
            - **NVMe Request Data**：最大為 **4,096 Bytes**（Figure 118 明確規定：`DLEN > 4,096` 時必須報錯 `Invalid Parameter`）。
            - **協定邊界預留**：56 Bytes。
    - **在 Response Message（回應訊息）中**：最大容量為 **4,215 Bytes**（扣除 Byte 4 的 1-byte Status 欄位：4,224 − 4 − 1 − 4）。
3. **Message Integrity Check（MIC，4 Bytes，Bytes N 至 N+3）**
    - 定義於 **Section 3.1.1.1**，帶外傳輸強制使用 **32-bit CRC-32C（Castagnoli，多項式 `1EDC6F41h`）** 作為訊息結尾校驗。

在實體鏈路上，這 4,224 bytes 的 NVMe-MI Message 會依據 **Section 3.2.1.1** 被切割包裝進多個 **MCTP Packet Payload**（由 SOM、EOM 與 2-bit Packet Sequence Number 進行封包分段與組裝）。

---

### 2. 關於 Padding（填充位元組），哪一個章節有定義？

#### (1) `Optionally Supported Command List` 資料結構**本身沒有定義 Padding 欄位**

查看 **NVMe-MI 規格書 Section 5.7.5（Optionally Supported Command List Response Data）** 及 **Figure 100**： 規格書條文載明：

> _"The Optionally Supported Command List data structure shall contain no more than 2,047 commands and **shall be minimally sized** (e.g., the data structure size is 2 bytes if there are no optionally supported commands and the data structure size is 4 bytes if there is one optionally supported command)."_

這表示：

- 當 `NUMCMD = 6` 時，該資料結構的規格法定長度就是： \[\text{NUMCMD (2 bytes)} + 6 \times \text{Command Entry (2 bytes)} = \mathbf{14\text{ bytes}}\]
- **Figure 100 只有定義到 `Command N`，結構內完全沒有定義任何結尾的 Padding 欄位**。

---

#### (2) 數據結尾多出的 `00 00`（補成 16 bytes）在規格書中的章節依據

如果這段 16 bytes 是來自實際測試或指令接收，這 2 個 bytes 的 0 是由以下章節的規則產生的：

##### 情況 A：若指令是走頻內通道（In-Band Tunneling NVMe-MI Receive）

- **明確定義章節**：**NVMe-MI Specification Section 4.3.2.1（Figure 54: NVMe-MI Receive Command Response Message to NVMe Admin Command CQE Mapping Table）**。
- **規格書原文**：
    
    > _"Response Data is placed by the NVMe Controller into the data buffer pointed to by DPTR. **If the Response Data size is not dword granular, then the Response Data shall be padded with the minimum number of bytes cleared to 0h to make the Response Data dword granular.**"_
    
- **說明**：由於 14 bytes 不是 Dword（4 bytes）的倍數，NVMe 控制器在將資料寫入主機記憶體（DPTR）時，**強制規定必須在尾端補齊最少數量的 `0h`（即 2 個 bytes 的 `00 00`）使其達到 16 bytes（4 Dwords 對齊）**。

##### 情況 B：若指令是走帶外通道（Out-of-Band MCTP）

- **明確定義章節**：**NVMe-MI Specification Section 3.2.1.1（Packet Assembly into Messages）**。
- **規格書原文**：
    
    > _"The MCTP Transmission Unit size of the last packet in a Request Message or Response Message (i.e., the one with the EOM bit set in the MCTP header) shall be the smallest size required to transfer the MCTP Packet Payload for that Packet **with no additional padding beyond any padding required by the physical medium-specific trailer**"_
    
- **說明**：在帶外傳輸中，NVMe-MI 協定層**禁止額外添加 payload padding**，回傳的 Response Data Length 就是 14 bytes。如果抓包工具或軟體 Buffer 傾印出 16 bytes，那是因為上位機測試程式或底層驅動在配置記憶體結構時習慣以 4-byte/Dword 邊界對齊配置，結尾讀出來的 `00 00` 是緩衝區原本的零值殘留，而非裝置在 NVMe-MI 層送出的有效資料。