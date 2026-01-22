
**Sanitize Operation「在不同階段發生 Reset」定義了不同的恢復行為** 

- **NVM Subsystem Reset**（或斷電重開）發生後，控制器在初始化的過程中，會先檢查「上次 Sanitize 做完了沒？」
    
- 如果沒做完，控制器會**強制**讓狀態機重新進入 **Restricted Processing State**（受限處理狀態），直到資料真的清完為止。


**不同階段發生 Reset 的後果**

根據重置發生的時間點，控制器的「繼續執行」方式略有不同：

#### **情境 A：在「清理資料中 (Sanitize Processing)」發生 Reset**

- **狀態：** 您正處於 `Restricted Processing` 狀態，正在擦除 NAND Flash。
    
- **動作：** 發生 Reset。
    
- **恢復行為：**
    
    - 控制器重啟後，發現上次沒做完。
        
    - **立即重新進入** `Restricted Processing` 狀態。
        
    - **繼續執行清理：** 為了確保資安，通常控制器**不會**從「斷掉的那個 LBA」接關，而是**重新執行**當前的清理步驟（例如重新對該 Block 進行 Erase），甚至可能重跑整個 Pass。
        
    - **結論：** **會繼續殺，直到殺完。**
        

#### **情境 B：在「媒體驗證中 (Media Verification)」發生 Reset**

這就是我們上一題討論過的 `MVCNCLD` (Media Verification Canceled) 的來源。

- **狀態：** 資料已經清完了，現在正處於 `Media Verification` 狀態檢查中。
    
- **動作：** 發生 Reset。
    
- **恢復行為：**
    
    - 控制器重啟後，發現「資料其實已經清完了，只是驗證被打斷」。
        
    - 控制器**不會**重新執行驗證（因為驗證通常很花時間，且資料已銷毀）。
        
    - **結果：**
        
        1. 將 `Sanitize Status Log` 中的 **MVCNCLD** 設為 `1` (告知主機：驗證被取消了)。
            
        2. 將狀態機轉移至 **Idle** (結束 Sanitize)。
            
    - **結論：** **不會繼續驗證，而是直接收工 (但會留下紀錄)。**