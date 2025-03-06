## 概要說明
Persistent Event Log（持久性事件日誌）是一種 NVMe 控制器用來記錄重要事件的日誌，它在某些條件下會被保留，但在某些情況下會被清除。

當發生 **影響多個控制器的事件**（例如 NVM Subsystem Reset）時，廠商指定的一個控制器負責記錄，而其他控制器不會重複記錄相同事件。

## Persistent Event Log 記錄的事件
Persistent Event Log 記錄的事件可以參考 [[Supported Events Bitmap]]，Bitmap 是用來表示哪些事件類別可以被記錄到 `Persistent Event Log`。

## 何時會清除 Persistent Event Log？
Persistent Event Log `不會永久保存`，它的清除條件如下：  
1. 當控制器所儲存的資料，超過 [[Persistent Event Log Size]]  可以支援的大小
2. 當控制器收到 `Get Log Page` 命令，且 Action 欄位為 `02h`（Release Context）
3. 發生 NVM Subsystem Reset（NVMe 子系統重置）
4. 發生 Controller Level Reset（控制器級別重置）
5. 廠商自訂的保留時間過期（例如，超過 1000 Timestamp 事件發生）

## 如何讀取 Persistent Event Log？
- 主機應使用 `Get Log Page` 命令來讀取 Persistent Event Log。
	- 如果指定的 Action 欄位為 `01h`，從現有的日誌讀取數據。
	- 如果指定的 Action 欄位為 `02h`，釋放 Persistent Event Log。

![[Pasted image 20250306084323.png]]

## 檢查支援 Persistent Event Log
- 可以透過 Identify Controller Data Structure 來確認支援狀況。
- Log Page Attributes，確認是否支援 `Persistent Event Log (PES)`。

![[Pasted image 20250305165826.png]]