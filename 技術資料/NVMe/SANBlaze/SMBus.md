# NVMe-MI 命令參考手冊 — SMBus Transport

> 版本：V22.0 UNH-IOL Conformance Scripts
> Transport：SMBus / I2C (Out-of-Band)
> 更新日期：2026-08-13

---

## 目錄

1. [全域參數與命令結構](SMBus.md#1-全域參數與命令結構)
2. [MCTP Control Messages（msg_type=0x10）](SMBus.md#2-mctp-control-messages)
3. [NVMe-MI Control Primitives（msg_type=0x0）](SMBus.md#3-nvme-mi-control-primitives)
4. [NVMe-MI Commands（msg_type=0x1）](SMBus.md#4-nvme-mi-commands)
5. [NVMe-MI Admin Commands（msg_type=0x2）](SMBus.md#5-nvme-mi-admin-commands)
6. [錯誤注入參數](SMBus.md#6-錯誤注入參數)
7. [mi -v 輸出格式完整說明](SMBus.md#7-mi--v-輸出格式完整說明)
8. [命令速查表](SMBus.md#8-命令速查表)

---

## 1. 全域參數與命令結構

### 命令基本結構

```
mi -t <msg_type> -T <transport> -s <ip> -d <slot> [opcode] [subopcode] [options] -v
```

### Message Type（-t 參數）對照表

| -t 值 | 類型 | 說明 |
|--------|------|------|
| `0x10` | MCTP Control | MCTP 控制訊息（GetEndpointID, SetEndpointID 等） |
| `0x0` | Control Primitive | NVMe-MI 控制原語（Replay, Pause, Resume, Abort） |
| `0x1` | NVMe-MI | NVMe-MI 命令層（VPD, Health, Config, Read Data） |
| `0x2` | NVMe Admin | NVMe Admin 命令穿透（Identify, Get Log Page, Get/Set Features） |

### 全域必要參數

| 參數 | 說明 | 範例 |
|------|------|------|
| `-T smbus` | Transport 類型 | `-T smbus` |
| `-s <ip>` | SANBlaze 主機 IP | `-s 192.168.1.100` |
| `-d <slot>` | 目標設備 Slot 號碼 | `-d 0` |
| `-v` | Verbose 模式（raw bytes + 解析）| `-v` |

### 全域選用參數

| 參數 | 說明 |
|------|------|
| `-p <port>` | MCTP 實體 Port 號碼 |
| `-o <offset>` | 資料偏移量 |
| `-l <length>` | 資料長度（bytes）|
| `-w <hex>` | 寫入資料 Payload |
| `-c <ctrl_id>` | Controller ID |
| `-n <nsid>` | Namespace ID（-1 = 所有 NS）|
| `-C <csi>` | Command Slot Index（0 或 1）|
| `-I <id>` | Instance ID |
| `-k <tag>` | Message Tag（-1 = any）|
| `-m <hex 或 field>` | (1) Raw hex message；(2) CDB field patch（如 `45.7=1`）|
| `-H <hex>` | 覆蓋 MCTP Header（錯誤注入）|
| `-M 1` | 故意送出錯誤 MIC（錯誤注入）|

---

## 2. MCTP Control Messages（msg_type=0x10）

### 2.1 Get Endpoint ID（Opcode 0x2）

**用途：** 讀取設備的 MCTP Endpoint ID（EID），確認基本 MCTP 連線。
**對應測試：** Test 1.1.00, 1.4.x

```bash
mi -t 0x10 -T smbus -s $sanblaze -d $slot 0x2 -v
```

**輸出範例：**
```
smbus_req[0]: 10 08 01 C8 08 80 00 06 C8 00 00 04 02 00 AA
smbus_rsp[0]: 10 08 01 C8 08 00 00 0A C8 01 00 00 3C 00 12 BB
mi_rsp:
00 3C 00 00
mi_rsp len: 4
Endpoint Type: Simple Endpoint (0)
Endpoint ID: 60
```

**mi_rsp Bytes 解析：**

| Byte | 欄位 | 範例 | 說明 |
|------|------|------|------|
| 0 | Completion Code | `00` | 0x00 = 成功 |
| 1 | Endpoint ID (EID) | `3C` | 60 decimal |
| 2 | Endpoint Type | `00` | Simple Endpoint |
| 3 | Medium Specific | `00` | 保留 |

**錯誤注入變體（Test 1.4.1）：**
```bash
# SOM=0, EOM=0 → 設備應 silently drop
mi -t 0x10 -T smbus -s $sanblaze -d $slot 0x2 -H 01${dest_eid}${src_eid}08 -v

# SOM=0, EOM=1（孤立 end 封包）→ 設備應 silently drop
mi -t 0x10 -T smbus -s $sanblaze -d $slot 0x2 -H 01${dest_eid}${src_eid}48 -v

# Bad destination EID
mi -t 0x10 -T smbus -s $sanblaze -d $slot 0x2 -H 01ff${src_eid}c8 -v
```

**Flags Byte 值對照（-H 的第 4 byte）：**

| 值 | SOM | EOM | 意義 |
|----|-----|-----|------|
| `0xC8` | 1 | 1 | 正常單封包訊息 |
| `0x08` | 0 | 0 | Middle packet（無效）|
| `0x48` | 0 | 1 | End packet only（無效）|

---

### 2.2 Set Endpoint ID（Opcode 0x1）

**用途：** 指派新的 MCTP EID 給設備。
**對應測試：** Test 3.1

```bash
mi -t 0x10 -T smbus -s $sanblaze -d $slot 0x1 -v
mi -t 0x10 -T smbus -s $sanblaze -d $slot 0x1 -C 0 -v   # Operation=Set EID
mi -t 0x10 -T smbus -s $sanblaze -d $slot 0x1 -C 1 -v   # Operation=Force EID
```

---

### 2.3 Get MCTP Version Support（Opcode 0x4）

**用途：** 查詢設備支援的 MCTP 版本。
**對應測試：** Test 3.2

```bash
mi -t 0x10 -T smbus -s $sanblaze -d $slot 0x4 -w $ver_type -v
# $ver_type: 0xFF=MCTP base, 0x01=NVMe-MI
```

---

### 2.4 Get Message Type Support（Opcode 0x5）

**用途：** 取得端點支援的所有 MCTP Message Types。
**對應測試：** Test 3.3

```bash
mi -t 0x10 -T smbus -s $sanblaze -d $slot 0x5 -v
```

---

### 2.5 Prepare for Endpoint Discovery（Opcode 0x0B）

**對應測試：** Test 3.4

```bash
mi -t 0x10 -T smbus -s $sanblaze -d $slot 0xB -v
```

---

### 2.6 Endpoint Discovery（Opcode 0x0C）

**對應測試：** Test 3.5

```bash
mi -t 0x10 -T smbus -s $sanblaze -d $slot 0xC -v
```

---

## 3. NVMe-MI Control Primitives（msg_type=0x0）

Control Primitives 是單封包的 NVMe-MI 訊息，控制設備端的命令處理狀態。

### 3.1 Get State Primitive（Opcode 0x3）

**用途：** 查詢 NVMe-MI 端點目前的 Response State。
**對應測試：** Test 7.3

```bash
mi -t 0x0 -T smbus -s $sanblaze -d $slot 0x3 -v
```

**mi_rsp Bytes 解析：**

| Byte | 欄位 | 說明 |
|------|------|------|
| 0–3 | Response Header | Status + Reserved |
| 4 | State | `0x00`=Idle, `0x01`=Busy, `0x04`=Response Ready, `0x08`=Paused |
| 5 | CSI | 此狀態對應的 Command Slot Index |
| 6 | Flags | Error/Pause flags |
| 7 | Reserved | — |

---

### 3.2 Replay Primitive（Opcode 0x4）

**用途：** 指示設備重傳先前緩衝的 Response Message。
**對應測試：** Test 7.4, 7.5, 7.8, 7.9, 5.3

```bash
# Replay 全部（RRO=0）
mi -t 0x0 -T smbus -s $sanblaze -d $slot 0x4 0x0 -v

# Replay 帶 offset（跳過前 N 個封包）
mi -t 0x0 -T smbus -s $sanblaze -d $slot 0x4 <rro_value> -v

# 指定 Port 的 Replay
mi -t 0x0 -T smbus -s $sanblaze -d $slot 0x4 0x1 -p $smbus_pcie_port -v

# 指定 Port + CSI
mi -t 0x0 -T smbus -s $sanblaze -d $slot 0x4 0x1 -p $smbus_pcie_port -C $csi -v
```

| 參數 | 說明 |
|------|------|
| `<rro_value>` | Response Replay Offset（跳過幾個封包）|
| `-p <port>` | 要 Replay 的 MCTP Physical Port |
| `-C <csi>` | Command Slot Index（0 或 1）|

> **注意：** MCTP 本身無自動重傳，Replay 必須主機主動觸發。

---

### 3.3 Pause Primitive（Opcode 0x1）

**用途：** 暫停 Response Message 傳送（流量控制）。
**對應測試：** Test 7.10, 7.12

```bash
mi -t 0x0 -T smbus -s $sanblaze -d $slot 0x1 -p $smbus_pcie_port -C 0 -v
mi -t 0x0 -T smbus -s $sanblaze -d $slot 0x1 -p $smbus_pcie_port -C 1 -v
```

---

### 3.4 Resume Primitive（Opcode 0x2）

**用途：** 恢復先前暫停的 Response 傳送。
**對應測試：** Test 7.13

```bash
mi -t 0x0 -T smbus -s $sanblaze -d $slot 0x2 -p $smbus_pcie_port -v
```

---

### 3.5 Abort Command Message Primitive（Opcode 0x6）

**用途：** 中止設備正在處理的命令。
**對應測試：** Test 7.14, 7.15

```bash
mi -t 0x0 -T smbus -s $sanblaze -d $slot 0x6 -v
mi -t 0x0 -T smbus -s $sanblaze -d $slot 0x6 -C $csi -v
```

---

### 3.6 Async Event Completion Primitive（Opcode 0x5）

**用途：** 通知端點主機已接收 Async Event。
**對應測試：** Test 14.01

```bash
mi -t 0x0 -T smbus -s $sanblaze -d $slot 0x5 -I 1 -k -1 -v
```

| 參數 | 說明 |
|------|------|
| `-I 1` | Instance ID = 1 |
| `-k -1` | Message Tag = any |

---

## 4. NVMe-MI Commands（msg_type=0x1）

### 4.1 Read Data Structure（Opcode 0x0）

**用途：** 讀取 NVMe-MI 資料結構，透過 DTYP 選擇目標。
**對應測試：** Test 8.6

```bash
mi -t 0x1 -T smbus -s $sanblaze -d $slot 0x0 <DTYP> [options] -v
```

| DTYP | 資料結構 | 語法 |
|------|---------|------|
| `0x0` | NVM Subsystem Information | `mi -t 0x1 ... 0x0 0x0 -v` |
| `0x1` | Port Information | `mi -t 0x1 ... 0x0 0x1 -p $port -v` |
| `0x2` | Controller List | `mi -t 0x1 ... 0x0 0x2 -v` |
| `0x3` | Controller Information | `mi -t 0x1 ... 0x0 0x3 -c $ctrl_id -v` |
| `0x4` | Optional Commands Supported | `mi -t 0x1 ... 0x0 0x4 -v` |

**NVM Subsystem Info mi_rsp 欄位（DTYP=0x0）：**

| Byte | 欄位 | 說明 |
|------|------|------|
| 4 | NPort | 埠數量 |
| 5 | NVMSR | bit0=NVMESD, bit1=NVMEE |
| 6 | VWCI | VPD Write Cycles Info |
| 7 | MEC | ME Capabilities（bit0=SMBus, bit1=PCIe VDM）|

---

### 4.2 NVM Subsystem Health Status Poll（Opcode 0x1）

**對應測試：** Test 8.4

```bash
mi -t 0x1 -T smbus -s $sanblaze -d $slot 0x1 -v
mi -t 0x1 -T smbus -s $sanblaze -d $slot 0x1 -C 0 -v
```

---

### 4.3 Controller Health Status Poll（Opcode 0x2，via -m raw bytes）

**用途：** 針對特定 Controller 讀取健康/錯誤 flags。
**對應測試：** Test 8.5

```bash
# SMBus IC=1 版本（標準）
mi -T smbus -s $sanblaze -d $slot \
   -m 8408000002000000${contID}00871f000000 -v

# 含 filter（CWARN, SPARE, PDLU, CTEMP 全啟用）
mi -T smbus -s $sanblaze -d $slot \
   -m 8408000002000000${contID}00871f000080 -v
```

**Raw Message Byte 解析：**

| Bytes | 值 | 欄位 | 說明 |
|-------|-----|------|------|
| 0 | `84` | IC + MsgType | IC=1，MsgType=0x4 |
| 4–7 | `02000000` | Opcode | Controller Health Status Poll（0x02）LE |
| 8–11 | `${contID}` | CTRL_ID | 目標 Controller ID（LE）|
| 12 | `00` | MAXRENT | 最多回傳 Entry 數 |
| 13 | `87` | Filter | `0x87`=CWARN+SPARE+PDLU+CTEMP 全啟 |
| 14–15 | `1f00` | Status Filter | INCVF+INCPF+INCF+CCF = all |
| 16–17 | `0000`/`0080` | Starting Controller | 起始 Controller |

---

### 4.4 Configuration Get（Opcode 0x4）

**對應測試：** Test 5.4, 8.2, 8.3

| Config ID | 名稱 | 語法 |
|-----------|------|------|
| `0x1` | SMBus/I2C Frequency | `mi -t 0x1 ... 0x4 0x1 -p $port [-C $csi] -v` |
| `0x2` | Health Status Change | `mi -t 0x1 ... 0x4 0x2 -p $port [-C $csi] -v` |
| `0x3` | MCTP TUS | `mi -t 0x1 ... 0x4 0x3 -p $port [-M 1] -v` |

**Config Get 0x3 輸出範例：**
```
mi_rsp:
00 00 00 00 00 00 00 00 40 00 00 00
MCTP Transmission Unit Size: 0x40 (64 bytes)
```

---

### 4.5 Configuration Set（Opcode 0x3）

**對應測試：** Test 8.2

| Config ID | 名稱 | 語法 |
|-----------|------|------|
| `0x1` | SMBus/I2C Frequency | `mi -t 0x1 ... 0x3 0x1 -p $port -w 02 -v` |
| `0x3` | MCTP TUS | `mi -t 0x1 ... 0x3 0x3 -p $port -w 40000000 -v` |

**SMBus/I2C 頻率值：**

| -w 值 | 頻率 |
|-------|------|
| `01` | 100 kHz |
| `02` | 400 kHz |
| `03` | 1 MHz |

**MCTP TUS 值（Little Endian）：**

| -w 值 | TUS |
|-------|-----|
| `40000000` | 64 bytes |
| `80000000` | 128 bytes |

---

### 4.6 VPD Read（Opcode 0x5）

**用途：** 讀取 VPD EEPROM，最多 256 bytes。
**對應測試：** Test 1.2, 1.3, 8.12

```bash
mi -t 0x1 -T smbus -s $sanblaze -d $slot 0x5 -v
mi -t 0x1 -T smbus -s $sanblaze -d $slot 0x5 -o $vpd_offset -l $vpd_length -v
mi -t 0x1 -T smbus -s $sanblaze -d $slot 0x5 -o 254 -l 1 -v
```

---

### 4.7 VPD Write（Opcode 0x6）

**用途：** 寫入資料至 VPD EEPROM。
**對應測試：** Test 4.8, 8.13

```bash
mi -t 0x1 -T smbus -s $sanblaze -d $slot 0x6 -l 0 -v             # DLEN=0 測試
mi -t 0x1 -T smbus -s $sanblaze -d $slot 0x6 -o 254 -l 2 -w cccc -v
mi -t 0x1 -T smbus -s $sanblaze -d $slot 0x6 -o $offset -l $length -w $data -v
mi -t 0x1 -T smbus -s $sanblaze -d $slot 0x6 -o $offset -l $length -w $orig_value -v
```

---

### 4.8 Management Endpoint Buffer Read（Opcode 0x0A）

**對應測試：** Test 8.8

```bash
# SMBus raw bytes（cmd_byte0=84）
mi -T smbus -s $sanblaze -d $slot \
   -m 840800000a000000${offsethex}${dlenhex} -v
```

---

### 4.9 Management Endpoint Buffer Write（Opcode 0x0B）

**對應測試：** Test 8.9

```bash
mi -T smbus -s $sanblaze -d $slot \
   -m 840800000b000000${offsethex}${dlenhex}${write_data} -v
```

---

### 4.10 Management Endpoint Reset（Opcode 0x06 via raw bytes）

**對應測試：** Test 12.5, 12.7

```bash
mi -T smbus -s $sanblaze -d $slot -m 8408000006000000 -v
```

---

### 4.11 SES Receive（Opcode 0x8）

**對應測試：** Test 8.10

```bash
mi -t 0x1 -T smbus -s $sanblaze -d $slot 0x8 $subopcode -v
mi -t 0x1 -T smbus -s $sanblaze -d $slot 0x8 $subopcode -c $cont_num -v
```

---

### 4.12 SES Send（Opcode 0x9）

**對應測試：** Test 8.11

```bash
mi -t 0x1 -T smbus -s $sanblaze -d $slot 0x9 $subopcode -v
mi -t 0x1 -T smbus -s $sanblaze -d $slot 0x9 $subopcode -c $cont_num -v
```

---

## 5. NVMe-MI Admin Commands（msg_type=0x2）

### 5.1 Identify（Admin Opcode 0x6）

**對應測試：** Test 9.1, 10.1, 10.2

```bash
# Identify Controller（CNS=0x1）
mi -t 0x2 -T smbus -s $sanblaze -d $slot 0x6 0x1 -c $controller_id -v

# Identify Namespace（CNS=0x0）
mi -t 0x2 -T smbus -s $sanblaze -d $slot 0x6 0x0 -n $ns -c $controller_id -v
```

**CNS 值對照：**

| CNS | 資料結構 |
|-----|---------|
| `0x0` | Namespace 資料結構 |
| `0x1` | Identify Controller |
| `0x2` | Active Namespace ID List |
| `0x5` | I/O CS 特定 Identify Namespace |
| `0x6` | I/O CS 特定 Identify Controller |
| `0x1C` | I/O CS Independent Identify Namespace |

---

### 5.2 Get Log Page（Admin Opcode 0x2）

**對應測試：** Test 9.2

```bash
# 基本語法
mi -t 0x2 -T smbus -s $sanblaze -d $slot 0x2 0x${LID} -c $controller_id -l $length -v

# 含 Namespace ID
mi -t 0x2 -T smbus -s $sanblaze -d $slot 0x2 0x${LID} \
   -n $lid_nsid -c $controller_id -l $length $mi_timeout -v

# 含 CDB field 修改（LSI, RAE 等）
mi -t 0x2 -T smbus -s $sanblaze -d $slot 0x2 0x${LID} \
   -n $lid_nsid -c $controller_id -l $length \
   -m 50-51=$lsi_hex,45.7=1 -v
```

**常用 LID 對照：**

| LID | Log Page 名稱 |
|-----|---------------|
| `0x01` | Error Information |
| `0x02` | SMART / Health Information |
| `0x03` | Firmware Slot Information |
| `0x04` | Changed Namespace List |
| `0x05` | Commands Supported and Effects |
| `0x06` | Device Self-Test |
| `0x07` | Telemetry Host-Initiated |
| `0x08` | Telemetry Controller-Initiated |
| `0x09` | Endurance Group Information |
| `0x0D` | Persistent Event Log |
| `0x13` | NVMe-MI Commands Supported and Effects |
| `0x15` | Boot Partition Log |

**-m CDB Field 修改格式：**

| 格式 | 說明 |
|------|------|
| `45.7=1` | CDB byte 45 的 bit 7 = 1（RAE）|
| `50-51=$lsi` | CDB bytes 50–51 = LSI 值 |
| `62.7=0` | CDB byte 62 的 bit 7 = 0 |
| `45.0=$bpid` | CDB byte 45 的 bit 0 = BPID |
| `48.0=$gdhm` | CDB byte 48 的 bit 0 = GDHM |

---

### 5.3 Get Features（Admin Opcode 0xa）

**對應測試：** Test 9.3, 10.3, 10.4

```bash
mi -t 0x2 -T smbus -s $sanblaze -d $slot 0xa 0x${FID} \
   -n $ns -c $controller_id $mi_length -v

# 含 GDHM bit
mi -t 0x2 -T smbus -s $sanblaze -d $slot 0xa 0x${FID} \
   -n $ns -c $controller_id -l $length -m 48.0=$gdhm -v
```

---

### 5.4 Set Features（Admin Opcode 0x9）

**對應測試：** Test 9.3, 10.3, 10.4

```bash
mi -t 0x2 -T smbus -s $sanblaze -d $slot 0x9 0x${FID} \
   -n $nsid -c $controller_id $mi_length -w $value -v

# 含 EA/SV CDB patch
mi -t 0x2 -T smbus -s $sanblaze -d $slot 0x9 0x${FID} \
   -n $ns -c $controller_id -m 49.5-6=$ea -w $value_to_set -v
```

**常用 FID 對照：**

| FID | Feature 名稱 |
|-----|-------------|
| `0x01` | Arbitration |
| `0x02` | Power Management |
| `0x04` | Temperature Threshold |
| `0x05` | Error Recovery |
| `0x06` | Volatile Write Cache |
| `0x07` | Number of Queues |
| `0x0B` | Asynchronous Event Configuration |
| `0x0E` | Timestamp |
| `0x7E` | Controller Metadata |
| `0x7F` | Namespace Metadata |
| `0x84` | Namespace Write Protection Config |

---

### 5.5 Sanitize（Admin Opcode 0x84）

**對應測試：** Test 9.5

```bash
mi -t 0x2 -T smbus -s $sanblaze -d $slot 0x84 $SANACT \
   -n 0 -c $controller_id -v
```

**SANACT 值對照：**

| 值 | Sanitize Action |
|----|----------------|
| `0x1` | Exit Failure Mode |
| `0x2` | Block Erase |
| `0x3` | Overwrite |
| `0x4` | Crypto Scramble Erase |

---

### 5.6 Asynchronous Event Request（背景執行）

**對應測試：** Test 14.1

```bash
# & 表示背景執行，等待設備主動送出 Async Event Notification
mi -t 0x2 -T smbus -s $sanblaze -d $slot 0x2 0x${subopcode1} -c $controller_id -v &
```

---

## 6. 錯誤注入參數

### 6.1 -H — 覆蓋 MCTP Header

**格式：** `-H 01 <dest_eid> <src_eid> <flags_byte>`

**Flags Byte 位元定義：**

| 位元 | 名稱 | 說明 |
|------|------|------|
| bit 7 | SOM | Start of Message |
| bit 6 | EOM | End of Message |
| bit 5 | TO | Tag Owner（1=Host 送出）|
| bit 4–3 | PktSeq | Packet Sequence Number（0–3 循環）|

**使用範例：**
```bash
# 正常訊息
mi -t 0x10 -T smbus -s $sanblaze -d $slot 0x2 -H 01${dest_eid}${src_eid}c8 -v

# 注入 middle packet（Test 1.4.1）
mi -t 0x10 -T smbus -s $sanblaze -d $slot 0x2 -H 01${dest_eid}${src_eid}08 -v

# 注入錯誤 EID（Test 1.4.2）
mi -t 0x10 -T smbus -s $sanblaze -d $slot 0x2 -H 01ff${src_eid}c8 -v
```

---

### 6.2 -M 1 — 故意送出壞 MIC

**對應測試：** Test 5.6

```bash
# 正常 MIC（mi 自動計算 CRC-32C）
mi -t 0x1 -T smbus -s $sanblaze -d $slot 0x4 0x3 -p $mctp_port -v

# 壞 MIC（-M 1 讓 mi 故意送錯 CRC-32C）
mi -t 0x1 -T smbus -s $sanblaze -d $slot 0x4 0x3 \
   -p $mctp_port -H 01${dest_eid}${src_eid}c8 -M 1 -v
```

**預期行為：**
- 正常：`mi_rsp:` 出現 → 設備接受並回應
- 壞 MIC：`mi_rsp:` **不出現** → 設備正確 silently drop

---

### 6.3 -m — Raw Message Bytes 或 CDB Field Patch

**用途一：** 完整 raw hex message（繞過高層封裝）

```bash
# IC=1 SMBus 版本的 Configuration Get Health Status Change
mi -T smbus -s $sanblaze -d $slot -m 84080000040000000200000000000000 -v
```

**Byte 解析：**

| Bytes | 值 | 說明 |
|-------|-----|------|
| 0 | `84` | IC=1, MsgType=0x4（NVMe-MI）|
| 1–3 | `080000` | Header Flags + Reserved |
| 4–7 | `04000000` | Opcode=Config Get (0x04) LE |
| 8–11 | `02000000` | Config ID=Health Status Change LE |
| 12–15 | `00000000` | Port=0 |

**用途二：** Admin CDB field 修改（`BYTE.BIT=VALUE` 語法）

```bash
# Get Log Page with RAE=1, LSI=0x0001
mi -t 0x2 -T smbus -s $sanblaze -d $slot 0x2 0x02 \
   -n -1 -c $controller_id -l 512 -m 45.7=1,50-51=0001 -v
```

---

## 7. mi -v 輸出格式完整說明

### 7.1 輸出區段結構

```
smbus_req[0]: 10 08 01 C8 08 80 00 06 C8 00 00 04 05 00 XX
              ↑ TX SMBus Raw frame（MCTP Header + NVMe-MI Message）

smbus_rsp[0]: 10 08 01 C8 08 00 00 0A C8 01 00 00 3C 00 XX
smbus_rsp[1]: 10 08 01 C8 48 00 00 0A ...
              ↑ RX 每個 MCTP 封包（可能多個）

mi_rsp:
00 3C 00 00 01 02 ...
              ↑ 重組後的 NVMe-MI Message 層 bytes

mi_rsp len: 8
Response Status: 00h
              ↑ Human-readable 解析
```

### 7.2 smbus_rsp 欄位位置

| field 序號 | 說明 |
|-----------|------|
| field 1 | SMBus Slave Address |
| field 2 | PEC 計算長度 |
| field 3 | Command Code |
| field 4 | Byte Count |
| field 5 | MCTP Reserved |
| field 6 | Source EID |
| field 7 | Dest EID |
| field 8 | Message Length |
| **field 9** | **MCTP Flags Byte（SOM/EOM/TO/PktSeq）** |
| field 10+ | NVMe-MI Message Header + Payload |
| last | PEC（CRC-8）|

### 7.3 mi_rsp 的 NVMe-MI Response Header

| Byte | 欄位 | 說明 |
|------|------|------|
| 0 | IC + MsgType | `0x01` = NVMe-MI Response |
| 1 | Reserved | `0x00` |
| 2 | Reserved | `0x00` |
| 3 | IID | Instance ID（需與 Request 相符）|
| 4 | Reserved | `0x00` |
| **5** | **Response Status** | **0x00=成功；非零=錯誤**（見 NVMe-MI Spec Table）|
| 6–7 | Reserved | `0x0000` |
| 8+ | Response Data | 命令特定回傳資料 |

### 7.4 Python 解析 MCTP Flags Byte 參考

```python
def parse_mctp_flags(byte_val: int) -> dict:
    return {
        'SOM':    (byte_val >> 7) & 1,      # bit 7
        'EOM':    (byte_val >> 6) & 1,      # bit 6
        'TO':     (byte_val >> 5) & 1,      # bit 5 (Tag Owner)
        'PktSeq': (byte_val >> 3) & 0b11,   # bits 4-3
        'MsgTag': byte_val & 0b111,         # bits 2-0
    }
```

---

## 8. 命令速查表

### Control Primitive（-t 0x0）

| Opcode | 命令 | 語法 |
|--------|------|------|
| `0x1` | Pause | `mi -t 0x0 ... 0x1 -p $port -C $csi -v` |
| `0x2` | Resume | `mi -t 0x0 ... 0x2 -p $port -v` |
| `0x3` | Get State | `mi -t 0x0 ... 0x3 -v` |
| `0x4` | Replay | `mi -t 0x0 ... 0x4 <rro> [-p $port] [-C $csi] -v` |
| `0x5` | Async Event Completion | `mi -t 0x0 ... 0x5 -I 1 -k -1 -v` |
| `0x6` | Abort | `mi -t 0x0 ... 0x6 [-C $csi] -v` |

### MCTP Control（-t 0x10）

| Opcode | 命令 | 語法 |
|--------|------|------|
| `0x1` | Set Endpoint ID | `mi -t 0x10 ... 0x1 [-C 0/1] -v` |
| `0x2` | Get Endpoint ID | `mi -t 0x10 ... 0x2 -v` |
| `0x4` | Get MCTP Version | `mi -t 0x10 ... 0x4 -w $ver -v` |
| `0x5` | Get Message Type | `mi -t 0x10 ... 0x5 -v` |
| `0xB` | Prepare EP Discovery | `mi -t 0x10 ... 0xB -v` |
| `0xC` | Endpoint Discovery | `mi -t 0x10 ... 0xC -v` |

### NVMe-MI（-t 0x1）

| Opcode | 命令 | 語法 |
|--------|------|------|
| `0x0` | Read Data Structure | `mi -t 0x1 ... 0x0 <DTYP> [-p $port] [-c $ctrl] -v` |
| `0x1` | NVM Subsystem Health | `mi -t 0x1 ... 0x1 [-C $csi] -v` |
| `0x2` | Controller Health | `mi ... -m 84080000 02000000 ... -v` |
| `0x3` | Configuration Set | `mi -t 0x1 ... 0x3 <CfgID> -p $port -w $val -v` |
| `0x4` | Configuration Get | `mi -t 0x1 ... 0x4 <CfgID> -p $port [-C $csi] -v` |
| `0x5` | VPD Read | `mi -t 0x1 ... 0x5 [-o $off] [-l $len] -v` |
| `0x6` | VPD Write | `mi -t 0x1 ... 0x6 [-o $off] -l $len -w $data -v` |
| `0x8` | SES Receive | `mi -t 0x1 ... 0x8 $subop [-c $ctrl] -v` |
| `0x9` | SES Send | `mi -t 0x1 ... 0x9 $subop [-c $ctrl] -v` |
| `0x0A` | ME Buffer Read | `mi ... -m 84...0a000000${off}${len} -v` |
| `0x0B` | ME Buffer Write | `mi ... -m 84...0b000000${off}${len}${data} -v` |

### NVMe-MI Admin（-t 0x2）

| Opcode | 命令 | 語法 |
|--------|------|------|
| `0x2` | Get Log Page | `mi -t 0x2 ... 0x2 0x${LID} -n $ns -c $ctrl -l $len -v` |
| `0x6` | Identify | `mi -t 0x2 ... 0x6 <CNS> [-n $ns] -c $ctrl -v` |
| `0x9` | Set Features | `mi -t 0x2 ... 0x9 0x${FID} -n $ns -c $ctrl -w $val -v` |
| `0xa` | Get Features | `mi -t 0x2 ... 0xa 0x${FID} -n $ns -c $ctrl [-l $len] -v` |
| `0x84` | Sanitize | `mi -t 0x2 ... 0x84 $SANACT -n 0 -c $ctrl -v` |
