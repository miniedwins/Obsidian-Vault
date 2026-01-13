## 1. 什麼是 Deallocated / Unwritten Logical Block

從未被寫過的邏輯區塊 (unwritten logical lock)，對主機而言就是一個乾淨的邏輯區塊該定義可以被稱為  deallocated / unwritten Logic Block。一旦該 LBA 被寫入下控制器就不再視為 deallocated。

若是要將已寫過的邏輯區塊被收回收 ( TRIM )，需要使用已下命令 :
- Dataset Management
- Write Zeroes
- Sanitize

---
## 2. 讀取行為由 Error Recovery Feature 決定

Host 可透過 **Error Recovery feature** 控制讀取這類 LBA 時的行為。
關鍵控制位元：
- **DULBE (Deallocated or Unwritten Logical Block Error Enable)**
    
### DULBE = 1（啟用錯誤）

當 DULBE 設為 1 時：

- 若以下指令存取到 deallocated / unwritten block，**必須中止並回傳錯誤**：
    
    - Copy
        
    - Read
        
    - Verify
        
    - Compare
        
- 回傳狀態碼：
    
    - **Deallocated or Unwritten Logical Block**
        

---

### DULBE = 0（不啟用錯誤）

若未啟用錯誤，controller **仍可回傳資料**，但資料內容由 **DRB** 決定。

DRB（Deallocation Read Behavior）設定

| DRB 值  | 回傳資料內容                         |
| ------ | ------------------------------ |
| `001b` | 所有 byte = `00h`                |
| `010b` | 所有 byte = `FFh`                |
| `000b` | `00h` 或 `FFh`（controller 自行決定） |

---

## 5. 回傳資料的特性（重要）

- 回傳的資料必須是 **deterministic**   

    - 同一個 deallocated LBA        
    - 在被重新寫入前        
    - 每次讀取結果都必須一樣
        
- 一旦該 LBA 被寫入：
    
    - 就不再視為 deallocated / unwritten
        
- Read / Verify 指令：
    
    - 不會改變 deallocation 狀態
        

---

## 6. Protection Information（PI）欄位行為

對於 deallocated / unwritten logical block：

#### Guard Field

- 每個 byte 必須：
    
    - 設為 `FFh`，或
        
    - 設為對「回傳資料內容」計算出的 CRC  
        （例如資料全為 `00h`，則 CRC 對應 `00h`）
        

#### 其他 PI 欄位

以下欄位全部設為 `FFh`（表示不檢查 PI）：

- Storage Tag（若有定義）
    
- Application Tag
    
- Logical Block Reference Tag
    

---

### 一句話總結

> Deallocated / Unwritten LBA 它會根據（DULBE=1）直接回報錯誤，或是（DULBE=0）回傳固定的值 00h / FFh，而且 Logical Block 在被重新寫入前，回傳內容必須一致。