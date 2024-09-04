# HCTM 介紹

控制器提供主機端一個溫度設定機制 **( HCTM )**，讓主機端 ( Host ) 可以通過特定的組態設定不同階段的熱管理 **( TMT1 and TMT2 )**，當控製器達到設定溫度的閥值執行特定熱管理動作。這些操作的目標主要是幫助裝置在運行過程中保持在主機指定的熱管理範圍內。

> **供應商特定的熱管理動作** : 除了切換電源狀態，控製器還可能執行一些由供應商定義的特定操作，這些操作可能與裝置的散熱機制、CPU 速度控制等相關，旨在更好地管理裝置的溫度。

下圖為 HCTM 範例，分別描述 TMT1 以及 TMT2 的關係。若是當前 Composite Temperature 達到符合HCTM 溫度設定，控制器會開始轉換到 `Low Power Active States` 並且執行 Vendor 所指定的 `Thermal Management Actions`。




![[hctm_example.png]]

那麼要如何設定 `TMT1` 以及 `TMT2` 溫度閥值 ? 如下圖所示，主機端是透過 Set-Feature ( HCTM ) 命令設定溫度。定義克耳文 ( Kelvin ) 是計量溫度的單位，但是我們使用的計量單位是攝氏 ( Celsius )，因此設定時需要對溫度做單位轉換。

> 克耳文  ( Kelvin ) = 攝氏溫度 ( Celsius ) + 273

另外若是溫度設定不當，控制器則會回覆主機端錯誤訊息 ( Invalid Field in Command )。

- **設定溫度規則 :** 
	- TMT1 < TMT2 
	- TMT2 > TMT1
- **錯誤範例設定 :** 
	- TMT2=80 若是設定 TMT1=85
	- TMT1=70 若是設定 TMT2=65 

![[host_controlled_thermal_management.png]]

另外值得要注意的是，`TMT1` 以及 `TMT2` 溫度閥值是有範圍限定，我們可以透過 `Identify Ctrl` 資料結構表取得最小與最大溫度的設定值 **( MNTMT and MXTMT )**，當設定溫度超過所表示的範圍，控制器則會拒絕該命令請求，並且回覆主機端錯誤訊息 ( Invalid Field in Command )。

![[MNTMT_MXTMT.png]]

# 檢查是否支援 HCTM

**主機控制的熱管理支援** : 控製器是否支援 HCTM， 是由控製器 `Identify Ctrl` 結構中的 `HCTMA` 欄位表示。如果支援，代表控製器可以響應主機的熱管理請求命令。

- HCTM ( Host Controlled Thermal Management Attributes )
	- Bit 0 : 1 ( Support )
	- Bit 0 : 0 ( Not Supported )
	- Bit 1-15  ( Reserved )

![[HCTM.png]]
# 如何設定 HCTM 溫度




