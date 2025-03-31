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