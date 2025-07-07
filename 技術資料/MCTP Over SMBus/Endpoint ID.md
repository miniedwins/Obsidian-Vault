EID (Endpoint ID) 是 MCTP 資料鏈結層中用來識別設備的邏輯位址。 每個 Endpoint（例如 NVMe-MI、BMC 內部元件等）會分配一個唯一的 **非 0 EID**（通常由 Endpoint Discovery 或靜態配置來決定）。

## Null Destination EID
適用於設備尚未經由 Endpoint Discovery 分配 EID 的情況。

範例說明：
主機端發送出命令（Set Endpoint ID），MCTP Header （Destination EID）就會被設定為 `0`。

## Null Source EID
適用於設備已經接受 Endpoint ID， 但是該設備尚未被主機註冊。

範例說明：
主機端發送出命令（Set Endpoint ID），目的端會回覆接受 Endpoint ID 訊息， 但是當前目的端 EID還沒被主機端註冊，因此目的端回傳的 MCTP Header （Source EID）就會被設定為 `0`。

## Broadcast EID
主要用於 MCTP 控制訊息類型，用來給總線上的廣播 EID。

範例說明：
主機端發送出命令（Prepare for  Endpoint Discovery），MCTP Header （Destination EID）就會被設定為 `0xFF`。

>**限制：Null Source EID and Null Destination EID**
>1. 只能操作在 SMBus Physical Address。
>2. 不能跨 bus 使用（因為 Physical Address 在不同 bus 可能重複）。
