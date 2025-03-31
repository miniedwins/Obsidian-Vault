## **1. Admin 模板 vs. Admin SP**

|**項目**|**Admin 模板**|**Admin SP**|
|---|---|---|
|**性質**|規範定義 (Template)|具體實作 (Instance)|
|**作用**|定義 SP (Security Provider) 的基本結構和行為|具體實作 **管理 SP** 的功能|
|**是否可變更**|**不可變更**，它是 TCG 規範的一部分|**可變更**，根據不同設備可能會有不同的設計|
|**用途**|提供 **SP 的標準定義**，但不執行實際管理功能|負責 **管理 TPer 內的 SP 和權限控制**|
|**UID 是否固定**|只是一個概念，沒有特定 UID|有具體 UID (如 `00 00 02 05`)|

換句話說，**Admin 模板 只是用來定義 SP 的架構，而 Admin SP 則是實際執行該功能的實例**。

---

## **2. 具體運作方式**

1. **Admin 模板 (SP Template)** 定義了 **SP (Security Provider)** 需要具備的屬性，例如：
    - SP 需要有 **權限管理機制**
    - SP 需要有 **存取控制表 (Access Control)**
    - SP 需要有 **方法 (Methods) 來管理其他 SP**
2. **Admin SP** 是 **基於 Admin 模板 來建立的具體 SP**，並且它的主要功能是：
    - 管理設備內的 **其他 SP** (例如 `Locking SP`)
    - **建立、刪除或修改** 權限 (例如 `Authority` 表)
    - 控制 **存取規則** (Access Control)
    - 管理 **C_PIN (Challenge-Response PIN)**
3. 在 **設備初始化時**，Admin SP 會根據 Admin 模板 **實例化**，並賦予一個 UID，例如：
    
    objectivec
    
    複製編輯
    
    `Admin SP UID: 00 00 02 05`
    

---

## **3. Admin SP 為什麼能管理 Locking SP？**

這是因為 **Admin SP 的主要職責是管理其他 SP**，所以在 **Admin SP 的 SP 表格 (Table 24 - SP Table Preconfiguration)** 內，會列出 **Admin SP 所管理的 SP**，包括：

- **自身的 UID (Admin SP)**
- **其他 SP 的 UID (Locking SP)**

例如，在你提供的 **Table 24 Admin SP - SP Table Preconfiguration** 內：

pgsql

複製編輯

`UID: 00 00 02 05  (Admin SP) SP Name: "Admin"  UID: 00 00 02 05 00 00 00 02 (Locking SP) SP Name: "Locking"`

這代表 **Admin SP 知道 Locking SP 的存在，並負責管理它**。

---

## **4. 具體存取方式**

如果你想查詢 **Admin SP 的相關資訊**，可以使用 **GET 命令**：

plaintext

複製編輯

`GET [UID = 00 00 02 05]`

這會回傳 **Admin SP 的屬性**。

如果你想查詢 **Admin SP 管理的 SP (如 Locking SP)**，可以查詢 SP 表格：

plaintext

複製編輯

`GET [Table = SP, SPID = 00 00 02 05]`

這會回傳 **Admin SP 內的 SP 列表**，其中應該會包含 `Locking SP`。

---

## **5. 總結**

- **Admin 模板**：只是 **定義** SP 該具備哪些功能，類似於一個「標準」。
- **Admin SP**：是 **實際的管理者**，負責控制 **設備內的 SP**，例如 `Locking SP`。
- **Admin SP 內有 Locking SP 的 UID**，是因為 **Admin SP 負責管理 Locking SP**。
- **Admin SP 是一個具體可存取的對象**，可以透過 **GET 指令** 來讀取它的資訊。