### 🧩 1️⃣ Byte Table vs Object Table 差異

|類型|說明|典型用途|
|---|---|---|
|**Byte Table**|是一個「純資料表」，以 key-value（Byte Sequence）形式儲存任意資料。  <br>每一列通常由 UID + 二進位資料（byte blob）組成。|儲存大量原始資料，例如 DataStore、Log、或 Vendor 定義資料。|
|**Object Table**|儲存的是「物件 (Object)」，每列代表一個 TPer 內的邏輯物件（Object），而物件又包含多個屬性 (Column)。  <br>每個欄位有意義，例如 `Enabled`, `CommonName`, `Policy`, `BooleanExpr` 等。|儲存結構化的管理物件，如 Locking Range、Authority、ACE（Access Control Entry）等。|

**📘總結：**

- Byte Table = 類似 key-value blob store。
    
- Object Table = 類似關聯式資料表，有 schema、有欄位。
    
- Opal 裡幾乎所有管理結構（Authority, LockingRange, ACE…）都是 **Object Table**。
    

---

### 🧱 2️⃣ 圖中這張「Table 30 Locking SP - ACE Table Preconfiguration」 是 Object Table 還是 Object？

這是 **Object Table**。

理由如下：

- 標題明確寫「ACE Table Preconfiguration」，代表這是 SP（Security Provider）中的一張表。
    
- 表中的每一列（例如 `ACE_Anybody`, `ACE_Admin`）都是這張「ACE Object Table」裡的一個 **Object 實體**。
    
- 每個 Object 用一個 UID（例如 `00000008 00000001h`）標識。
    

所以：

> ✅ Table 30 = 一整張 Object Table  
> 每一列 = 一個 Object  
> 每個 Object 有自己的欄位（如 Name, BooleanExpr, Columns...）

---

### 🔍 3️⃣ 欄位 (Columns) 是否也是 Object？

這個要分層看：

|名稱|是 Object 嗎？|說明|
|---|---|---|
|**Table (ACE Table)**|✅ 是 Object Table|在 TPer 裡是一個 Object Table|
|**Row (例如 ACE_Admin)**|✅ 是 Object|它是 Table 裡的一筆 Object 實體，有自己的 UID|
|**Column (Name, BooleanExpr, Columns...)**|❌ 不是獨立 Object（通常是屬性欄位）|它們是 Object 的屬性（Attributes），儲存在該 Object 的資料空間中|

只有少數欄位如果本身是 UID（例如 Columns 欄位指向另一個 Object）  
→ 那就「間接引用另一個 Object」。

---

### 🔩 結論整理

| 層級     | 名稱                                  | 類型                   | 關係                                  |
| ------ | ----------------------------------- | -------------------- | ----------------------------------- |
| SP     | Locking SP                          | 一個 Security Provider | 管理整個 Storage Policy                 |
| Table  | ACE Table                           | Object Table         | SP 內的一張表                            |
| Row    | ACE_Admin (UID = 0000000800000002h) | Object               | ACE Table 的一筆資料                     |
| Column | BooleanExpr / Columns / Name        | 屬性欄位 (Attribute)     | 該 Object 的成員，不是獨立 Object（除非內容為 UID） |