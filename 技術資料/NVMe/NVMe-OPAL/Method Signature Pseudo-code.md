### **1. 方法簽名（Method Signatures）**

方法簽名是 TCG 方法的 **偽代碼（pseudo-code）** 表示方式，用來描述：

- 方法名稱（Method Name）
- 參數（Parameters）
- 回傳值（Results）

這樣的表示方式避免了直接使用 **位元組編碼（byte encodings）**，讓方法的描述更易讀、更直觀。

方法簽名的格式：

sql

複製編輯

`<InvokingID>.<MethodName>[     Required Parameter(s),     Optional Parameter(s) ]  =>  [ Result ]`

---

### **2. 方法呼叫（Method Invocation）**

TCG Opal 方法根據不同的對象類型，使用不同的 UID 來識別。

#### **a. Session Manager 方法（Session Manager Method Calls）**

- 由 Session Manager (SM) 負責管理的全域方法。
- UID：`SMUID = 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0xFF`
- 格式：
    
    css
    
    複製編輯
    
    `SMUID.MethodName[ <Parameters> ]`
    
- 範例：
    
    css
    
    複製編輯
    
    `SMUID.Properties[ <Parameters> ]`
    
    （調用 `Properties` 方法來獲取屬性資訊。）

---

#### **b. 安全性提供者 (SP) 方法（SP Method Calls）**

- 由 Security Provider (SP) 管理的安全功能。
- UID：`ThisSP = 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x01`
- 格式：
    
    css
    
    複製編輯
    
    `ThisSP.MethodName[ <Parameters> ]`
    
- 範例：
    
    css
    
    複製編輯
    
    `ThisSP.Random[ <Parameters> ]`
    
    （調用 `Random` 方法來獲取隨機數。）

---

#### **c. 表格（Table）方法（Table Method Calls）**

- 用於操作特定表格（Table）的方法，例如新增或查詢記錄。
- UID：`TableUID`（此表格的唯一識別碼）
- 格式：
    
    css
    
    複製編輯
    
    `TableUID.MethodName[ <Parameters> ]`
    
- 範例：
    
    css
    
    複製編輯
    
    `SomeLogTableUID.AddLog[ <Parameters> ]`
    
    （向 `SomeLogTableUID` 這張表格新增一條日誌記錄。）

---

#### **d. 物件（Object）方法（Object Method Calls）**

- 針對特定物件（Object）執行的方法，例如加密或解密操作。
- UID：`ObjectUID`（此物件的唯一識別碼）
- 格式：
    
    css
    
    複製編輯
    
    `ObjectUID.MethodName[ <Parameters> ]`
    
- 範例：
    
    css
    
    複製編輯
    
    `C_AES_128ObjectUID.Encrypt[ <Parameters> ]`
    
    （調用 `Encrypt` 方法，使用 `C_AES_128ObjectUID` 這個 AES 128 加密物件來進行加密。）

---

### **3. 方法簽名的實例**

舉例來說，某個方法簽名可能長這樣：

ruby

複製編輯

`ThisSP.GenerateKey[     KeyLength,     Algorithm ]  =>  [ GeneratedKey ]`

這表示：

1. 在 **ThisSP**（Security Provider）中調用 `GenerateKey` 方法。
2. **需要的參數（Required Parameter）**：`KeyLength`（金鑰長度）、`Algorithm`（加密演算法）。
3. **回傳值（Result）**：`GeneratedKey`（生成的金鑰）。

---

### **總結**

這段內容的重點是：

1. **方法簽名** 以偽代碼方式表示，避免直接處理位元組編碼，使得方法易於閱讀。
2. **不同類型的 TCG 方法調用**：
    - `SMUID.MethodName[...]` → **Session Manager 方法**
    - `ThisSP.MethodName[...]` → **Security Provider 方法**
    - `TableUID.MethodName[...]` → **表格操作**
    - `ObjectUID.MethodName[...]` → **物件方法（例如加密）**
3. **這種方法調用格式使得 TCG Opal 的方法描述清晰明瞭，可用於實作與調試。**

4o