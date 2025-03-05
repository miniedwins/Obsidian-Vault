## 概要說明
`Supported Events Bitmap` 指的是 控制器支援的事件類型的位元圖（Bitmap），用來表示哪些事件類別可以被記錄到 `Persistent Event Log`（持久化事件日誌）中。

## SEB 的作用
- 每個 bit 對應一種類別的事件。
- 如果某個 bit 被設定為 `1`，表示該類別的事件會被記錄到 `Persistent Event Log`。
- 如果某個 bit 被設定為 `0`，則該類別的事件不會被記錄。
- 設備廠商（Vendor）可以自定義事件類別 `VSES`。

![[Pasted image 20250305181221.png]]