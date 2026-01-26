## 概要說明

當主機下令 **保留映射 (`NDAS=1`)**，但控制器硬體 **不支援 (`NDI=1`)** 時，會依據 **NODRM** 參數決定後續執行動作 ( 處理或是拒絕 )。主要目的是為了處理 Sanitize 命令與設定有不一致情況發生。

> **參數位置：**
> **NDI :** 位於 Identify Controller (Sanitize Capabilities)。   
> **NODRM :** 位於 Sanitize Config Command (Dword 11)。

## NODRM 模式說明

- **NODRM = 0 (No-Deallocate Error Response Mode)**    
    - **結果：** SSD 直接拒絕指令，回傳錯誤 **Invalid Field in Command**。
        
- **NODRM = 1 ( No-Deallocate Warning Response Mode)** 
    - **結果：** SSD 執行 Sanitize 並強制清除映射。        
    - **紀錄：** Sanitize Status Log Page 中標記「Sanitized Unexpected Deallocate」告知主機。