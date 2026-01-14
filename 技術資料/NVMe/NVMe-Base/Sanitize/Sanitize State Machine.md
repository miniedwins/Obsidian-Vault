


![](assets/Sanitize%20State%20Machine/file-20260114103744498.png)


## IDLE State

**Exit Failure Mode 是一個「安全」的指令**：

- 如果你已經在 Idle 狀態，你手癢又發了一次「退出失敗模式」，控制器也不會報錯 (Invalid Field)，它會當作沒事發生。

這解釋了為什麼我們一直強調 AUSE=1：

- **如果 AUSE=1**：滿足 (c) 的條件，狀態機能透過「Exit Failure Mode」回到 Idle。
    
- **如果 AUSE=0**：不滿足 (c) 的條件，就算你發送了退出指令，狀態機依然會根據 **Restricted Failure** 的規則把你擋下來，不讓你回到 Idle。

原文 : In this state, all controllers in the NVM subsystem are permitted to resume any power management that was suspended by any prior sanitize operation.

說明 : 當控制器進入到省電模式，若是接收到 Sanitize 命令，控制器必須要等待 Sanitize 運行完畢，直到進入到 Idle；一旦進入 Idle，就必須把省電功能還給系統。

---

### **NVMe Sanitize：Idle State 技術筆記**

**Idle State** 是 NVM 子系統或特定 Namespace 的基礎狀態，代表當前沒有任何清理作業（Sanitize Operation）正在進行。在進入此狀態前，控制器會確保所有的背景媒體銷毀動作已完全停止。

#### **一、 進入 Idle State 的三種路徑**

根據規範 8.1.26.4.1，裝置處於此狀態代表符合以下任一條件：

- **原生狀態：** 自出廠或該 Namespace 建立以來，從未執行過任何 Sanitize 操作。
    
- **成功完工：** 最近一次發起的 Sanitize 操作已圓滿完成（包含擦除與要求的驗證）。
    
- **失敗後強制退出 (僅限 Unrestricted)：** * 上一次操作在「非受限模式」（AUSE 位元設為 '1'）下失敗。
    
    - 主機隨後發送了 **Exit Failure Mode** (SANACT = 001b) 指令，成功讓狀態機從 Unrestricted Failure 轉移至 Idle。
        

#### **二、 操作權限與指令處理**

在 Idle 狀態下，控制器對指令的處理最為寬鬆，確保系統能隨時重新配置：

- **指令不受限：** 主機可以無限制地發送新的 `Sanitize` 或 `Sanitize Namespace` 指令來啟動新的清理任務。
    
- **容錯機制：** 若裝置已處於 Idle 狀態，主機再次發送 `Exit Failure Mode` 指令，控制器**不視為錯誤**，會回傳 Successful Completion。這允許測試腳本將此指令作為「狀態歸零」的安全前置動作。
    

#### **三、 硬體資源與功耗管理**

由於 Sanitize 執行期間需要極高功耗且嚴禁中斷，Idle 狀態是恢復硬體正常運作的分水嶺：

- **恢復省電功能：** 在 Processing 狀態下，控制器會強行暫停（Suspend）所有自動電源管理（如 APST）。**唯有進入 Idle State 後**，控制器才被允許恢復（Resume）這些省電機制。
    
- **熱管理恢復：** 裝置回到 Idle 後，相關的熱管理與功耗限制將回歸正常配置，不再為了維持清理效率而持續處於高功耗狀態。
    

#### **四、 重點摘要 (Key Takeaways)**

1. **AUSE 位元的關鍵：** 只有當初設定 `AUSE=1`，失敗後才有機會透過 `Exit Failure Mode` 回到 Idle；若 `AUSE=0`，失敗後將鎖死在 Restricted Failure，無法直接回到 Idle。
    
2. **狀態機的終點：** 無論是成功、或是從非受限失敗中退出，目標都是回到 Idle，以釋放對一般讀寫指令的攔截限制。
    
3. **效能影響：** Idle 狀態是唯一允許硬體進入深層睡眠（Power State）的 Sanitize 相關狀態。