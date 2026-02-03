## 概要說明

此欄位僅在主機發送 Sanitize 指令且設定 **`No-Deallocate After Sanitize (NDAS) = 1`** 時才具意義。它定義了控制器在「保留映射」的情況下，是否會雞婆地幫你「善後」。

**參數定義：**
- 定義於 Identify Controller – Sanitize Capabilities
- Bits 31:30 – No-Deallocate Modifies Media After Sanitize ( NODMMAS )

## NODMMAS 模式說明

- **NODMMAS = 01b (不修改 / Raw Mode)**    
    - **定義：** 控制器承諾在 Sanitize 過程中，**絕對不會**對媒體進行額外的修改動作。        
    - **行為：** 僅執行物理清除 (如 Block Erase 變全 FF)，不重寫 ECC。        
    - **後果：** 讀取該區域通常會回報 **Media Error** (因 Raw Data 不符 ECC 檢查)。        
    - **意義：** 保留最真實的物理抹除狀態 (適合鑑識)。
        
- **NODMMAS = 10b (會修改 / Safe Mode)**    
    - **定義：** 控制器會在 Sanitize 過程中，**額外執行修改動作** (Additionally Modified)。        
    - **行為：** 物理清除後，自動寫入合法的資料樣式 (如全 00) 並計算正確的 ECC。        
    - **後果：** 讀取該區域會成功回傳 **預設值 (00/FF)**，不會報錯。        
    - **意義：** 防止後續存取遇到資料完整性錯誤 (Integrity Errors)，讓 SSD 可直接使用。