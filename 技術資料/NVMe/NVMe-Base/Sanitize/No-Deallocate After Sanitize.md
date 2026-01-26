## 概要說明
**NADS ( No-Deallocate After Sanitize )**
主機發出 **Sanitize (NADS=1)** 命令完成後，要求控制器不要進行 **Deallocate Logic Blocks**。

**No-Deallocate After Sanitize：**
- **NADS = 0：** 執行 Sanitize 完成後，進行 Deallocate logic blocks。
- **NADS = 1：** 執行 Sanitize 完成後，不進行 Deallocate logic blocks。

**參數定義：**
- 位於 Sanitize – Command Dword 10
- Bits9 : No-Deallocate After Sanitize ( NDAS )

**備註說明：**
- 此參數設定會根據 `NDI=1` 以及 `NODRM=0/1` 相關設定有連動關係，產生不一樣的結果。
- 詳細說明需要參考 **NODRM**。

> **參考：**
> **NDI：** [No-Deallocate Inhibited](No-Deallocate%20Inhibited.md)    
> **NODRM：** **[No-Deallocate Response Mode](No-Deallocate%20Response%20Mode.md)
 