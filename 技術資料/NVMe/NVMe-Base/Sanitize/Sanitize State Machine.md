


![](assets/Sanitize%20State%20Machine/file-20260114103744498.png)


## IDLE State

**Exit Failure Mode 是一個「安全」的指令**：

- 如果你已經在 Idle 狀態，你手癢又發了一次「退出失敗模式」，控制器也不會報錯 (Invalid Field)，它會當作沒事發生。

若裝置已處於 Idle 狀態，主機再次發送 `Exit Failure Mode` 指令，控制器**不視為錯誤**，會回傳 Successful Completion。這允許測試腳本將此指令作為「狀態歸零」的安全前置動作。

**AUSE 位元的關鍵：** 只有當初設定 `AUSE=1`，失敗後才有機會透過 `Exit Failure Mode` 回到 Idle；若 `AUSE=0`，失敗後將鎖死在 Restricted Failure，無法直接回到 Idle。

原文 : In this state, all controllers in the NVM subsystem are permitted to resume any power management that was suspended by any prior sanitize operation.

說明 : 在 Processing 狀態下，控制器會強行暫停（Suspend）所有自動電源管理。**唯有進入 Idle State 後**，控制器才被允許恢復（Resume）這些省電機制。

**Idle State** 是 NVM 子系統或特定 Namespace 的基礎狀態，代表當前沒有任何清理作業（Sanitize Operation）正在進行。在進入此狀態前，控制器會確保所有的背景媒體銷毀動作已完全停止。

**進入 Idle State 的三種路徑**

根據規範 8.1.26.4.1，裝置處於此狀態代表符合以下任一條件：

- **原生狀態：** 自出廠或該 Namespace 建立以來，從未執行過任何 Sanitize 操作。
    
- **成功完工：** 最近一次發起的 Sanitize 操作已圓滿完成（包含擦除與要求的驗證）。
    
- **失敗後強制退出 (僅限 Unrestricted)：** * 上一次操作在「非受限模式」（AUSE 位元設為 '1'）下失敗。
    
    - 主機隨後發送了 **Exit Failure Mode** (SANACT = 001b) 指令，成功讓狀態機從 Unrestricted Failure 轉移至 Idle。


## Media Verification State


## Post-Verification State



