
### 1. PDUOutletControl

直接上斷電，不需要設定延遲

PDUOutletControlOutletCommand

- **PowerOnTime**
	- `snmpset -v 1 -c private $IP 1.3.6.1.4.1.318.1.1.12.3.3.1.1.4.2 i 1`

- **PowerOffTime**
	- `snmpset -v 1 -c private $IP 1.3.6.1.4.1.318.1.1.12.3.3.1.1.4.2 i 2`

### 2. PDUOutletConfig

- PDUOutletConfigPowerOnTime
    
- **設定斷電維持時間 1 秒 (ConfigPowerOffTime)** 


### 2. 執行指令 (Control)
- **啟動「延遲重啟」 (delayedReboot = 6)** `snmpset -v 1 -c private {ipaddr} 1.3.6.1.4.1.318.1.1.12.3.3.1.1.4.2 i 6`

---

### 🆘 緊急救援

- **取消倒數/掛起指令 (cancelPendingCommand = 7)** `snmpset -v 1 -c private {ipaddr} 1.3.6.1.4.1.318.1.1.12.3.3.1.1.4.2 i 7`