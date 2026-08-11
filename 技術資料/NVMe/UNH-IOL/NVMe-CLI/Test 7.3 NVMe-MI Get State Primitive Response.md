
#### **Case 1: Get State Control Primitive 請求與清除機制驗證**

- **測試目標**： 驗證 Get State Control Primitive 請求在不同 **Clear Error State Flags (CESF)** 設定值（1 與 0）下的交互驗證，並確認 Management Endpoint State (MES) 的錯誤清除機制是否正確運作。
- **測試流程**：
    1. 執行 MCTP 初始化。
    2. 發送 **Get Endpoint ID** 控制訊息以獲取端點 ID。
    3. 發送 **Get State Control Primitive** 請求，並將 **CESF (Clear Error State Flags) 位元設為 1**，記錄回傳的 MES 狀態。
    4. 再次發送 **Get State Control Primitive** 請求，並將 **CESF 位元設為 0**，記錄並比對回傳的 MES 狀態。
- **預期觀測結果**：
    1. 步驟 3 與步驟 4 的 Get State 請求皆應成功完成。
    2. 在步驟 3 (CESF = 1) 執行後，MES 中的 Error State Flags (Bits 14:03) 應被**原子性 (Atomically) 清除為 0h**。
    3. 步驟 4 (CESF = 0) 回傳的 MES 暫存器中，**Bits 14:03 應保持為 0h**，且不應被修改。

---

#### **Case 2: NVM Subsystem Reset 後清除 Management Endpoint State 暫存器位元**

- **測試目標**： 驗證當發生 **NVM Subsystem Reset** 時，Management Endpoint State (MES) 暫存器中除了 **Bit 14 (NSSRO - NVM Subsystem Reset Occurred) 被設為 1** 以外，其餘位元皆會被清除為 0。
- **測試流程**：
    1. 執行 MCTP 初始化。
    2. 發送 **Read NVMe-MI Data Structure** 指令（將 **DTYP 設為 00h - NVM Subsystem Information**），讀取並記錄 NNSC (Capabilities) 欄位中的 **Status Reporting Enhancements (SRE)** 是否支援（若 SRE 欄位未設為 1 則此測試不適用）。
    3. 執行 **NVM Subsystem Reset**。
    4. 向 Management Endpoint Command Slot 0 發送 **Get State Control Primitive** 請求（Tag = 0x01, MEB = 1），記錄回傳的 MES 數據結構。
    5. 執行 **Management Endpoint Reset**。
    6. 再次發送相同的 **Get State Control Primitive** 請求，記錄並驗證 MES 數據。
- **預期觀測結果**：
    1. 在步驟 4 接收到的 MES 暫存器中，**Bit 14 (NSSRO) 必須精確設為 1**。
    2. **Bit 15 與 Bits 13:0 必須全部清除為 0**。

---

#### **Case 3: Management Endpoint State 暫存器錯誤旗標更新與清除驗證**

- **測試目標**： 驗證當待測物 (DUT) 在面對各種格式錯誤或異常的 MCTP 封包時，**MES 暫存器位元 13:6** 是否會被正確且精確地設置為 1，並能透過 CESF = 1 原子性清除。
- **測試流程**：
    1. 執行 MCTP 初始化，並發送 **Read NVMe-MI Data Structure (DTYP = 00h)** 確認裝置支援 SRE。
    2. 發送 **Get State Control Primitive** 請求（MEB = 1, CESF = 0），確認初始 MES 暫存器狀態。
    3. 依序注入下列 MCTP 與 NVMe-MI **異常/壞封包 (Error Stimulus)**：
        - 發送無效的 **Configuration Get** 請求（使用保留的 Configuration ID，如 0x1234）。
        - 發送 **Configuration Get** 請求（將 Tag Owner 位元誤設為 1）。
        - 以隨機時間間隔（100ms 至 500ms）發送 10 次 Configuration Get 指令以模擬網路延遲與**封包序號不連續 (Out-of-Sequence)**。
        - 刻意發送**無效目的端 ID (Destination EID)**、**錯誤傳輸單元大小 (Transmission Unit)**、**壞標頭版本 (Header Version)** 等異常封包。
    4. 發送 **Get State Control Primitive** 請求，記錄 MES 暫存器狀態。
    5. 發送 **Get State Control Primitive** 請求，並將 **CESF 位元設為 1**，等待並記錄回傳回應。
- **預期觀測結果**：
    1. 步驟 3 中除了正常的 Get State 外，所有異常命令都必須由 DUT **正確識別並回傳對應的錯誤狀態**（如 Bad Packet, Out-of-Sequence, Unknown Destination ID, Bad Header Version, Unsupported TU 等）。
    2. 在步驟 4 讀取的 MES 數據中，對應的錯誤旗標位元（**Bits 13:6**：包含 BPOPL、BUEMT、OSPSN、ITU、UDSTID、BHVS、UTUNT 等）**必須被正確設置為 1**。
    3. 步驟 5 (CESF = 1) 回傳的數據中，原先 MES 的狀態值被正確複製到回應的 CPSR 欄位；隨後，MES 暫存器中的 **Bits 14:03 應被原子性清除為 0h**。

---

#### **Case 4: NVM Subsystem Reset 清除 CCSF 數據結構驗證**

- **測試目標**： 驗證當發生 **NVM Subsystem Reset** 時，Composite Controller Status Flags (CCSF) 暫存器除了 HwInit 與 NSSRO 位元以外，其餘位元皆會被清除為 0。
- **測試流程**：
    1. 執行 MCTP 初始化。
    2. 發送 **Read NVMe-MI Data Structure (DTYP = 00h)**，記錄並確認支援 SRE。
    3. 執行一次 **Controller Level Reset**，藉此將 CCSF 數據結構中的 **Ready (RDY) 位元設置為 1**。
    4. 對 **Health Status Change (Configuration Identifier 02h)** 發送 **Configuration Get** 請求，確認 CCSF 至少有一個狀態位元被設為 1。
    5. 發送 **Reset 指令（RSTTYP = 00h - Reset NVM Subsystem）** 觸發 NVM Subsystem Reset。
    6. 再次發送對 **Health Status Change (CID = 02h)** 的 **Configuration Get** 請求，讀取 CCSF 狀態。
- **預期觀測結果**：
    1. 步驟 5 的 NVM Subsystem Reset 成功觸發。
    2. 在步驟 6 讀取的 CCSF 狀態中，驗證除了 **HwInit** 與 **NSSRO** 位元外，其餘所有狀態位元**皆必須被清零 (0)**。

---

#### **Case 5: 起始 Controller ID 超出最大範圍與 Persistent Event Log (PEL) 寫入驗證**

- **測試目標**： 驗證當對 DUT 發送 Controller Health Status Poll 命令且 **Starting Controller ID (SCTLID)** 超出最大支援 Controller ID 時，DUT 是否會回傳 **Invalid Parameter** 錯誤，且 PEL 欄位能精確指出錯誤位置，並寫入 **Persistent Event Log (PEL)**。
- **測試流程**：
    1. 執行 MCTP 初始化。
    2. 向 DUT 發送 **Controller Health Status Poll** 指令，故意將 **Starting Controller ID (SCTLID)** 欄位設置為**大於系統最大 Controller ID 的無效值**。
    3. 向 DUT 發送 **Get Log Page** 指令以讀取 **Persistent Event Log (LID = 0x0Dh)**。
- **預期觀測結果**：
    1. 在步驟 2 中，DUT 必須回傳 **Invalid Parameter** 錯誤，且回傳的 Parameter Error Location (PEL) 欄位應**精確指出無效 parameter 是 SCTLID 欄位**。
    2. 在步驟 3 的 Persistent Event Log (LID = 0x0Dh) 中，應能觀測到**對應的參數錯誤事件已被成功記錄**於 Log 數據中。

---
