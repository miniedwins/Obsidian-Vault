# 基本介紹

**Temperature Threshold** 主要目的是用來設定溫度感測器，控製器可以在 **SMART 健康資訊日誌** 中報告**最多九個感測器溫度**，包括一個綜合溫度（Composite Temperature ) 以及八個溫度感測器。對於每個感測器，都會有對應的**過溫閾值**（Over Temperature Threshold）和 **低溫閾值**（Under Temperature Threshold）。

![[temperature_threshold.png]]

當溫度超過或是等於主機端所設定的過溫閾值，或者低於或等於低溫閾值時，SMART 健康資訊日誌中的關鍵警告欄位（Critical Warning field）的第二位會被設定為 **"1"**。這種情況可能會觸發一個**非同步事件**，通知主機發生了溫度異常。

![[smart_health_critical_warning.png]]

控製器必須為 **綜合溫度（Composite Temperature）** 實現過溫閾值功能。

- **Composite Temperature 的閾值實現**:
    - 控製器必須為**綜合溫度（Composite Temperature）**實現**過溫閾值**功能。
    - 如果**Warning Composite Temperature Threshold (WCTEMP)** 欄位報告了非零值，則還必須為 Composite Temperature 實現**低溫閾值**功能。
- **各感測器的閾值實現**:
    - 對於所有有效的溫度感測器（即那些報告了非零值的感測器），都需要實現相應的過溫和低溫閾值功能。
- **默認閾值**:
    - Composite Temperature 的**過溫閾值**預設值是 **WCTEMP** 欄位的值（如果 **WCTEMP** 為非零）。如果 **WCTEMP** 為零，過溫閾值的預設值是**具體實現決定**的。
    - Composite Temperature 的**低溫閾值**預設值也是**具體實現決定**的。
    - 所有實現的溫度感測器的默認**過溫閾值**為 **FFFFh**（表示極高的閾值，通常不會觸發警告），默認**低溫閾值**為 **0h**

# 執行命令操作

## 檢查感測器溫度設定


## 設定綜合溫度


