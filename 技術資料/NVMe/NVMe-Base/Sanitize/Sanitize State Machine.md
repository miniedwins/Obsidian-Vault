## 概要說明

Sanitize 的運作並非單純的線性流程，而是一個具備「容錯選擇」與「持久性保證」的狀態循環。整個流程核心部分組成：

1. **清除路徑 (Processing Path) :** 選擇哪一個路徑 **Restricted** 或是 **Unrestricted** 進行物理清除。
2. **驗證階段 (Verification)：** (可選) 在物理清除後，並且停留在這個階段，讓主機檢查結果。
3. **收尾階段 (Deallocation)：** 清除邏輯映射 ( Deallocate Logic Block )，確保資料無法被再次存取。
4. **結束階段 (IDLE)：** 整個流程清理完成後 ( 成功或是失敗退出 )，最終需要回到 **IDLE** 階段。

![](assets/Sanitize%20State%20Machine/file-20260114103744498.png)

## 階段運作過程說明

### IDLE State

#### 定義
等待主機發送 Sanitize Command。

#### 進入條件
Sanitize 未執行，或上一次 Sanitize 已完全結束（已處理成功或失敗後的最終狀態）。

### Sanitize Process

這是真正對 NVM 媒體執行物理清除（Block Erase / Crypto Erase / Overwrite）的執行階段。根據主機對 **「完成」** 的要求不同，分為兩種處理路徑 Restricted Processing 以及 Unrestricted Processing。

決定進入哪一條路徑，取決於 Sanitize 命令中的 **`AUSE` (Allow Unrestricted Sanitize Exit)** 設定。這代表了主機對這次清除任務的態度，如下所述：

#### Restricted Processing

#### 定義
安全性的清除，**必須執行到成功為止**，不接受中途放棄。

#### 特性
若途中斷電或重置，控制器重啟後**必須自動恢復**並繼續執行，直到成功才能離開此狀態。

#### 進入條件
SPEC 要求設定 AUSE = 0，表示進入 Restricted Processing。

#### Unrestricted Processing

#### 定義
安全性的清除，若發生意外或失敗，**允許放棄並退出**。

#### 特性
若途中斷電或重置，Sanitize 流程視為 **已取消 (Canceled)**，控制器直接回到 Idle 狀態。 

#### 進入條件
SPEC 要求設定 AUSE = 1，表示進入 Unrestricted Processing。

### Restricted Failure State

#### 定義
當 Sanitize 操作在 **AUSE = 0** 下執行，卻因錯誤（如硬體故障、電源中斷後無法恢復等）導致無法完成時，控制器所進入的保護狀態。

#### 特性
- 為了確保資料安全，此狀態下控制器通常會**拒絕**大部分的 NVM 指令（除了取得 Log 或重新發送 Sanitize 指令外），防止未清除乾淨的資料被存取。

- 無法透過簡單的 Reset 離開。必須重新發送一個合法的 Sanitize 指令（且 AUSE 通常須仍設為 0）並成功執行，才能解除此狀態。

#### 進入條件
- 從 Restricted Processing 進入：物理清除過程中發生失敗。
- 從 Post-Verification Deallocation 進入：Deallocation 階段發生失敗。

### Unrestricted Failure State

#### 定義
當 Sanitize 操作在 **AUSE = 1** 下執行，卻因錯誤導致無法完成時，控制器所進入的狀態。

#### 特性
- 雖然 Sanitize 失敗，主機可以發送 Sanitize 命令 **Exit Failure Mode** 退出狀態。
- 主機可以重新發送 Sanitize 命令，再一次嘗試執行物理清除動作。

#### 進入條件
- 從 Restricted Processing 進入：物理清除過程中發生失敗。
- 從 Post-Verification Deallocation 進入：Deallocation 階段發生失敗。

### Media Verification State

#### 定義
這是 Sanitize 流程中唯一允許主機在資料銷毀後進行鑑識。

當控制器進入 **Media Verification State** 時，它內部的物理清理工作已經結束了。控制器此時的任務，允許主機讀取使用者資料區域（這在 Sanitize Processing 階段是被禁止的）。

這裡說的**允許主機讀取使用者資料區域**，是指主機透過 NVM Read 命令讀取 LBA，控制器在這個階段 不會拋出 **Uncorrectable Error** 錯誤。

##### 為什麼不會拋出錯誤？
需要參考 : [Additional Media Modification](Additional%20Media%20Modification.md)

#### 特性
專門留給主機發送 Read 指令去驗證資料，確認從真實物理 LBA 讀回來的資料，是否符合預期（例如全 00、全 FF，或特定的 Pattern）。

#### 進入條件
主機執行 Sanitize 命令需要設定參數 EMVS = 1，才可以在完物理清理工作完成後進入該狀態。

### Post Verification Deallocation

#### 定義
控制器將所有使用者資料區域執行 Deallocation。

#### 特性
若途中斷電或重置後不會回到 Idle，而是會繼續執行 Deallocation 動作，直到全部完成。

#### 進入條件
- 必須經由 **Media Verification State** 完成後進入。
- 主機發送指令 **Exit Failure Mode** 退出驗證後進入。

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

控制器在此狀態下**嚴格禁止**執行任何「退出失敗 (Exit Failure Mode)」的指令。主機**唯一的出路**，就是發送一個合法的 Sanitize 指令來「重試」，直到清理作業成功為止。

此外，重試時必須嚴格遵守 **AUSE = 0** (Restricted Completion Mode) 的設定。

### 可以執行的命令 (Allowed Commands)

這些是主機可以用來「重試」並試圖修復失敗狀態的手段：

- **Target is Subsystem**    
    - 010b ( Start a Block Erase sanitize operation )        
    - 011b ( Start an Overwrite sanitize operation )        
    - 100b ( Start a Crypto Erase sanitize operation )
        
- **Target is Namespace**    
    - 010b ( Start a Block Erase sanitize operation )        
    - 011b ( Start an Overwrite sanitize operation )        
    - 100b ( Start a Crypto Erase sanitize operation )
        
### 被禁止的命令 (Aborted Commands)

在此狀態下，控制器會拒絕以下指令。請注意 **Target is Subsystem** 與 **Target is Namespace** 回傳的 Status Code 差異：

**1. Target is Subsystem** (全域清理失敗時)

- 001b ( Exit Failure Mode ) : 		
    - Status Code : Sanitize Failed。
        
- 101b ( Exit Media Verification State ) :           
    - Status Code : Invalid Field in Command。
        
- AUSE bit = '1' ( Unrestricted Completion ):            
    - Status Code : Sanitize Failed。
        
**2. Target is Namespace** (單一 Namespace 清理失敗時)

- 001b ( Exit Failure Mode ):            
    - Status Code : Sanitize Namespace Failed。
        
- 101b ( Exit Media Verification State ):           
    - Status Code : Invalid Field in Command。
        
- AUSE bit = '1' ( Unrestricted Completion ):            
    - Status Code : Sanitize Namespace Failed。
        
> **備註 (Note) :** 相比 Unrestricted Failure State 最大的不同在於，**Restricted Failure State 不允許使用 `001b (Exit Failure Mode)`**。
> 
> 唯一的恢復方式 (Failure Recovery) 是發送一個新的 Sanitize Command，並且必須將 **AUSE bit 設定為 '0'** (維持受限模式)，直到資料真正被銷毀成功才能回到 Idle 狀態。

## Unrestricted Failure State

根據規範針對 **Target is a Subsystem or Namespace** 在 **Restricted Failure (受限失敗)** 狀態下的定義，最後真正「可以執行」並且不會被拒絕 ( Abort ) 的命令。其它不可執行的命令，例如 : 101b ( Exit Media Verification State )，則控制器需要回傳狀態碼 ( Sanitize Failed Status Code )。

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

驗證工作主要是由「主機 (Host)」來執行，且必須由主機「手動」下令退出。

### 1. 是由控制器驗證？還是主機端驗證？

- **控制器的角色 (開門者)：** 當控制器進入 **Media Verification State** 時，它內部的清理工作（Block Erase / Overwrite）其實已經結束了。控制器此時的任務是**「解除讀取鎖定」**，允許主機讀取 User Data 區域（這在 Sanitize Processing 階段是被禁止的）。
    
- **主機的角色 (檢查者)：** 這個狀態是專門留給主機 (Host Software / User) 的「檢查時間」。主機可以發送 Read 指令去抽查 LBA，確認讀回來的資料是否符合預期（例如全 00、全 FF，或特定的 Pattern）。
    

**為什麼不是控制器自己驗證就好？** 控制器在 `Restricted Processing` 階段結束前，其實已經做過底層的物理驗證（例如 Check Erase Status）。如果底層物理抹除失敗，它早就跳去 `Restricted Failure` 了。 會設定 `EMVS=1` 進入這個狀態，通常是為了符合某些資安規範（如軍規、政府規範），要求**外部稽核者（主機）** 必須親自確認資料已銷毀。

### 2. 驗證後需不需要手動執行 Exit Media Verification State ?

答案是：**是，絕對需要手動執行。**

一旦您在 Sanitize 指令中設定了 `EMVS = 1` (Enter Media Verification State)，控制器進入此狀態後就會**停在那裡等待**，不會自動跳轉。

- **等待什麼？** 等待主機發送 **Exit Media Verification State (SANACT = 101b)** 的指令。
    
- **流程如下：**
    
    1. 主機讀取資料，確認清理乾淨。
        
    2. 主機發送 `Sanitize Command`，將 `SANACT` 設為 `101b`。
        
    3. 控制器收到指令，狀態機才會離開 `Media Verification State`，轉移到 `Post-Verification Deallocation` 或 `Idle`。
        

**如果您不發送這個指令會怎樣？** 控制器會一直卡在 **Media Verification State**。 在此狀態下，雖然您可以讀取資料，但您無法對 Namespace 進行一般的寫入操作（Write），也無法開始新的 Sanitize（除非是特定允許的重試指令）。硬碟在邏輯上仍處於「Sanitize 尚未完成」的階段。
## Post-Verification State
