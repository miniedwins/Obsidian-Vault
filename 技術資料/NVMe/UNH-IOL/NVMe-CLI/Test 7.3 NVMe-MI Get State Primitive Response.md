以下為您整理並修正筆誤與排版混淆後，**Test 7.3 Case 1 至 Case 4** 的完整測試目標、測試流程與預期觀測結果對照表：

---

### **Test 7.3 – NVMe-MI Get State Primitive Response (FYI)**

#### **Case 1: NVMe-MI Get State Primitive Response**

- **測試目標 (Test Purpose)：**  
    驗證待測物（DUT）的管理端點（Management Endpoint）是否支援 `Get State` 控制原型（Control Primitive），以及其對「清除錯誤狀態旗標（CESF = 1）」與「僅讀取旗標（CESF = 0）」的回應機制是否正確符合規範。
- **測試流程 (Test Procedure)：**
    1. 進行 MCTP 初始化。
    2. 發送 `Get Endpoint ID` 指令。
    3. 發送 `Get State` 控制原型請求，並將 **CESF (Clear Error State Flags) 位元設為 1**。
    4. 發送第二次 `Get State` 控制原型請求，同樣將 **CESF 設為 1**。
    5. 發送一個具有**無效標頭版本 (Bad Header Version)** 的 `Get Endpoint ID` 封包。
    6. 發送 `Get State` 請求，並將 **CESF 設為 0**（僅讀取不清除）。
    7. 發送 `Get State` 請求，並將 **CESF 設為 1**（讀取並清除）。
    8. 發送 `Get State` 請求，並將 **CESF 設為 0**。
    9. 依序重複上述流程，但改為發送以下異常條件封包以誘發對應的錯誤旗標：
        - 發送無 SOM 且無 EOM 標記的 `Get Endpoint ID` 中間封包（Middle Packet）。
        - 發送無效目的端 ID 的封包（Destination Endpoint ID = 0x11）。
        - 發送錯誤 Tag 所有者（Tag Owner = 01b）的封包。
        - 發送錯誤 MIC (CRC) 檢驗碼的 `Read NVMe-MI Data Structure` 指令。
        - 發送錯誤 LCRC 的 `Read NVMe-MI Data Structure` 指令（僅適用於 PCIe VDM 傳輸）。
- **預期觀測結果 (Observable Results)：**
    1. 待測物在遭遇上述異常條件封包時，必須依規格書規定靜默丟棄（Drop）封包，但必須在**管理端點狀態（Management Endpoint State, MES）資料結構中，精確地將對應的錯誤旗標位元（Bits 13:6）標記為 1**。
    2. 當發送 **CESF = 0** 的 `Get State` 請求時，回傳的狀態中對應的錯誤旗標必須依然為 1。
    3. 當發送 **CESF = 1** 的 `Get State` 請求後，錯誤旗標必須隨即被**原子性地重置為 0**，並在後續 CESF = 0 的讀取中確認旗標已皆成功清除為 0h。

---

#### **Case 2: MES Bits Cleared on NVM Subsystem Reset**

_(原規範書將此流程誤植於 Case 1 的預期結果中，此處已校正回獨立 Case 2)_

- **測試目標 (Test Purpose)：**  
    驗證發生 **NVM Subsystem Reset (子系統重置)** 時，Management Endpoint State (MES) 資料結構中除了 **Bit 14 (NSSRO - NVM Subsystem Reset Occurred)** 之外的所有狀態旗標與錯誤位元是否都能被正確初始化清除。
- **測試流程 (Test Procedure)：**
    1. 進行 MCTP 初始化。
    2. 發送 `Read NVMe-MI Data Structure` 指令 (DTYP = 0x00)，記錄 `NNSC` (NVM Subsystem Capabilities) 的欄位值。_(若不支援 Status Reporting Enhancements 則此 Case 不適用)_。
    3. **執行 NVM Subsystem Reset (子系統重置)**。
    4. 發送 `Get State` 控制原型請求至 Command Slot 0（Header 的 MEB 設為 0x01），記錄並驗證返回的 MES 資料結構。
    5. 執行 `Management Endpoint Reset`。
    6. 再次發送 `Get State` 請求並記錄 MES 狀態。
- **預期觀測結果 (Observable Results)：**
    1. 驗證在 NVM Subsystem Reset 之後，MES 資料結構中的 **Bit 14 (NSSRO) 必須被正確設為 1**。
    2. 驗證 MES 的 **Bit 15 (Pause Flag) 與 Bits 13:0 必須皆成功被清除為 0**。

---

#### **Case 3: MES Expected Error Updates**

- **測試目標 (Test Purpose)：**  
    驗證 Management Endpoint 在遭遇**各種實體層與傳輸層的封包錯誤**時，是否能在 MES 結構中的對應位元（Bits 13:6）**正確且精確地將錯誤狀態更新標記為 1**，並能透過 CESF 順利重置清除。
- **測試流程 (Test Procedure)：**
    1. 進行 MCTP 初始化並讀取 `Read NVMe-MI Data Structure` 以確認 SRE 與 NNSC 支援度。
    2. 發送初始的 `Get State` 請求，記錄乾淨的 MES 狀態。
    3. 傳送 `Get State` 請求，並將 Clear Error State Flags (CESF) 設為 0。
    4. 發送一個包含無效設定的 `Configuration Get` 指令（如：不支援的配置識別碼 0x1234）。
    5. 發送 `Configuration Get` 指令（Config ID = 01h）並故意將 Tag Owner (TO) 欄位設為 1b。
    6. 在短時間內隨機發送 10 次 `Configuration Get` 指令以模擬網路延遲與序號亂序。
    7. 發送 `SOM = 0b` 且 `EOM = 0b` 的異常中間封包，且其 Payload 大小不等於起頭封包的 Payload 大小。
    8. 發送 `Configuration Get` 指令並將 Destination Endpoint ID 設為無效的 0xFF。
    9. 發送 `Configuration Get` 指令並將 Header Version 欄位設為無效的 0xF。
    10. 發送 `Configuration Get` (Config ID = 03h) 取得 TU Size，再發送一個傳輸大小不符的配置指令。
    11. 發送 `Get State` 控制原型請求（MEB 設為 0x01）並記錄回傳的 MES。
    12. 發送 `Get State` 控制原型請求，並將 Clear Error State Flags (CESF) 設為 1。
- **預期觀測結果 (Observable Results)：**
    1. 除了正常的 `Get State` 之外，所有發送的異常指令皆應回傳對應的錯誤狀態回應（如：Invalid Parameter、Bad Header 等）。
    2. 驗證 MES 中記錄各種錯誤狀態的 **Bits 13:6 皆成功被標記為 1**，證明包含：BPOPL (壞封包/物理層錯誤)、BUEMT (錯誤Message Tag)、OSPSN (序號不連續)、ITU (錯誤傳輸單元)、UDSTID (未知目的端 ID)、BHVS (錯誤標頭版本)、UTUNT (不支援傳輸單元) 等錯誤均被精確記錄。
    3. 驗證 MES 的值成功被複製回傳至控制原型回應的 `Control Primitive Specific Response` 欄位中。
    4. 驗證在執行 CESF = 1 的清除請求後，MES 中的 **Bits 14:03 被成功重置清除為 0**。

---

#### **Case 4: NVM Subsystem Reset Clears CCSF Data Structure**

- **測試目標 (Test Purpose)：**  
    驗證執行 **NVM Subsystem Reset** 後，複合控制器狀態旗標 (Composite Controller Status Flags, CCSF) 資料結構中，除了硬體初始化狀態 (`HwInit`) 與重置發生記錄 (`NSSRO`) 外，其餘所有的狀態旗標（例如 Ready 位元）是否都會被成功**清除重置為 0**。
- **測試流程 (Test Procedure)：**
    1. 進行 MCTP 初始化並記錄 NNSC。
    2. 執行 **Controller Level Reset (CLR，控制器層級重置)**，將 CCSF 中的 Ready (RDY) 位元設為 1。
    3. 發送 `Configuration Get` 讀取 `Health Status Change` (Config ID = 02h)，確認 CCSF 暫存器中至少有一個狀態位元被設為 1。若皆為 0 則跳過此測試。
    4. **執行 NVM Subsystem Reset (子系統重置)**。
    5. 再次發送 `Configuration Get` 讀取 `Health Status Change` (Config ID = 02h)，比對重置前後的暫存器旗標。
- **預期觀測結果 (Observable Results)：**
    1. 驗證在執行 NVM Subsystem Reset 後，除了 `HwInit` 和 `NSSRO` 這兩個必要的初始化旗標外，**CCSF 欄位中的其餘所有狀態旗標皆必須成功被清除為 0**。

---

