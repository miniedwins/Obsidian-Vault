
## Sanitize NVM Subsystem Failure Handling

| **失敗狀態 (Failure State)** | **原本設定 (AUSE)** | **唯一的出路 (Recovery)**                                        | **Exit Failure Mode 有效嗎？** | **後果**                         |
| ------------------------ | --------------- | ----------------------------------------------------------- | -------------------------- | ------------------------------ |
| **Restricted Failure**   | **0** (嚴格)      | **必須重跑 Sanitize 直到成功**                                      | **無效**                     | 若硬體壞了無法成功，硬碟永久鎖死 (磚塊化)。        |
| **Unrestricted Failure** | **1** (寬容)      | 1. 重跑 Sanitize<br><br>  <br><br>2. **使用 Exit Failure Mode** | **有效**                     | 可強制回到 Idle，讓硬碟恢復讀寫 (即使資料沒清乾淨)。 |

## Sanitize Namespace Failure Handling

### 核心邏輯總結

- **白名單機制**：只有極少數「必要」的 Admin 指令會被執行（例如：讓你能下第二次 Sanitize 指令來解除錯誤狀態，或者是讀取日誌 Identify 的指令）。
    
- **其餘一律封鎖**：除了白名單以外的所有 Admin 指令，控制器**必須拒絕執行**。
    
- **統一回傳代碼**：在拒絕這些指令時，不能隨便回傳「無效指令」或「一般錯誤」，而必須明確回傳 **`Sanitize Namespace Failed`**。