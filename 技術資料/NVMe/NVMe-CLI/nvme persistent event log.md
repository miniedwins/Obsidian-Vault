## 檢查支援 Persistent Event Feature

```shell
$ sudo nvme id-ctrl -H /dev/nvme0 | grep -i Persistent
[4:4] : 0x1 Persistent Event log Supported
[3:3] : 0 ANA Persistent Loss state Not Supported**
```

## 建立 Persistent Event Log

需要先建立 `Persistent Event Log`，否則會讀取不到日誌資訊。

```shell
$ sudo nvme persistent-event-log -a 1 /dev/nvme0
Establishing Persistent Event Log Context
```

## 讀取 Persistent Event Log Header

協議規範的 Log Header 長度為 `512 Bytes`。

```shell
$ sudo nvme persistent-event-log -a 1 -l 512 /dev/nvme0
```

## 讀取 Persistent Event Log

可以從 `Persistent Log Header` 取得日誌總長度。

```shell
$ sudo nvme persistent-event-log -a 1 -l 1024 /dev/nvme0
```

### 輸出結果 ( Event Header )

```shell
# Persistent Event Header
Persistent Event Log for device: nvme0
Action for Persistent Event Log: 0
Log Identifier: 13
Total Number of Events: 451
Total Log Length : 23398
Log Revision: 1
Log Header Length: 492
Timestamp: 1741245640291
Power On Hours (POH): 83Power Cycle Count: 69
PCI Vendor ID (VID): 7117
PCI Subsystem Vendor ID (SSVID): 7117
Serial Number (SN): 832401201019    
Model Number (MN): 7680GB PCIe Drive                   
NVM Subsystem NVMe Qualified Name (SUBNQN): nqn.2019-12.com.phison:nvme:nvm-subsystem-sn-832401201019
Generation Number: 0
Reporting Context Information (RCI): 0
Supported Events Bitmap:
Support SMART/Health Log Snapshot Event(0x1)
Support Firmware Commit Event(0x2)
Support Timestamp Change Event(0x3)
Support Power-on or Reset Event(0x4)
Support NVM Subsystem Hardware Error Event(0x5)
Support Change Namespace Event(0x6)
Support Format NVM Start Event(0x7)
Support Format NVM Completion Event(0x8)
Support Sanitize Start Event(0x9)
Support Sanitize Completion Event(0xa)
Support Set Feature Event(0xb)
Support Set Telemetry CRT Event(0xc)
Support Thermal Excursion Event(0xd)
```

### 輸出結果 ( Event Entries )
- 顯示 `Persistent Event Entries`，描述不同的事件日誌。
- 新的日誌會一直出現在最上層，原先舊的日誌會往後移動。

```shell
# Persistent Event Entries
Event Number: 0
Event Type: Set Feature Event(0xb)
Event Type Revision: 1
Event Header Length: 21
Event Header Additional Info: 0
Controller Identifier: 1
Event Timestamp: 1741244332056
Port Identifier: 0
Vendor Specific Information Length: 0
Event Length: 16
Set Feature Event Entry:
Set Feature ID  :0x7 (Number of Queues),  value:0x030003

Event Number: 1
Event Type: Timestamp Change Event(0x3)
Event Type Revision: 1
Event Header Length: 21
Event Header Additional Info: 0
Controller Identifier: 1
Event Timestamp: 1741244332046
Port Identifier: 0
Vendor Specific Information Length: 0
Event Length: 16
Time Stamp Change Event Entry:
Previous Timestamp: 0
Milliseconds Since Reset: 0
 
Event Number: 2
Event Type: Power-on or Reset Event(0x4)
Event Type Revision: 1
Event Header Length: 21
Event Header Additional Info: 0
Controller Identifier: 1
Event Timestamp: 18794
Port Identifier: 0
Vendor Specific Information Length: 0
Event Length: 44
Power On Reset Event Entry:
Firmware Revision: 3693290555842778192 (PTPQ14A3)
Reset Information List:
Controller ID: 1
Firmware Activation: 0
Operation in Progress: 0
Controller Power Cycle: 69
Power on milliseconds: 298323611
Controller Timestamp: 18794

Event Number: 3
Event Type: Change Namespace Event(0x6)
Event Type Revision: 1
Event Header Length: 21
Event Header Additional Info: 0
Controller Identifier: 1
Event Timestamp: 1741272443736
Port Identifier: 0
Vendor Specific Information Length: 0
Event Length: 48
Change Namespace Event Entry:
Namespace Management CDW10: 1
Namespace Size: 976773168
Namespace Capacity: 976773168
Formatted LBA Size: 0
End-to-end Data Protection Type Settings: 0
Namespace Multi-path I/O and Namespace Sharing Capabilities: 0
ANA Group Identifier: 0
NVM Set Identifier: 0
Namespace ID: 2
```