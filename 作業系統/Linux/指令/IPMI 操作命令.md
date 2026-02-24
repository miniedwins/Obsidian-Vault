
- 安裝 ipmitool 套件

```bash
$ apt install ipmitool
```

- 伺服器開機

```bash
$ ipmitool -H <bmc address> -U <User> -P <Password> power on
```

- 伺服器關機

```bash
$ ipmitool -H <bmc address> -U <User> -P <Password> power off
```

- 取得所有的感測器資訊

```bash
$ ipmitool -I lanplus -H <bmc address> -U <User> -P <Password> sensor list
```

- 取得指定感測器資訊 ( 例如 : 風扇或是其它元件 )

```bash
$ ipmitool -I lanplus -H <bmc address> -U <User> -P <Password> sensor get "FAN1"
```

