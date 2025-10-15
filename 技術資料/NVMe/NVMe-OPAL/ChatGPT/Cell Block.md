## 🧩 一、cell_block 是什麼？

`cell_block` 是一種「區塊選擇器」，  
用來指定 **Table 的哪一個區塊（rows × columns）** 要被操作。

比如你要對某個表格（例如 ACE table, MBR table, DataStore table）進行：

- `.Get()` → 讀取部分內容
    
- `.Set()` → 寫入部分內容
    

那你就需要告訴控制器：「我要操作哪一個 cell 或哪一段區域」。

這時就要用 `cell_block`。

---

## 📘 二、cell_block 的結構（Name 對應關係）

|Name(hex)|名稱|意義|常用於|
|---|---|---|---|
|`0x00`|Table|要操作的 table UID|幾乎都可省略（因為已知）|
|`0x01`|startRow|開始的 Row（可以是 Row number 或物件 UID）|Table 操作時常用|
|`0x02`|endRow|結束的 Row|多筆連續資料時用|
|`0x03`|startColumn|開始的 Column number|一般 Table（多欄）時用|
|`0x04`|endColumn|結束的 Column number|多欄操作時用|

---

## 🧮 三、什麼時候用 startRow / endRow？

### 👉 用在「多筆 Row」的資料操作中：

也就是 **要指定多列 (rows)** 的情況。

|場景|範例|使用情況|
|---|---|---|
|要讀取多筆資料|`Table.Get[ Where = [ startRow=0, endRow=3 ] ]`|一次讀多筆|
|要更新部分行|`Table.Set[ Where = [ startRow=2 ] ]`|只改第2筆|
|要從某個 UID 所屬的列開始|`startRow = UID(Object1)`|針對特定物件|

🟢 **簡單說**：

- `startRow` 是「從哪一筆開始」
    
- `endRow` 是「到哪一筆結束」
    

如果是「物件導向表 (Object Table)」，`startRow` 可以直接用物件的 UID。

---

## 📊 四、什麼時候用 startColumn / endColumn？

### 👉 用在「多個欄位 (Columns)」的操作中：

也就是 **一筆資料內有多個欄位**，而你只要改其中一部分時。

|場景|範例|使用情況|
|---|---|---|
|只讀第 3 欄的資料|`startColumn=3, endColumn=3`|單一欄位|
|更新第 1~4 欄的資料|`startColumn=1, endColumn=4`|多欄同時修改|
|省略時|預設全欄都讀|若沒特別指定就全欄位|

🟢 **簡單說**：

- `startColumn` → 第一個欄位編號
    
- `endColumn` → 最後一個欄位編號
    
- 若都省略 → 預設整行（所有欄位）
    

---

## 🧠 五、使用情境對照表

|類型|方法|cell_block 範例|意義|
|---|---|---|---|
|Bytes Table|`.Get()`|`[startRow=0, endRow=255]`|讀整個 Byte 範圍|
|Object Table|`.Get()`|`[startRow=User1_UID]`|讀特定物件資料|
|Table|`.Set()`|`[startRow=0x01, startColumn=3, endColumn=5]`|修改指定欄位|
|Table|`.Delete()`|`[startRow=10, endRow=15]`|刪除多筆資料|

---

## ⚠️ 六、限制條件（常見錯誤）

1. **Object Table**：
    
    - `startRow` **必須是 UID**。
        
    - 若你用數字（RowNumber）會錯。
        
2. **Byte Table**：
    
    - 不允許用 `startColumn` / `endColumn`。
        
    - 只允許 Row 操作。
        
3. **省略規則**：
    
    - 若省略 `startRow` → 預設第 0 列（first row）。
        
    - 若省略 `endRow` → 預設最後一列。
        
    - 若省略 `startColumn` → 第一欄。
        
    - 若省略 `endColumn` → 最後一欄。
        

---

## ✅ 七、總結一句話

| 想做的事           | 要用的欄位                |
| -------------- | -------------------- |
| 操作哪一筆或哪幾筆「Row」 | `startRow`, `endRow` |
| 操作哪幾個「Column」  | `startColumn`, `end` |