#### **1. 核心概念：什麼是 Additional Media Modification？**

- **定義：** 當 Sanitize (如 Block Erase) 完成後，控制器自動將被抹除的區域重新寫入合法的資料樣式（如全 00 加上正確的 ECC）。
    
- **目的：** 為了讓主機在設定 **No-Deallocate (保留映射)** 時，讀取該區域**不會**因為 ECC Error 而報錯，能順利讀到資料。
    
- **代價：** 破壞了物理抹除的原始痕跡（覆蓋了案發現場），導致無法進行數位鑑識。
    

#### **2. 觸發執行的「黃金三條件」**

根據 NVMe 規範，控制器**只有在同時滿足**以下三個條件時，才會執行 Additional Media Modification。缺一不可。

1. **能力支援 (Capability):**
    
    - Identify Controller 中的 `SANICAP (NODMMAS)` 欄位必須是 **10b**。
        
    - (代表：控制器支援且預設會執行修改)。
        
2. **保留映射 (No-Deallocate):**
    
    - Sanitize 指令中的 `NDAS` (No-Deallocate After Sanitize) bit 必須設為 **1**。
        
    - (代表：主機要求保留 LBA 映射)。
        
3. **不進入驗證 (No Verification):**
    
    - Sanitize 指令中的 `EMVS` (Enter Media Verification State) bit 必須是 **0**。
        
    - **(關鍵點：這就是開關)**。

|**情境**|**設定組合**|**控制器行為**|**結果與意義**|
|---|---|---|---|
|情境 A：<br><br>  <br><br>一般讀取需求|• SANICAP = 10b<br><br>  <br><br>• NDAS = 1<br><br>  <br><br>• **EMVS = 0**|**執行修改 (Modify)**<br><br>  <br><br>寫入合法的 00 與 ECC。|**✅ 讀取成功 (00)**<br><br>  <br><br>主機可順利讀取不報錯，但無法證明是否真的執行過 Block Erase (證據被覆蓋)。|
|情境 B：<br><br>  <br><br>數位鑑識需求|• SANICAP = 10b<br><br>  <br><br>• NDAS = 1<br><br>  <br><br>• **EMVS = 1**|**不執行修改 (Skip)**<br><br>  <br><br>保留物理抹除後的原始狀態 (Raw)。|**✅ 進入 Media Verification State**<br><br>  <br><br>雖然 ECC 是錯的，但驗證模式允許讀取原始資料 (Raw FF)，讓主機親眼確認物理抹除的結果。|