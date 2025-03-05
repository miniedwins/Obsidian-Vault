# 概要說明
`Temperature Threshold` 主要目的是用來設定溫度感測器，控製器可以在 **SMART 健康資訊日誌** 中報告**最多九個感測器溫度**，包括一個綜合溫度（Composite Temperature ) 以及八個溫度感測器。對於每個感測器，都會有對應的**過溫閾值**（Over Temperature Threshold）和 **低溫閾值**（Under Temperature Threshold）。

![[temperature_threshold.png]]

當溫度超過或是等於主機端所設定的**過溫閾值**，或者低於或等於**低溫閾值**時，SMART 健康資訊日誌中的關鍵警告欄位（Critical Warning field）的第二位會被設定為 **"1"**。這種情況可能會觸發一個**非同步事件**，通知主機發生了溫度異常。

![[smart_health_critical_warning.png]]

控製器必須為 **綜合溫度（Composite Temperature）** 實現**過溫閾值**（Over Temperature Threshold）和 **低溫閾值（Under Temperature Threshold）**。它的預設值，可以透過 `Identify Ctrl` 結構表找到 `WCTEMP` 以及 `CCTEMP`。

另外對於有效的溫度感測器（即那些報告了非零值的感測器），都需要實現相應的過溫和低溫閾值功能。所有實現的溫度感測器的預設**過溫閾值**為 **FFFFh**，默認**低溫閾值**為 **0h**。

> **待確認 : 若是沒有實現溫度感測器，SMART 健康資訊日誌應該要多少 ?**
> 1. 沒有實現溫度感測器，若是設定溫度感測器1，則命令無效
> 2. NVMe-CLI SMART 日誌不會顯示，那是因為預設 0xFFFF 的關係嗎 

![[composite_termperature_threshold.png]]

# 執行命令操作
## 取得當前綜合溫度
首先可以檢查感測器預設溫度，**WCTEMP** 為當前預設 Over Temperature Threshold。

```shell
$ nvme id-ctrl /dev/nvme0 -H 
NVME Identify Controller:
vid       : 0x1bcd
ssvid     : 0x1bcd
sn        : 122020404029        
mn        : 480GB PCIe Drive                        
fr        : PNPP2D2A
...
...
wctemp    : 357
 [15:0] : 84 °C (357 K)	Warning Composite Temperature Threshold (WCTEMP)

cctemp    : 362
 [15:0] : 89 °C (362 K)	Critical Composite Temperature Threshold (CCTEMP)
```

以下 **NVMe-CLI** 命令會幫我們直接取得 **綜合溫度（Composite Temperature )**。在這裡我們可以看到 Over Temperature Threshold 會對應到 **WCTEMP** 所表示的溫度相同。

```shell
$ nvme get-feature -f 0x4 /dev/nvme0 -H
get-feature:0x04 (Temperature Threshold), Current value:0x00000165
	Threshold Type Select         (THSEL): 0 - Over Temperature Threshold
	Threshold Temperature Select (TMPSEL): 0 - Composite Temperature
	Temperature Threshold         (TMPTH): 84 °C (357 K)
```

## 設定綜合溫度
例如 : 若是想要過溫閾值為 50°C，因此需要設定 THSEL= 00 以及 TMPTH = 0x012f

- `THSEL` : 選擇設定 Temperature Threshold 
	- 00 : Over
	- 01 : Under
- `TMPTH` : 設定溫度閾值 ( 單位 : Kelvins )

```shell
$ nvme set-feature -f 0x04 --value=0x00000143 /dev/nvme0
set-feature:0x04 (Temperature Threshold), value:0x00000143, cdw12:00000000, save:0
```

設定完成後，可以透過 `Get-Feature` 取得當前溫度閥值是否被更改

```shell
$ nvme get-feature -f 0x04 /dev/nvme0 -H
get-feature:0x04 (Temperature Threshold), Current value:0x00000143
	Threshold Type Select         (THSEL): 0 - Over Temperature Threshold
	Threshold Temperature Select (TMPSEL): 0 - Composite Temperature
	Temperature Threshold         (TMPTH): 50 °C (323 K)
```
