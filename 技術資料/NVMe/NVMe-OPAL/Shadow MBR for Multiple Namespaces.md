

# 📘 MBRControl Table 筆記整理

## 🔹目的

`MBRControl` table 用來控制「Shadow MBR（虛擬主開機區）」的啟用與綁定關係。  
在鎖定狀態下，Storage Device 會讓主機讀到一個假的 MBR（通常是登入程式區），防止主機直接存取資料區。

---

## 🔹主要欄位

|欄位名稱|說明|
|---|---|
|**NamespaceID**|指定哪一個 Namespace 的 MBR 被控制。|
|**Enabled**|`TRUE` 表示 Shadow MBR 已啟用；`FALSE` 表示停用。|

---

## 🔹ANS_C (All Namespace Capable)

|名稱|說明|
|---|---|
|**ANS_C = 1**|裝置支援 `NamespaceID = 0xFFFF_FFFF`，代表「全域控制所有 Namespace」。|
|**ANS_C = 0**|裝置不支援全域 Namespace，只能綁定到特定的 Namespace。|

---

## 🔹Set Method 限制條件總覽

| 編號    | 條件說明                                                                          | 結果                  | 解釋                                            |
| ----- | ----------------------------------------------------------------------------- | ------------------- | --------------------------------------------- |
| **①** | 指定的 Namespace 不存在（例：裝置只有 NS1～NS2，但你設 NS3）                                     | ❌ INVALID_PARAMETER | 不可綁不存在的 Namespace。例外：`0x0000_0000` 表示尚未綁定，允許。 |
| **②** | `Enabled = TRUE` 時修改 `NamespaceID`                                            | ❌ INVALID_PARAMETER | 啟用狀態中不可改 Namespace。必須先停用再修改。                  |
| **③** | `ANS_C = 0` 但設定 `NamespaceID = 0xFFFF_FFFF`                                   | ❌ INVALID_PARAMETER | 不支援全域 Namespace 的裝置不能用 `FFFF_FFFF`。           |
| **④** | `NamespaceID = 0x0000_0000` 時設定 `Enabled = TRUE`                              | ❌ INVALID_PARAMETER | 尚未綁定 Namespace 時不能啟用 Shadow MBR。              |
| **⑤** | 啟用 Shadow MBR 時 (`Enabled = TRUE`)，但 Namespace 的 LBA Format 與 MBR Table 格式不相容 | ⚠️ MAY fail         | 可能因格式不相容而拒絕啟用。                                |

---

## 🔹正確設定流程 ✅

|步驟|動作|說明|
|---|---|---|
|1️⃣|確認目標 Namespace 存在。|不能是不存在的或刪除的 Namespace。|
|2️⃣|設定 `NamespaceID` = <有效的 Namespace> 或 `0xFFFF_FFFF`（若支援 ANS_C）。|綁定對象。|
|3️⃣|確認 `Enabled = FALSE`。|關閉狀態下修改。|
|4️⃣|設定 `Enabled = TRUE`。|啟用 Shadow MBR。|
|5️⃣|若要改變綁定 Namespace：|先 `Enabled = FALSE` → 再改 `NamespaceID`。|

---

## 🔹錯誤操作範例 ❌

|操作|結果|原因|
|---|---|---|
|`Set NamespaceID = 0xFFFF_FFFF`，但 ANS_C = 0|INVALID_PARAMETER|裝置不支援全域 MBR 控制。|
|`Set Enable = TRUE`，但 NamespaceID = 0|INVALID_PARAMETER|尚未綁定任何 Namespace。|
|啟用中修改 NamespaceID|INVALID_PARAMETER|啟用狀態不可改動綁定。|

---

## 🔹小結論

- **`NamespaceID` 要先正確設定，才能啟用 Shadow MBR。**
    
- **啟用狀態 (`Enabled=TRUE`) 下不可再修改 Namespace。**
    
- **`ANS_C` 為 1 時，可使用 `0xFFFF_FFFF` 進行全域綁定。**
    
- **若 Namespace 被刪除或 LBA 格式不符，啟用可能失敗。**



## Deassign Method of Operation
1️⃣ 先把所有 **Namespace Non-Global Range Locking object** 全部解除 (Deassign)  
2️⃣ 再解除 **Namespace Global Range Locking object**  
3️⃣ 最後才能執行 **Namespace Management command → Delete Namespace**

## RevertSP

### 🧩 原文分析：

#### 🔸 第一段：

> If a namespace is associated with a Namespace Global Range Locking object when the RevertSP method is invoked,  
> then the media encryption key of that namespace is eradicated, regardless of whether the KeepGlobalRangeKey parameter is set to TRUE or FALSE.

📖 意思是：

- 若 Namespace 在執行 `RevertSP()` 時，仍「連結著」它自己的 **Namespace Global Range Locking object**，
    
- 那麼這個 Namespace 的媒體加密金鑰 **一定會被清除（eradicated）**。
    
- 即使你設定 `KeepGlobalRangeKey=TRUE`，也沒用。
    

💡 換句話說：

> `RevertSP` 不會保留 Namespace Global Range 的 key，只有在 namespace 已經「解除關聯（deassign）」的情況下，才有機會保留。

---

#### 🔸 第二段：

> If the invoker of the RevertSP method wishes to keep the keys associated with Namespace Global Range Locking objects,  
> the Deassign method should be invoked on those Namespace Global Range Locking objects prior to invoking the RevertSP method.

📖 意思是：

- 若你想要「保留 Namespace Global Range 的加密金鑰」，
    
- 你**必須先呼叫 `Deassign()`**，把 Namespace 從它的 Namespace Global Range Locking object 解除關聯，
    
- 然後再執行 `RevertSP()`。
    

---

#### 🔸 第三段：

> If the Deassign method is successfully invoked on a Namespace Global Range Locking object before the RevertSP method is invoked,  
> then the media encryption key of that namespace/LUN would be associated with the Global Range Locking object at time of RevertSP method invocation.

📖 意思是：

- 當你成功 `Deassign()` 後，
    
    - 該 Namespace 原本的 media key（屬於 Namespace Global Range Locking object）
        
    - 會被「交還」給 **Global Range Locking object** 管理。
        
- 這樣在 `RevertSP()` 執行時，該 Namespace 的 key 不會被清除，  
    因為它現在屬於 Global Range Locking object。
    

---

### 🔐 整體邏輯圖（簡化理解）

|狀態|動作|結果|
|---|---|---|
|Namespace still linked to Namespace Global Range LO|`RevertSP()`|🔥 該 Namespace 的 media key 被清除（eradicated）|
|Namespace **Deassigned** 回 Global Range LO|`RevertSP()`|✅ key 保留（因為屬於 Global Range LO）|

### 🔹 第一段

> Upon successful invocation of the RevertSP method, the method SHALL increment the Unused Key Count by the number of Namespace Non-Global Range Locking objects when the method was invoked.

意思是：

- 當你執行 `RevertSP()` 成功後，
    
- **TPer 會把 “Namespace Non-Global Range Locking objects” 的數量加回 Unused Key Count。**
    

💡 為什麼？

- 因為 `RevertSP` 會「解除所有 Namespace Non-Global Range Locking objects」。
    
- 這些 Locking objects 原本各自佔用一把 key（在 Assign 時 Unused Key Count 減 1）。
    
- 當你 revert（重置）時，它們都被清除、釋放出來，  
    所以要把那幾把 key **加回 pool** → 也就是「Unused Key Count +N」。
    

🧠 換句話說：

> RevertSP = 釋放所有 Non-Global Range 的金鑰佔用。

---

### 🔹 第二段

> If the RevertSP method is invoked with the KeepGlobalRangeKey parameter set to TRUE, then the TPer SHALL:  
> a) continue to use the media encryption key for each namespace/LUN that was associated with the Global Range Locking object; and  
> b) eradicate the media encryption key associated with the K_AES_* object indicated by the ActiveKey column value of each Non-Global Locking object.

意思是：

- 若 `KeepGlobalRangeKey=TRUE`：
    
    - (a) Global Range Locking object 的 key 保留，不清除；
        
    - (b) 但所有 Non-Global（包含 Namespace Global Range 和 Namespace Non-Global Range）的 key 都要被清除。
        

🧠 所以：

> Unused Key Count 加回來的是「被清掉的 Non-Global Range keys」。

---

### 🔹 第三段

> The Unused Key Count SHALL NOT be otherwise affected by the RevertSP method invocation, i.e. the Unused Key Count should not be returned to its OFS values.

意思是：

- 除了上述的「加回 Non-Global Range key 數量」之外，
    
    - `RevertSP` 不應該重設 Unused Key Count 為出廠（OFS, Original Factory Setting）值。
        
- 換句話說：
    
    - 不會「歸零」或「回復初始出廠值」，
        
    - 只會針對被釋放的 Non-Global Range key 做 **增量回補**。

## 後續需要解決的問題
1. 如何區別回傳的錯誤 ( TCG OPAL 或是 NVMe Error )
2. 測試 CNL 需要測試軟體需要維護一個 Locking Table
3. 如何將需要的命令 Assign and Deassign Method 做出來
4. 如何將所有的核心測試方法整理成一個 Q&A
