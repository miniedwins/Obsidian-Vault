# TCG Opal/Enterprise 儲存安全中的 GlobalRange 與資料加密機制

## 1. GlobalRange 的金鑰機制

**是的，GlobalRange 確實會有一把加密金鑰**，這是 TCG 儲存安全架構的核心設計：

- 所有 Locking Range (包括 GlobalRange) 都關聯到獨立的加密金鑰
    
- **GlobalRange Key 特性**：
    
    - 預設涵蓋整個儲存媒體的邏輯位址空間
        
    - 作為其他 Locking Range 的「父範圍」(當其他範圍未定義時，會繼承 GlobalRange 的存取控制)
        
    - 在 Enterprise SSC 中可能與媒體加密金鑰(MEK)綁定
        
    - 金鑰由控制器的安全處理器管理，不會以明文形式暴露給主機
        
- **金鑰層級範例**：
    
    mermaid
    
    复制
    
    graph TD
      A[Media Encryption Key] --> B(GlobalRange Key)
      B --> C[LockingRange1 Key]
      B --> D[LockingRange2 Key]
    

## 2. 資料寫入時的加密行為

**寫入資料是否會被加密取決於以下條件**：

### 對於支持硬件加密的 SED (Self-Encrypting Drive)：

- **必定會加密寫入**：
    
    - 所有數據在寫入媒體物理層前會自動加密
        
    - 使用 GlobalRange 或相應 Locking Range 的金鑰加密
        
    - 加密過程在控制器硬件中完成，對主機完全透明
        
- **加密流程**：
    
    mermaid
    
    复制
    
    sequenceDiagram
      主機->>控制器: 傳送明文數據
      控制器->>加密引擎: 使用範圍金鑰加密
      加密引擎->>媒體: 寫入密文
    

### 對於非加密型 Locking Range 實現：

- **僅存取控制**：
    
    - 某些低成本實現可能只做存取阻斷
        
    - 數據以明文存儲，但讀取時會檢查 Locking Range 狀態
        
    - 不符合 TCG 完整規範，屬於非標準實現
        

### 企業級設備的特殊情況：

- **多重加密層**：
    
    - 可能同時應用媒體級加密(MEK)和邏輯範圍加密
        
    - 例如：GlobalRange 使用 AES-256 媒體加密 + LockingRange 使用額外的 XTS-AES 加密
        

## 實際應用驗證方法

若要確認您的設備實際行為：

1. 檢查 **IDENTIFY** 命令回應：
    
    - 確認 `Trusted Computing Feature Set` 標誌
        
    - 查看 `Encryption Mode` 參數
        
2. 使用 **PSID Rever**t 測試：
    
    bash
    
    复制
    
    # 範例指令(實際指令依廠商而異)
    sedutil-cli --psidRevert /dev/sdX
    
    若執行後數據不可讀，則證明存在硬件加密
    
3. 查看 **SMART 數據**：
    
    bash
    
    复制
    
    smartctl -g security /dev/sdX
    

## 安全建議

1. 對於敏感數據：
    
    - 優先選擇標明「TCG Opal 2.0」或「Enterprise SSC」認證的設備
        
    - 確認規格中包含「Full Disk Encryption」或「Instant Secure Erase」特性
        
2. 部署後驗證：
    
    bash
    
    复制
    
    # 檢查加密狀態(Linux範例)
    cryptsetup status /dev/sdX
    
3. 金鑰管理：
    
    - 初始化時務必變更預設 MSID
        
    - 對不同 Locking Range 使用獨立金鑰
        
    - 啟用「Crypto Erase」而非傳統格式化
        

這種設計確保即使物理媒體被移出設備，沒有正確的金鑰也無法解讀數據，符合現代資料安全保護要求。


============================================================

## OPAL/Locking SP 的 Key 模型

- **Global Range**
    
    - 一開始整顆 disk 的加密是由 **Global Key (K_global)** 負責。
        
    - 沒有定義的範圍 (或不受 Locking Range 控制的範圍)，都用 Global Key。
        
- **Locking Range N**
    
    - 每一個 Locking Range 會有一把獨立的 AES Key (K_rangeN)。
        
    - 當該 Range 被「啟用 (Active)」並「上鎖 (Locked)」時，是否能存取要透過授權判斷。
        
    - 如果某個 Range 被 **Disable** 或 **Unlocked**，那麼任何人都可以存取這個 Range 的資料。
        

---

## ⚡ 你的問題：「Disable / Unlocked 的 Range 會用哪把 Key？」

- **即使 Range 被 Disable 或 Unlocked**，它的資料 **仍然使用該 Range 原本的 K_rangeN 來加解密**。
    
    - 因為「加解密用哪把 Key」是由 **LBA 所屬的 Range** 決定的，不是由存取控制決定的。
        
    - Lock/Unlock/Disable 只是決定「誰能不能訪問」，而不是決定「換不換 Key」。
        
- **沒有被任何 Range 覆蓋的 LBA** → 使用 **K_global**。
    

---

## 📌 例子

假設：

- Global Key = K_global
    
- Range1 (LBA 0x100–0x2FF) → K_range1
    

### Case A：Range1 = Enabled + Locked

- User 沒授權 → 無法讀寫 (I/O blocked)
    
- 有授權 → 能讀寫，但資料仍然是用 K_range1 加解密
    

### Case B：Range1 = Enabled + Unlocked

- 任何人都能讀寫
    
- 但加解密 **還是使用 K_range1**
    
- 所以資料內容跟 Global Key 管轄的區域不同
    

### Case C：Range1 = Disabled

- 等同於沒有這個 Range
    
- **回歸 Global Key (K_global)** → 再讀時，資料會 mismatch，因為它本來是用 K_range1 寫的
    

---

## 🧭 關鍵差異

- **Unlocked**：資料仍然用 Range 的 Key，但不再有存取限制。
    
- **Disabled**：Range 被移除，這段 LBA 回到 Global Key 的控制 → 如果之前用 Range Key 寫的資料，現在會亂碼。
    

---

✅ 所以回答你的疑問：

- **Range Unlocked → 還是用原本的 Range Key**。
    
- **Range Disabled → 改用 Global Key，舊資料就讀不對了**。