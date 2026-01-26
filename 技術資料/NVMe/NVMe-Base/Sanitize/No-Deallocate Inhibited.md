## 概要說明
**NDI (No-Deallocate Inhibited)** 表示當執行 Sanitize 命令完成後，控制器是否禁止 No-Deallocate。

**定義：** 控制器是否禁止 No-Deallocate。
- NDI = 0 : 支援保留映射 (Supports No-Deallocate)。    
- NDI = 1 : 禁止保留映射 (Inhibits/Can't do it)。

> **參數位置：**
> **NDI :** 位於 Identify Controller (Sanitize Capabilities)。   