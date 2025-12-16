## 測試案例 1（正常行為）

### Title

在 MBRControl 未啟用狀態下，允許指定 NamespaceID 為 0x0000_0000

### Description

此測試用來確認：  
當 MBRControl 功能尚未啟用時，系統允許將 NamespaceID 指定為保留值 `0x0000_0000`，並且不將此行為視為參數錯誤。

本案例僅驗證 NamespaceID 指定行為，不驗證 MBRControl 啟用流程。

### Steps

1. 確認目前 MBRControl 功能尚未啟用，且系統允許進行設定相關操作
    
2. 透過 MBRControl 的設定流程，嘗試指定其 NamespaceID 欄位
    
3. 指定的目標為保留值 `0x0000_0000`，不觸發任何啟用行為
    

### Expected Result

1. 系統接受此次 NamespaceID 指定請求，未拒絕該行為
    
2. MBRControl 中顯示的 NamespaceID 為 `0x0000_0000`
    
3. 系統未回報任何與參數無效或狀態不允許相關的錯誤
    

---

## 測試案例 2（正常行為）

### Title

在 Namespace 存在且格式相容時成功啟用 MBRControl

### Description

此測試用來確認：  
當指定的 Namespace 確實存在，且其 LBA 格式與 MBR 表內容相容時，系統允許啟用 MBRControl 功能。

本案例不驗證 NamespaceID 合法性以外的其他邊界條件。

### Steps

1. 選擇一個系統中實際存在的 Namespace
    
2. 確認該 Namespace 的 LBA 格式與 MBR 表內容相容
    
3. 以該 Namespace 為目標，嘗試啟用 MBRControl 功能
    

### Expected Result

1. 系統接受啟用 MBRControl 的請求
    
2. MBRControl 進入啟用狀態
    
3. 系統未回報任何與格式或參數相關的錯誤
    

---

## 測試案例 3（邊界／異常）

### Title

指定不存在的 Namespace 作為 NamespaceID 時應被拒絕

### Description

此測試用來確認：  
當嘗試將 NamespaceID 指向一個不存在的 Namespace（且非保留值 0x0000_0000）時，系統必須拒絕該行為，以避免引用無效資源。

### Steps

1. 確認目前 MBRControl 尚未啟用
    
2. 選擇一個系統中不存在的 Namespace
    
3. 嘗試將 MBRControl 的 NamespaceID 指向該不存在的 Namespace
    

### Expected Result

1. 系統拒絕此次 NamespaceID 指定請求
    
2. 系統回報「參數無效」方向的錯誤
    
3. NamespaceID 維持原有設定，不被變更
    

---

## 測試案例 4（邊界／異常）

### Title

在 MBRControl 已啟用狀態下嘗試變更 NamespaceID

### Description

此測試用來確認：  
一旦 MBRControl 已啟用，系統不允許再變更其 NamespaceID，以確保保護範圍的一致性。

### Steps

1. 確認 MBRControl 已處於啟用狀態
    
2. 嘗試透過設定流程變更目前使用的 NamespaceID
    

### Expected Result

1. 系統拒絕此次 NamespaceID 變更行為
    
2. 系統回報「參數無效」或「狀態不允許」方向的錯誤
    
3. 原有 NamespaceID 維持不變
    

---

## 測試案例 5（邊界／異常）

### Title

在裝置不支援 Multiple Namespaces 時指定 NamespaceID 為 0xFFFF_FFFF

### Description

此測試用來確認：  
當裝置回報不支援 Multiple Namespaces 功能時，系統不得接受代表「所有 Namespace」的特殊值 `0xFFFF_FFFF`。

### Steps

1. 確認裝置回報 Multiple Namespaces 支援數量為零
    
2. 確認 MBRControl 尚未啟用
    
3. 嘗試將 MBRControl 的 NamespaceID 指定為「所有 Namespace」
    

### Expected Result

1. 系統拒絕該 NamespaceID 指定行為
    
2. 系統回報「參數無效」方向的錯誤
    
3. NamespaceID 不發生變更
    

---

## 測試案例 6（邊界／異常）

### Title

在 NamespaceID 尚未指向實際 Namespace 時嘗試啟用 MBRControl

### Description

此測試用來確認：  
當 NamespaceID 尚未指向任何實際 Namespace（保留值狀態）時，系統不允許啟用 MBRControl，以避免未定義的保護行為。

### Steps

1. 確認目前 MBRControl 的 NamespaceID 為保留值，未對應實際 Namespace
    
2. 嘗試啟用 MBRControl 功能
    

### Expected Result

1. 系統拒絕啟用 MBRControl 的請求
    
2. 系統回報「參數無效」方向的錯誤
    
3. MBRControl 維持未啟用狀態
    

---

## 測試案例 7（邊界／異常）

### Title

當 Namespace 的 LBA 格式與 MBR 表不相容時嘗試啟用 MBRControl

### Description

此測試用來確認：  
當指定的 Namespace 存在，但其 LBA 格式與 MBR 表內容不相容時，系統可能拒絕啟用 MBRControl，並回報格式不相容相關錯誤。

### Steps

1. 選擇一個實際存在的 Namespace
    
2. 確認該 Namespace 的 LBA 格式與 MBR 表內容不相容
    
3. 嘗試以該 Namespace 為目標啟用 MBRControl
    

### Expected Result

1. 系統可能拒絕該啟用請求
    
2. 若被拒絕，系統需回報「MBR 格式不相容」方向的錯誤
    
3. MBRControl 不進入啟用狀態