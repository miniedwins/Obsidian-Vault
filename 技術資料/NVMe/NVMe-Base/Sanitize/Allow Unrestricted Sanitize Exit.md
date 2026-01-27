## 概要說明

**AUSE ( Allow Unrestricted Sanitize Exit )**
決定 Sanitize Processing (物理清除) 階段，是否可以中途放棄清理。

**Allow Unrestricted Sanitize Exit：**
- **AUSE = 0：** 進入 **Restricted Processing** 狀態。一旦開始，除非成功，否則無法退出。
- **AUSE = 1：** 進入 **Unrestricted Processing** 狀態。允許中途放棄或被 Reset 中斷。

**AUSE 位元關鍵說明：** 
- `AUSE=0`，失敗後將鎖死在 **Restricted Failure Mode**，無法直接回到 Idle。
- `AUSE=1`，失敗後才有機會透過 Sanitize 命令發送 **Exit Failure Mode** 回到 Idle；

**參數定義：**
- 位於 Sanitize – Command Dword 10
- Bits3 : Allow Unrestricted Sanitize Exit ( AUSE )

**備註說明：**
- **有效時機：** `SANACT` 設定為以下三種 Start 指令之一時：
    - `010b` (Block Erase)    
    - `011b` (Crypto Erase)        
    - `100b` (Overwrite)        
- **無效時機 (Ignored)：**    
    - 若 `SANACT` 是其他值 (如 Exit Failure, Exit Media Verification 等)，控制器將**忽略** AUSE 位元。

> **參考 :** 
> **EMVS：[Exit Failure Mode](Exit%20Failure%20Mode.md)