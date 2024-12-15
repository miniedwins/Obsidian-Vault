# Controller Reset

## 概要說明

* 專門針對 NVMe 控製器本身的重置，執行復位時控製器會重啟，但不會重設某些持久屬性。
* **控製器復位不會影響與傳輸相關的設定。**
## 如何觸發控制器重置

NVMe 規範中說明只要將 `CC.EN=1` 設定成 `CC.EN=0`，即是觸發 `Controller Reset`。
## 解釋不同於 Controller Level Reset

 控制器重置 ( Controller Reset ) 與控製器級重置 ( Controller Level Reset ) 不同 : 
 
* 當執行控製器級重置時，重置操作會影響整個控製器及其相關功能。
* 主機端與控制器之間的**通訊協議**，會根據PCIe規範被重設。
## 總結說明

先執行 `Controller Reset` 然後重置的範圍再擴大到 `Controller Level Reset`。也就證明為什麼 **Controller Level Reset 觸發條件會是 Controller Reset**。
