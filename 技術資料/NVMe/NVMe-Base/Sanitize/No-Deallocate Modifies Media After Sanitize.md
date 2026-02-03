## 概要說明

它定義了控制器在執行 Sanitize 並且 「保留映射」的情況下，所有的物理清除完成後，控制器會不會額外預先寫入合法的資料（例如全 00） + 重新計算正確 ECC 回寫資料到 NAND 區域 。

## 使用情境
當 Sanitize 執行完後會保留映射表，若是主機此時讀取資料，控制器必定會回報 ECC 錯誤（因為物理清除不會重新計算 ECC），若是 NODMMAS=10b 設定預先寫入資，可以讓主機讀取資料時不會發生 ECC 錯誤。

**備註說明：**
此欄位僅在主機發送 Sanitize 指令且設定 No-Deallocate After Sanitize (NDAS) = 1 時才具意義。

**參數定義：**
- 定義於 Identify Controller – Sanitize Capabilities
- Bits 31:30 – No-Deallocate Modifies Media After Sanitize ( NODMMAS )

## NODMMAS 模式說明

- **NODMMAS = 01b ( 不修改 )**    
    - **定義：** 控制器在 Sanitize 過程中，**絕對不會**對媒體( Media ) 進行額外的修改動作。        
    - **行為：** 僅執行物理清除 (如 Block Erase 變全 FF)，**重點是不重寫 ECC**。
          
- **NODMMAS = 10b ( 會修改 )**    
    - **定義：** 控制器會在 Sanitize 過程中，**額外執行修改動作** ( Additionally Modified )。        
    - **行為：** 物理清除後，自動寫入合法的資料樣式 (如全 00) 並計算正確的 ECC。