## ⚠️ 問題原因：Overlapping Locking Ranges

根據 TCG Opal 規範：

> Any Set method invocation that results in overlapping LBA ranges is prohibited.

也就是說：

- 同時存在的兩個非 Global Range **不能有重疊的 LBA 區間**。
    
- 若有重疊，TPer **會拒絕**（回錯誤碼）。
    

你的例子：

> Range8 = 0–100  
> Range7 = 0–200  
> 這兩個重疊在 0–100 → ❌ 不允許。

---

## 🧠 原因（為什麼會禁止重疊）

每個 Locking Range 都有一把獨立的 **Media Encryption Key (MEK)**。  
若兩個 Range 控制到相同的 LBA，就會發生：

- 一個 LBA 可能同時對應兩把不同的加密金鑰。
    
- TPer 不知道該用哪一把 Key 解密那個區塊。
    
- 導致資料混亂或毀損。
    

所以規範強制禁止這種狀況。

---

## ✅ 正確做法

要從 Range8 (0–100) 改成使用 Range7 (0–200)，  
你必須先讓 Range8 **不再佔用 LBA 0–100**，也就是解除它的控制。

---

### 步驟流程：

#### 🔹 Step 1：刪除或縮小 Range8

讓 Range8 不再覆蓋 0–100。  
有兩種方式：

##### 方式 A：縮小 Range8 的範圍

把 Range8 改成 LBA=101–xxx（確保不重疊）。

`Set LockingRange8:   RangeStart = 101   RangeLength = (舊長度 - 101)`

##### 方式 B：刪除 Range8

設定它的 `RangeLength = 0`

`Set LockingRange8:   RangeLength = 0`

根據 spec：

> Zero-length Locking Range controls no LBAs and does not overlap any other range.

這樣 Range8 不再控制任何 LBA，就釋放了 0–100 的區間。

---

#### 🔹 Step 2：設定新的 Range7

現在可以建立或修改 Range7：

`Set LockingRange7:   RangeStart = 0   RangeLength = 200`

---

#### 🔹 Step 3：（選擇性）產生新 Key

由於這是新範圍，建議產生新 Key：

`GenKey(LockingRange7.ActiveKey)`

---

#### 🔹 Step 4：執行 Secure Erase（視需求）

如果你想確保之前 Range8 控制的資料（0–100）不可讀：

`GenKey → 相當於 Secure Erase`

---

## 🧭 範例流程摘要：

|步驟|指令|說明|
|---|---|---|
|1|`Set LockingRange8.RangeLength = 0`|釋放 LBA 0–100|
|2|`Set LockingRange7.RangeStart = 0, RangeLength = 200`|新建範圍|
|3|`GenKey(LockingRange7.ActiveKey)`|產生新加密金鑰|
|4|`Set LockingRange7.ReadLockEnabled/WriteLockEnabled = TRUE`|啟用鎖定|

---

## 🔒 小提醒

- Global Range 會自動接手那些不屬於任何 Locking Range 的 LBA。
    
- 所以當 Range8 被清空（Length=0）後，那些區域會暫時回歸 Global Range。
    
- 再由 Range7 接手後，控制權就會轉移。
    

---

## ✅ 總結

|狀況|行為|
|---|---|
|Range 重疊|❌ 規範禁止|
|RangeLength=0|✅ 安全釋放區間|
|新 Range 設定|✅ 必須避開現有範圍|
|換 Key (`GenKey`)|✅ 由 Host 主動執行|
|自動換 Key|❌ 不會自動發生|