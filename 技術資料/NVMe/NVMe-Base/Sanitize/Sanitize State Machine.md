


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


## Restricted Processing State

### Transition Restricted Processing : Idle

核心摘要：當 Sanitize 作業完成並由 Restricted Processing 轉移至 Idle 狀態時，Sanitize Log Page 的狀態更新取決於「清理的目標範圍 (Sanitization Target)」**。

#### **1. 情境 A：Target is NVM Subsystem**

在此情境下，無論控制器是否支援 `Sanitize Namespace Command`，[Global Data Erased](Global%20Data%20Erased.md) (GDE)位元皆會被設定為 `1`。這表示從 NVM Subsystem 的全域視角來看，所有使用者資料皆已被清除。

- **若不支援 Sanitize Namespace Command：**
    
    - 控制器僅能執行全域清理。
        
    - **結果：** `GDE` 設為 `1`，且 Subsystem 的 `SANS` 回復為 `0h` (Idle)。
        
- **若支援 Sanitize Namespace Command：**
    
    - 雖然支援指定 Namespace 清理，但本次指令是針對「全域」執行。
        
    - **結果：**
        
        1. **全域旗標：** `GDE` 設為 `1`。
            
        2. **個別旗標：** 系統內**所有**存在的 Namespace，其  Namespace Data Erased (NDE) 皆會被聯動設定為 `1`（因為全域被清空，自然包含所有局部）。
            
        3. **狀態復歸：** 全域與所有 Namespace 的 `SANS` 欄位皆回復為 `0h` (Idle)。

#### **2. 情境 B：Target is a Namespace**

在此情境下，僅針對指定的 Namespace 進行狀態更新，不會影響 GDE。

- **結果：**
    
    1. 該特定 Namespace 的 `NDE` 設為 `1`。
        
    2. 該特定 Namespace 的 `SANS` 回復為 `0h` (Idle)。
        
    3. **注意：** 此時 `GDE` 維持不變（除非該動作同時滿足了 GDE 的定義，但通常單一清理不觸發全域旗標）。


## Restricted Failure State



## Unrestricted Failure State

根據規範針對 **Target is a Subsystem or Namespace** 在 **Restricted Failure (受限失敗)** 狀態下的定義，最後真正「可以執行」並且不會被拒絕 ( Abort ) 的命令。其它不可執行的命令，例如 : 101b ( Exit Media Verification State )，則控制器需要回傳錯誤訊息 ( Sanitize Failed Status Code )。

這些規範定義，主要是給主機「重新」再一次進行清理 ( Sanitize ) 或是直接退出 Unrestricted Failure State 回到 Idle 狀態的方法或是手段。

- **Target is Subsystem**
	- 001b ( Exit Failure Mode )
	- 010b ( Start a Block Erase sanitize operation )
	- 011b ( Start an Overwrite sanitize operation )
	- 100b ( Start a Crypto Erase sanitize operation )

- **Target is Namespace**
	- 001b ( Exit Failure Mode )
	- 100b ( Start a Crypto Erase sanitize operation )

>備註 :  只有 Unrestricted Sanitize 發生錯誤進入到 Unrestricted Failure State 狀態下，才可以執行Exit Failure Mode 退出 Unrestricted Failure State。

## Media Verification State


## Post-Verification State
