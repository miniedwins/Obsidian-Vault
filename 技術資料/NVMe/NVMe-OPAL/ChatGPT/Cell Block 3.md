## 🧩 一、什麼是 `cell_block`

> `cell_block` = 一組 Named 值（name=value 結構），  
> 每個 name 是一個 **uinteger 索引**，表示這個值在這個 grouping 中的「位置」。  
> 整個 group 用 **List** 包起來。

它的用途：

- 在傳送一個命令（例如 `Set`, `Get`, `Delete`, `Add`）時，  
    需要指定要操作哪個表（table）、哪一列（row）、哪一欄（column），  
    這組資訊就是用 `cell_block` 表達的。
    

---

## 📦 二、基本結構範例（語法化）

`[cell_block] ::= List of Named(uinteger, value)  例如： [   { 0x00 : <table UID> },   { 0x01 : <row UID> },   { 0x02 : <column UID> },   { 0x03 : <optional component> }, ]`

其中每一個 `{ name : value }` 都是 Named 結構，  
外層用 List 包住，整體就稱為一個 `cell_block`。

---

## 🔢 三、組成項目與規則說明

|索引 (name)|名稱|值類型|意義|預設/限制|
|---|---|---|---|---|
|**0x00**|Table|UID|指定要操作的 Table|若呼叫是在 Table 上 → 可省略；若呼叫在 Object 上 → **必須省略**，否則錯誤|
|**0x01**|Row|UID|指定 Table 中的 Row|可省略（依 method context）|
|**0x02**|Column|UID|指定 Table 中的 Column|依操作而定，可省略|
|**0x03+**|其他欄位|視表格定義而定|特殊用途（依不同表格定義）|依規格或 context|

---

## ⚙️ 四、行為規則（你引的那三條重點）

這三條是針對 `0x00` = Table 欄位的限制：

|條文|意義|
|---|---|
|a.|若沒有指定 Table（省略 0x00），預設就是對「呼叫這個 method 的 table」操作。|
|b.|若 method 是對某個 **Object** 呼叫的（例如某個 row 或 object instance），則 **不得出現 Table 欄位 (0x00)**。若有，操作直接失敗。|
|c.|若是對 Table 呼叫 `Get`，同樣 **不得指定 Table 欄位**。如果你在 `Get`(table) 時帶了 0x00，則也會 fail。|

換句話說：

|呼叫對象|可否有 Table (0x00)?|結果|
|---|---|---|
|呼叫在 Table 上 (`table.Get()`)|❌ 不可有|否則失敗|
|呼叫在 Object 上 (`object.Get()`)|❌ 不可有|否則失敗|
|呼叫在 SP 上（跨 Table 操作）|✅ 可有|指定要操作哪個 Table|
|省略 0x00|✅|表示使用「當前操作對象」|

---

## 🧠 五、舉例說明（實際情境）

### ✅ 範例 1：對 Table 呼叫 `Get`

你想取得 Locking Table 的所有列

`Method: Get Invoked on: Locking Table cell_block: [   {0x01 : 0x00}   # Row 0 ]`

不能包含 `{0x00 : <table UID>}`，否則規範規定「method SHALL fail」。

---

### ✅ 範例 2：對 SP 呼叫跨表操作

你在 Admin SP 上呼叫 `Get` 想要指定某個 Table

`Method: Get Invoked on: Admin SP cell_block: [   {0x00 : <Locking.Table UID>},   # 指定 Table   {0x01 : <某個 row UID>} ]`

這時 0x00 就必須要出現，因為你要告訴 SP：「我要操作哪張表」。

---

### ✅ 範例 3：對 Object 呼叫 `Set`

你在某個 Row（Object）上呼叫 `Set` 更新欄位值：

`Method: Set Invoked on: Locking Object cell_block: [   {0x02 : <ColumnUID>},   # 指定要改哪個欄位 ]`

這時 `0x00` 也不能出現，因為你已經是針對這個 Object 操作。

---

## 📘 六、簡化理解

| Level     | 呼叫對象                | 是否需要 Table (0x00) | cell_block 範例                        |
| --------- | ------------------- | ----------------- | ------------------------------------ |
| SP 層級     | AdminSP / LockingSP | ✅ 需要              | `{0x00: <tableUID>, 0x01: <rowUID>}` |
| Table 層級  | LockingTable        | ❌ 不要有             | `{0x01: <rowUID>}`                   |
| Object 層級 | LockingObject       | ❌ 不要有             | `{0x02: <columnUID>}`                |

## 🧩 一、`cell_block` 整體結構回顧

前面提到：

|名稱|名稱值 (uinteger)|用途|
|---|---|---|
|0x00|Table|指定要操作哪個 Table|
|0x01|**startRow**|起始 Row（或 Object）|
|0x02|**endRow**|結束 Row（僅適用 byte table）|

---

## 🧠 二、`startRow` (Name = 0x01)

### 📘 定義

> `startRow` 代表要從哪一個 row 開始操作。  
> 這個值可以是：  
> 1️⃣ `uid`（某個 Object 的唯一識別符）  
> 2️⃣ `RowNumber`（數值，用於 bytes table）

這兩者 **只能擇一**，不能同時出現。

---

### ⚙️ 使用規則

|呼叫對象|是否必填|值型態|特殊規則|
|---|---|---|---|
|**Bytes Table**|可省略|RowNumber (uinteger)|若省略 → 預設為第 1 row（row 0）|
|**Object Table**|✅ 必填|Object UID|若省略 → 失敗；若 UID 不屬於該表 → 失敗|
|**Object**|❌ 不可有|無|若帶入 → 失敗|

---

### 📘 實際例子

#### ✅ Case 1：Get from Bytes Table

想從 bytes table 的第一列開始：

`cell_block: [   { 0x01 : 0x00 }  # RowNumber = 0 ]`

或可省略，因為預設是第一列。

---

#### ✅ Case 2：Get from Object Table

你要操作 UID 為 `0x9001` 的 Locking Object：

`cell_block: [   { 0x01 : 0x9001 }   # Object UID ]`

→ 如果你沒帶 `{0x01: ...}`，則規範說「method invocation SHALL fail」。

---

#### ❌ Case 3：Method invoked on Object

如果你直接對 Object 呼叫：

`LockingObject[0x9001].Set(...)`

就 **不能再帶 0x01**，否則 fail。  
因為 context 已經是那個 Object，不需要再指名。

---

## 🧠 三、`endRow` (Name = 0x02)

### 📘 定義

> `endRow` 用於指定結束的 row 編號（RowNumber），僅用於 bytes table。

它的功能：讓你指定從哪一列到哪一列，類似範圍操作。

---

### ⚙️ 使用規則

|呼叫對象|是否可用|值型態|預設值|備註|
|---|---|---|---|---|
|**Bytes Table**|✅ 可用|uinteger (RowNumber)|若省略 → 最後一列|可形成範圍 `[startRow, endRow]`|
|**Object Table**|❌ 不可有|無|無|若出現 → 失敗|
|**Object**|❌ 不可有|無|無|若出現 → 失敗|

---

### 📘 實際例子

#### ✅ Case 1：Get from Bytes Table rows 0–5

`cell_block: [   { 0x01 : 0x00 },  # startRow = 0   { 0x02 : 0x05 }   # endRow = 5 ]`

#### ✅ Case 2：Get all rows from Bytes Table

`cell_block: [ ]`

→ 省略 0x01 和 0x02，預設範圍 = firstRow → lastRow

#### ❌ Case 3：Get from Object Table

`cell_block: [   { 0x01 : <ObjectUID> },   { 0x02 : 0x05 }    # ❌ 錯誤，Object Table 不允許 endRow ]`

---

## 📊 四、整體結構示意圖

`cell_block (List)  ├── { 0x00 : <Table UID> }     # Table (optional)  ├── { 0x01 : <startRow> }      # RowNumber 或 Object UID  └── { 0x02 : <endRow> }        # RowNumber (only for bytes table)`

---

## ✅ 五、簡化理解表

| 操作對象         | 0x00 (Table) | 0x01 (startRow)   | 0x02 (endRow) | 備註              |
| ------------ | ------------ | ----------------- | ------------- | --------------- |
| SP           | ✅ 可有         | ✅ 可有              | ✅ 可有          | 明確指定 Table 與範圍  |
| Bytes Table  | ❌ 不可有        | 可省略 (預設首列)        | 可省略 (預設末列)    | 用 RowNumber     |
| Object Table | ❌ 不可有        | ✅ 必填 (Object UID) | ❌ 不可有         | 針對特定 Object     |
| Object       | ❌ 不可有        | ❌ 不可有             | ❌ 不可有         | context 已隱含 row |