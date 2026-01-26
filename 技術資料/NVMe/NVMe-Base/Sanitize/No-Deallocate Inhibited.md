## 概要說明
**NDI ( No-Deallocate Inhibited )** 
表示當執行 Sanitize 命令完成後，控制器是否 **禁止或是啟用** No-Deallocate。

**No-Deallocate Inhibited：**
- **NDI = 0：** 支援保留映射 (Supports No-Deallocate)。    
- **NDI = 1：** 禁止保留映射 (Inhibits/Can't do it)。

**參數定義：**
- 定義於  Identify Controller ( Sanitize Capabilities )。