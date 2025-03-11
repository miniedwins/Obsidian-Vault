## 概要說明
Autonomous Power State Transitions（APST）是 NVMe 提供的一種自動省電機制，主要目的是當 SSD 閒置一段時間後，自動降低功耗，提高能源效率。如果 SSD 持續閒置超過「設定的閒置時間」，它會自動進入較低的電源狀態 [[Non-Operational Power States]]。

## 省電機制
控制器基於這兩個參數 [[#Idle Time Prior to Transition（ITPT）|ITPT]] 以及 [[#Idle Transition Power State （ITPS）|ITPS]]，判斷是否進入閒置狀態並且切換電源狀態（PS）。

### Idle Time Prior to Transition（ITPT）
1. 當 NVMe 控制器進入閒置狀態時，開始計算 `ITPT`（閒置時間）。
2. `ITPT` 是一個時間閾值（單位為毫秒），當閒置時間超過該閾值時，控制器會根據 `ITPS` 進行狀態轉換。

### Idle Transition Power State （ITPS）
1. 當 `ITPT` 達到指定時間後，控制器會自動切換到 `ITPS` 所指定的低功耗狀態。
2.  `ITPS` 指定了要進入的電源狀態，通常是一個非運行（Non-Operational）電源狀態，例如 `PS3` 或 `PS4`。

![[Pasted image 20250311074058.png]]

備註 : 
>Controller Idle : 控制器被認為是空閒狀態，並且沒有任何未完成的命令在 I/O Submission Queue 當中，也就是沒有 [[Outstanding Command]]。

## 補充說明
### APSTE 以及 NOPPME 之間交互作用
兩個與電源管理相關的功能，它們之間可能存在交互作用的影響。

![[Pasted image 20250311090336.png]]

