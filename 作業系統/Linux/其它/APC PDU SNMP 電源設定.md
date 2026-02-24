
**環境變數假設：** `$IP` 為 PDU 網址，範例皆以操作 **Port 2** 為例。 

## 1. 立即動作 (Control)

**OID: `1.3.6.1.4.1.318.1.1.12.3.3.1.1.4`**

**控制語法：** `snmpset -v 1 -c private $IP {OID}.{Port} i {Value}

```shell
# 立即上電 (immediateOn = 1)
$ snmpset -v 1 -c private $IP 1.3.6.1.4.1.318.1.1.12.3.3.1.1.4.2 i 1

# 立即斷電 (immediateOff = 2)
$ snmpset -v 1 -c private $IP 1.3.6.1.4.1.318.1.1.12.3.3.1.1.4.2 i 2

# 取消倒數 (cancelPendingCommand = 7) *緊急停止用*
$ snmpset -v 1 -c private $IP 1.3.6.1.4.1.318.1.1.12.3.3.1.1.4.2 i 7
```

## 2. 延遲重啟設定與執行

**OID: `1.3.6.1.4.1.318.1.1.12.3.4.1.1.{Config}.{Port}`**

- `.3` = `PowerOnTime` (指令下達後，延遲上電的時間)
    
- `.4` = `PowerOffTime` (指令下達後，延遲斷電的時間)   

**控制語法：** `snmpset -v 1 -c private $IP {OID}.{Port} i {Time}

**實戰範例：設定「5 秒後斷電，斷電維持 15 秒後上電」**

```shell
# 1. 設定上電前等待 15 秒 (Config .4)
snmpset -v 1 -c private $IP 1.3.6.1.4.1.318.1.1.12.3.4.1.1.4.2 i 15

# 2. 設定斷電前等待 5 秒 (Config .5)
snmpset -v 1 -c private $IP 1.3.6.1.4.1.318.1.1.12.3.4.1.1.5.2 i 5

# 3. 觸發執行「延遲重啟」 (Control, delayedReboot = 6)
snmpset -v 1 -c private $IP 1.3.6.1.4.1.318.1.1.12.3.3.1.1.4.2 i 6
```

> 小叮嚀:
> 只要一次設定完成後，之後只要每次直接執行延遲重啟，即可重複進行上斷電動作。

## 參考網站
[Online MIB Browser](https://mibbrowser.online/mibdb_search.php?mib=POWERNET-MIB)