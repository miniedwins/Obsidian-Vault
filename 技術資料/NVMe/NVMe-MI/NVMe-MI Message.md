


![[Pasted image 20250620171239.png]]

## Message Type
MCTP 封包的 Message Type 必須設定為 `0x04`，表示這是一個 NVMe-MI over MCTP Message。

## Integrity Check field ( IC )
- All NVMe-MI Messages in the **in-band tunneling mechanism** shall not be protected by a CRC and thus this bit shall be cleared to `0` in all in-band NVMe-MI Messages.

- All NVMe-MI Messages in the **out-of-band mechanism** shall be protected by a CRC and thus this bit shall be set to `1` in all out-of-band NVMe-MI Messages.

## Request or Response ( ROR )

## Command Slot Identifier ( CSI )

## NVMe-MI Message Type

![[Pasted image 20250710153234.png]]


