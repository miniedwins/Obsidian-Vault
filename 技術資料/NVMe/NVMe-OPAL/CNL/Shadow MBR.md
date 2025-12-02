
## 概要說明

`MBRControl` table 用來控制「Shadow MBR（虛擬主開機區）」的啟用與綁定關係。  
在鎖定狀態下，Storage Device 會讓主機讀到一個假的 MBR（通常是登入程式區），防止主機直接存取資料區。

## 主要欄位

### Shadow MBR Table

| 欄位名稱            | 說明                                     |
| --------------- | -------------------------------------- |
| **NamespaceID** | 指定哪一個 Namespace 的 MBR 被控制。             |
| **Enabled**     | `TRUE` 表示 Shadow MBR 已啟用；`FALSE` 表示停用。 |

### ANS_C (All Namespace Capable)

| 名稱            | 說明                                                     |
| ------------- | ------------------------------------------------------ |
| **ANS_C = 1** | 裝置支援 `NamespaceID = 0xFFFF_FFFF`，代表「全域控制所有 Namespace」。 |
| **ANS_C = 0** | 裝置不支援全域 Namespace，只能綁定到特定的 Namespace。                  |

## Set Method 限制條件總覽

| 編號    | 條件說明                                                                          | 結果                  | 解釋                                            |
| ----- | ----------------------------------------------------------------------------- | ------------------- | --------------------------------------------- |
| **①** | 指定的 Namespace 不存在（例：裝置只有 NS1～NS2，但你設 NS3）                                     | ❌ INVALID_PARAMETER | 不可綁不存在的 Namespace。例外：`0x0000_0000` 表示尚未綁定，允許。 |
| **②** | `Enabled = TRUE` 時修改 `NamespaceID`                                            | ❌ INVALID_PARAMETER | 啟用狀態中不可改 Namespace。必須先停用再修改。                  |
| **③** | `ANS_C = 0` 但設定 `NamespaceID = 0xFFFF_FFFF`                                   | ❌ INVALID_PARAMETER | 不支援全域 Namespace 的裝置不能用 `FFFF_FFFF`。           |
| **④** | `NamespaceID = 0x0000_0000` 時設定 `Enabled = TRUE`                              | ❌ INVALID_PARAMETER | 尚未綁定 Namespace 時不能啟用 Shadow MBR。              |
| **⑤** | 啟用 Shadow MBR 時 (`Enabled = TRUE`)，但 Namespace 的 LBA Format 與 MBR Table 格式不相容 | ⚠️ MAY fail         | 可能因格式不相容而拒絕啟用。                                |

---

## 正確設定流程

| 步驟  | 動作                                                             | 說明                                      |
| --- | -------------------------------------------------------------- | --------------------------------------- |
| 1️⃣ | 確認目標 Namespace 存在。                                             | 不能是不存在的或刪除的 Namespace。                  |
| 2️⃣ | 設定 `NamespaceID` = <有效的 Namespace> 或 `0xFFFF_FFFF`（若支援 ANS_C）。 | 綁定對象。                                   |
| 3️⃣ | 確認 `Enabled = FALSE`。                                          | 關閉狀態下修改。                                |
| 4️⃣ | 設定 `Enabled = TRUE`。                                           | 啟用 Shadow MBR。                          |
| 5️⃣ | 若要改變綁定 Namespace：                                              | 先 `Enabled = FALSE` → 再改 `NamespaceID`。 |
|     |                                                                |                                         |

---

## 錯誤操作範例

|操作|結果|原因|
|---|---|---|
|`Set NamespaceID = 0xFFFF_FFFF`，但 ANS_C = 0|INVALID_PARAMETER|裝置不支援全域 MBR 控制。|
|`Set Enable = TRUE`，但 NamespaceID = 0|INVALID_PARAMETER|尚未綁定任何 Namespace。|
|啟用中修改 NamespaceID|INVALID_PARAMETER|啟用狀態不可改動綁定。|

---

## 小結論

- **`NamespaceID` 要先正確設定，才能啟用 Shadow MBR。**
    
- **啟用狀態 (`Enabled=TRUE`) 下不可再修改 Namespace。**
    
- **`ANS_C` 為 1 時，可使用 `0xFFFF_FFFF` 進行全域綁定。**
    
- **若 Namespace 被刪除或 LBA 格式不符，啟用可能失敗。**


