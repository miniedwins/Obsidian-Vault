## 概要說明

當執行 **Sanitize 命令** 與控制器 Identify 所設定的 **No-Deallocate Inhibited (NDI)** 參數，它們的執行動作有不一致情況發生的時候，控制器會根據 **NODRM** 設定參數決定後續的執行動作。

## 什麼情境下會發生不一致 ?

當主機執行 Sanitize 命令並且**保留映射 (`NDAS=1`)**，代表執行命令完成後，不會進行 **Deallocate logic blocks**。但是 Identify Controller 設定說明不支援 **No-Deallocate Inhibited** (`NDI=1`)， 此時執行 Sanitize 命令會與當前 **NDI** 設定產生了不一致的動作。

因此當執行命令與控制器有沒有支援 **No-Deallocate** 產生不一致的行為的時候，NVMe 設計了一個參數 **NODRM** 來決定這時候該怎麼處理。

> **參數定義：**
> - **NDI：** 位於 Identify Controller (Sanitize Capabilities)。   
> - **NODRM：** 位於 Sanitize Config Command (Dword 11)。

## NODRM 模式說明

- **NODRM = 0 (No-Deallocate Error Response Mode)**    
    - **結果：** SSD 直接拒絕指令，回傳錯誤 **Invalid Field in Command**。
        
- **NADS=1 and NODRM = 1 ( No-Deallocate Warning Response Mode)** 
    - **結果：** SSD 執行 Sanitize 並強制清除映射。        
    - **紀錄：** Sanitize Status Log Page 中標記「Sanitized Unexpected Deallocate」告知主機。

> **參考：**
> - **NDI：** [No-Deallocate Inhibited](No-Deallocate%20Inhibited.md)
> - **NADS：** [No-Deallocate After Sanitize](No-Deallocate%20After%20Sanitize.md)
