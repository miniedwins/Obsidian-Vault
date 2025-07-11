

## 範例說明（單 Slot）

假設目前正在使用 Command Slot 0，Controller 傳送以下 3 個封包：

| Packet | SOM | EOM | Msg Tag | TO  | Payload | 屬於哪個 Slot |
| ------ | --- | --- | ------- | --- | ------- | --------- |
| 1      | 1   | 0   | 0       | 1   | ...     | Slot 0    |
| 2      | 0   | 0   | 0       | 1   | ...     | Slot 0    |
| 3      | 0   | 1   | 0       | 1   | ...     | Slot 0    |
這 3 個封包是 **同一條 Command Message**，由 SOM 開始、EOM 結束、Msg Tag 一致 → 屬於同一 Slot。

在這個命令還沒回應完成前，**不可以用 Slot 0 傳送另一條命令**，即使換 Msg Tag 也不行。

## 延伸範例（同時使用 2 Slot）

✔ Slot 0 和 Slot 1 可以同時處理不同的 Command Message（互不干擾）

| Packet  | Msg Tag | Target Slot | 狀態         |
| ------- | ------- | ----------- | ---------- |
| A-1~A-n | 0       | Slot 0      | 正在傳送中      |
| B-1~B-n | 1       | Slot 1      | 可同時傳送第二條命令 |
