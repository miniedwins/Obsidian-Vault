# HCTM

## 基本介紹

控制器提供主機端一個熱管理設定機制 **( HCTM )**，讓主機端 ( Host ) 可以通過特定的組態設定不同階段的熱管理 **( TMT1 and TMT2 )**，當控製器達到設定溫度的閥值時，執行特定熱管理動作。

- **這些操作的目標主要是**
	- 降低性能以減少熱量的產生，從而保護裝置和資料的安全。
	- 當溫度回到安全範圍內，控製器停止這些功率限制或熱管理措施，恢復正常的高性能運行狀態。

> **供應商特定的熱管理動作** : 除了切換電源狀態，控製器還可能執行一些由供應商定義的特定操作，這些操作可能與裝置的散熱機制、CPU 速度控制等相關，旨在更好地管理裝置的溫度。

## 何謂 TMT1 以及 TMT2 ?

TM ( Thermal Management Temperature )** 它是一個就是 `Set-Feature` 命令，主機端可以透過該命令方式來設定溫度的閥值，共可以設定 TMT1 ( Light Throttle ) 以及 TMT2 ( Heavy Throttle )。當控制器達到主機端所設定的溫度時，就會開始啟動熱管理機制。

下圖為 **HCTM** 範例，分別描述 **TMT1 以及 TMT2 之間的關係**。若是當前 Composite Temperature 達到符合 HCTM 溫度設定，控制器會開始轉換到 `Low Power Active States` 並且執行廠商所指定的 `Thermal Management Actions` 也就是熱管理動作。

- **Light Throttle**（溫度在 TMT1 和 TMT2 之間）：控製器會進入低功耗模式，降低性能以控制溫度。當溫度下降到 TMT1 以下時，控製器恢復正常運行。
    
- **Heavy Throttle**（溫度超過 TMT2）：控製器可能會採取更強的限制措施，如進一步降低頻率。當溫度下降到 TMT1 以下時，停止所有限制動作，控製器恢復正常狀態。

![[hctm_example.png]]

那麼要如何設定 `TMT1` 以及 `TMT2` 溫度閥值 ? 如下圖所示，主機端是透過 **Set-Feature ( HCTM )** 命令設定溫度。不過要注意的是計量溫度的單位是 **克耳文 ( Kelvin )**，但是我們使用的計量單位是**攝氏 ( Celsius )**，因此設定時需要對溫度做單位轉換。

> 克耳文  ( Kelvin ) = 攝氏溫度 ( Celsius ) + 273

若是溫度設定不當，控制器會回覆主機端錯誤訊息 ( Invalid Field in Command )。

- **設定溫度規則 :** 
	- TMT1 < TMT2 
	- TMT2 > TMT1
- **錯誤範例設定 :** 
	- 當前 TMT2 = 80 若是設定 TMT1 = 85
	- 當前 TMT1 = 70 若是設定 TMT2 = 65 

![[host_controlled_thermal_management.png]]

另外值得要注意的是，`TMT1` 以及 `TMT2` 溫度閥值是有限定值，我們可以透過 `Identify Ctrl` 資料結構表取得最小與最大溫度的設定值 **( MNTMT and MXTMT )**，當設定溫度超過所表示的限定值，控制器則會拒絕該命令請求，並且回覆主機端錯誤訊息 ( Invalid Field in Command )。

![[thermal_management_termperature.png]]

# 執行命令與操作
## 檢查是否支援 HCTM

**主機控制的熱管理支援** : 控製器是否支援 HCTM，可以從結構表 `Identify Ctrl` 獲得 `HCTMA` 欄位。如果支援，代表控製器可以響應主機的熱管理請求命令。

- HCTMA ( Host Controlled Thermal Management Attributes )
	- Bit 0 : 1 ( Support )
	- Bit 0 : 0 ( Not Supported )
	- Bit 1-15  ( Reserved )

![[host_ctrl_thermal_management_attrs.png]]

從命令回報的結果得知 HCTMA = 1 ，代表控制器有支援 HCTM。

```shell
$ nvme id-ctrl /dev/nvme0 -H | grep hctma
hctma     : 0x1
```
## 查看當前 HCTM 設定

主機端可以透過 Get-Feature ( HCTM ) 取得當前 TMT1 以及 TMT2 溫度設定的狀態。

```shell
$ nvme get-feature -f 0x10 /dev/nvme0 -H
get-feature:0x10 (Host Controlled Thermal Management), Current value:0x015d0160
		Thermal Management Temperature 1 (TMT1) : 349 K (76 °C)
		Thermal Management Temperature 2 (TMT2) : 352 K (79 °C)
```
## 設定 HCTM 溫度

首先取得當前 HCTM 所設定的溫度，可以得知 TMT1=76 °C 以及 TMT2=79 °C。

```shell
$ nvme get-feature -f 0x10 /dev/nvme0 -H
get-feature:0x10 (Host Controlled Thermal Management), Current value:0x015d0160
		Thermal Management Temperature 1 (TMT1) : 349 K (76 °C)
		Thermal Management Temperature 2 (TMT2) : 352 K (79 °C)
```

接下來我們想要將 TMT1 設定 60 °C，在稍微有一點的溫度下觸發熱管理機制。

```shell
$ nvme set-feature -f 0x10 --value=0x014d0160 /dev/nvme0
set-feature:0x10 (Host Controlled Thermal Management), value=0x014d0160, cdw12:00000000, save:0
```

然後再重新取得 HCTM 設定的溫度，可以發現當前的 TMT1 溫度已經變成 60 °C

```shell
$ nvme get-feature -f 0x10 /dev/nvme0 -H
get-feature:0x10 (Host Controlled Thermal Management), Current value:0x015d0160
		Thermal Management Temperature 1 (TMT1) : 349 K (60 °C)
		Thermal Management Temperature 2 (TMT2) : 352 K (79 °C)
```

若是 HCTM 設定溫度不符合規則，例如 : TMT1=0x0142 以及 TMT2=0x0140

當設定 TMT1=85 °C  大於 TMT2=83 °C 觸發熱管理的動作不符合定義，因此發生錯誤。

```
$ nvme set-feature -f 0x10 --value=0x1420140 /dev/nvme0
NVMe status: Invalid Field in Command: A reserved coded value or an unsupported value in a defined field (0x2002)
```

另外需要考慮到控制器支援溫度的上下限 **( MNTMT & MXTMT )**，當設定超過限定的範圍，控制器也是會回覆錯誤訊息。

例如 : TMT1=76 °C  以及  TMT2=80 °C，首先透過 `Identify Ctrl` 取得結構表，得知當前可設定最小與最大溫度的值是 MNTMT= 40°C  以及 MXTMT= 79°C。

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
mntmt     : 313
 [15:0] : 40 °C (313 K)	Minimum Thermal Management Temperature (MNTMT)

mxtmt     : 352
 [15:0] : 79 °C (352 K)	Maximum Thermal Management Temperature (MXTMT)

```

雖然 TMT1 設定符合規則，但是 TMT2 已經超過限定範圍，因此主機端發出的命令請求會發生錯誤。

```shell
$ sudo nvme set-feature -f 0x10 --value=0x015d0161 /dev/nvme0
NVMe status: Invalid Field in Command: A reserved coded value or an unsupported value in a defined field (0x2002)
```



