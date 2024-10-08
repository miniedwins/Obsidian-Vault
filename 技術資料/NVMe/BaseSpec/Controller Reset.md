# Controller Reset

## 介紹說明

**控製器復位**（Controller Reset）是一個特殊的復位類型，雖然它屬於控製器級復位，就是說只會**復位控制器屬性**，除了某些部份屬性無法被復位。但在這種情況下，PCI 暫存器空間可能不會像其他復位操作那樣被重設。

常規復位（Conventional Reset）和功能級復位（Function Level Reset, FLR）是根據 PCI Express 規範定義的復位方法，都會觸發 NVMe 控製器級復位（Controller Reset）
* [[Conventional Reset]]
* [[Function Level Reset]]
## 多個不同的復位說明

