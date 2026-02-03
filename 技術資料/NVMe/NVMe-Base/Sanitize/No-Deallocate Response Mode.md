## 概要說明

當執行 **Sanitize 命令** 與控制器 Identify 所設定的 **No-Deallocate Inhibited (NDI)** 參數，它們的執行動作有衝突的情況發生，控制器會根據 **NODRM** 設定參數決定後續的執行動作。

## NODRM 使用情境

當主機執行 Sanitize 命令並且**保留映射 (`NDAS=1`)**，代表執行命令完成後，不會進行 **Deallocate logic blocks**。但是當前的 Identify Controller 可能會設定 **不支援No-Deallocate** (`NDI=1`)，若是執行 Sanitize 命令並且保留映射，就會與當前 **NDI** 的設定產生執行上的衝突。

為了解決是否要進行 `Deallocate` 或是 `No-Deallocate`，因此 NVMe SPEC 設計了一個參數 **NODRM** 來決定控制器這個時候該怎麼處理。

> **參數定義：**
> - **NDI ：** 位於 Identify Controller (Sanitize Capabilities)。   
> - **NODRM ：** 位於 Sanitize Config Command (Dword 11)。

## NODRM 模式說明

- **NODRM = 0 (No-Deallocate Error Response Mode)**    
    - **結果 ：** SSD 直接拒絕指令，回傳錯誤 **Invalid Field in Command**。
        
- **NADS=1 and NODRM = 1 ( No-Deallocate Warning Response Mode)** 
    - **結果 ：** SSD 執行 Sanitize 並強制清除映射。        
    - **紀錄 ：** Sanitize Status Log Page 中標記「Sanitized Unexpected Deallocate」告知主機。

> **參考：**
> - **NDI ：** [No-Deallocate Inhibited](No-Deallocate%20Inhibited.md)
> - **NADS ：** [No-Deallocate After Sanitize](No-Deallocate%20After%20Sanitize.md)
