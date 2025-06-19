Management Component Transport Protocol (MCTP) 使用 **Message Type** 字段來區分不同類型的消息，這些代碼定義在 **DMTF DSP0236 (MCTP Base Specification)** 及相關標準中。以下是完整的 MCTP Message Type 分類與說明：

![[Pasted image 20250619112614.png]]

當 BMC 或管理控制器需要透過 SMBus/I2C 傳送 NVMe 管理命令（NVMe-MI）時，MCTP 封包的 Message Type 必須設定為 `0x04`，表示這是一個 `NVMe-MI over MCTP` 的消息。

如果只是要傳送 MCTP 基礎控制協議（例如端點發現、協商或路由管理），則 Message Type 需設定為 `0x00`，表示這是一個 `MCTP Control Message`。

![[Pasted image 20250619113950.png]]