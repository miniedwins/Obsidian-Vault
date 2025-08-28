在 MCTP 協議中，Message Type 欄位是每一筆封包中 **用來識別上層協議內容** 的欄位。它的存在目的，是讓主機判斷這是一筆「控制指令」還是某個上層協議（如 PLDM 或 NVMe-MI）的資料。

## Control Message
如果只是要傳送 MCTP 基礎控制協議（例如端點發現、協商或路由管理），則 Message Type 需設定為 `0x00`，表示這是一個 MCTP Control Message。

> 基本 MCTP Control Message 並不會使用 Integrity Check field（IC），因此該位元會設定為 0。

![[Pasted image 20250620165945.png]]

## NVMe-MI Message
當 BMC 或管理控制器需要透過 SMBus/I2C 傳送 NVMe 管理命令（NVMe-MI）時，MCTP 封包的 Message Type 必須設定為 `0x04`，表示這是一個 NVMe-MI over MCTP Message。

![[Pasted image 20250620171239.png]]

## MCTP Message Type Codes
這些代碼定義在 DMTF DSP0236 (MCTP Base Specification) 及相關標準中。以下是完整的 MCTP Message Type 分類與說明：

![[Pasted image 20250619112614.png]]