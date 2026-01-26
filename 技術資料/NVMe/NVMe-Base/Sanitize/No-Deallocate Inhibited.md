## 概要說明
**NDI ( No-Deallocate Inhibited )** 
表示當執行 Sanitize 命令完成後，控制器是否 **禁止或是啟用** No-Deallocate。

**No-Deallocate Inhibited：**
- **NDI = 0：** 支援保留映射 (Supports No-Deallocate)。    
- **NDI = 1：** 禁止保留映射 (Inhibits/Can't do it)。

**參數定義：**
- 定義於  Identify Controller ( Sanitize Capabilities )。

**備註說明：**
- **NDI** 設定會根據 `NADS=1` 以及 `NODRM=0/1` 相關設定有連動關係，產生不一樣的結果。
- 詳細說明需要參考 **NODRM**。

> **參考：** 
> **NDAS：**[No-Deallocate After Sanitize](No-Deallocate%20After%20Sanitize.md)
> **NODRM：**[No-Deallocate Response Mode](No-Deallocate%20Response%20Mode.md)