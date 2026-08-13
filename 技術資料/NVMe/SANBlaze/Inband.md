# NVMe-MI 命令參考手冊 — Inband Transport

> 版本：V22.0 UNH-IOL Conformance Scripts
> Transport：PCIe Inband（NVMe-MI 透過 PCIe 通道）
> 更新日期：2026-08-13

---

## 目錄

1. [Inband vs. SMBus 架構差異](#1-inband-vs-smbus-架構差異)
2. [Inband Raw Message 格式說明](#2-inband-raw-message-格式說明)
3. [測試邊界行為：Inband 上的禁用命令](#3-測試邊界行為inband-上的禁用命令)
4. [Inband NVMe-MI 命令](#4-inband-nvme-mi-命令)
5. [Inband Admin Commands（64-byte Capsule 格式）](#5-inband-admin-commands64-byte-capsule-格式)
6. [Inband 特有行為差異](#6-inband-特有行為差異)
7. [SMBus vs. Inband 命令對照表](#7-smbus-vs-inband-命令對照表)

---

## 1. Inband vs. SMBus 架構差異

### 傳輸架構比較

| 項目 | SMBus (Out-of-Band) | Inband (PCIe) |
|------|---------------------|---------------|
| 傳輸通道 | I2C/SMBus（帶 MCTP 分包）| PCIe NVMe Admin 通道 |
| mi 命令 Transport | `-T smbus` | `-T inband` |
| MCTP Header | 每個封包有 MCTP Header（SOM/EOM/PktSeq）| 無 MCTP 分包機制 |
| IC Bit (Integrity Check) | **IC=1（必須帶 MIC CRC-32C）**| **IC=0（不帶 MIC）**|
| MIC（Message Integrity Check）| 必須（最後封包末尾 4 bytes）| 無 MIC |
| Control Primitives | 支援（Replay, Pause, Resume, Abort, Get State）| **禁止（spec 規定）**|
| MCTP Control Messages | 支援（Get/Set EID 等）| **不適用（N/A）**|
| Admin Commands 封裝 | NVMe-MI 封裝（msg_type=0x2）| 64-byte NVMe Admin Capsule |
| 回應長度計算 | `mi_rsp_length - 12` | `mi_rsp_length - 4096` 或 `- 4088` |

### 傳輸層 Header 中的 IC Bit 決定

```
SMBus 命令（IC=1）：  cmd_byte0="84"  → 0x84 = 1000 0100 (IC=1, MsgType=0x4)
Inband 命令（IC=0）： cmd_byte0="04"  → 0x04 = 0000 0100 (IC=0, MsgType=0x4)
```

這個 `cmd_byte0` 是所有使用 `-m` raw bytes 命令的第一個 byte。

---

## 2. Inband Raw Message 格式說明

所有 Inband 命令都透過 `-m <hex_string>` 傳送完整的 NVMe-MI Message。
以下是通用的 byte 結構：

### 2.1 NVMe-MI Message Header（前 4 bytes）

```
Byte 0: IC + MsgType
  bit 7   = IC (Integrity Check): 0 = Inband, 1 = SMBus
  bits 3:0 = MsgType:
    0x0 = Control Primitive
    0x1 = NVMe-MI Command
    0x2 = NVMe Admin Command (via MI encapsulation)
    0x4 = PCIe Direct / MI Tunneling Frame

Byte 1: Flags / Command Slot / Reserved
Byte 2-3: Reserved (0x0000)
```

### 2.2 NVMe-MI Command Payload（Bytes 4-15 for simple commands）

```
Bytes 4-7:  Opcode（Little Endian，32-bit）
Bytes 8-11: Config ID / Controller ID / SubOpcode（Little Endian）
Bytes 12-15: Port / Reserved（Little Endian）
```

### 2.3 NVMe Admin Capsule Payload（64-byte 格式）

```
Byte 0:    IC + MsgType（0x04 for Inband）
Byte 1:    Flags
Byte 4:    Admin Opcode
Byte 5:    Control Flags
Byte 6-7:  Controller ID（LE）
Bytes 8-27: NVMe CDB Reserved fields
Bytes 28-29: Data Transfer Length（LE）
Bytes 30-39: Reserved
Byte 40:   Feature Identifier (FID) 或 Log Page ID (LID)
Bytes 41-63: Reserved
```

---

## 3. 測試邊界行為：Inband 上的禁用命令

### 3.1 Control Primitives → Inband 禁用

**NVMe-MI 規範規定：** Control Primitives（Replay, Pause, Resume, Abort, Get State）在 Inband transport 上是被禁止的。

**Test 5.3 — CRC Check（Control Primitive Replay）：**

```bash
# SMBus 版本（正常）
mi -t 0x0 -T smbus -s $sanblaze -d $slot 0x4 0x0 -v

# Inband 等效（raw bytes）→ 預期失敗/錯誤
mi -T inband -s $sanblaze -d $slot -m 0400000004000000 -v
```

**Byte 解析（`0400000004000000`）：**

| Bytes | 值 | 說明 |
|-------|-----|------|
| 0 | `04` | IC=0, MsgType=0x4 |
| 1–3 | `000000` | Reserved |
| 4 | `04` | Control Primitive Opcode = Replay (0x04) |
| 5–7 | `000000` | RRO=0, Reserved |

**預期行為：** Inband 設備應回傳錯誤（`inband_nvme_err`），腳本確認此為正確拒絕行為。

---

### 3.2 Admin Commands via NVMe-MI（msg_type=0x2）→ Inband 禁用

**Test 9.3/10.3/10.4 — Get/Set Features：**  
透過 NVMe-MI 封裝（msg_type=0x2）發送 Admin Commands 到 Inband transport 是**被禁止**的。  
腳本使用 raw bytes（64-byte Admin Capsule 格式）測試此拒絕行為。

**預期行為：** `error_code != 0`（設備回傳錯誤）

---

### 3.3 IC Bit = 1 on Inband → 違規

**Test 5.2 — Message IC Test：**

```bash
# IC=1 on Inband（錯誤，規範規定 Inband 不使用 IC）
mi -T inband -s $sanblaze -d $slot -m 84080000040000000200000000000000 -v

# IC=0 on Inband（正確）
mi -T inband -s $sanblaze -d $slot -m 04080000040000000200000000000000 -v
```

---

## 4. Inband NVMe-MI 命令

這些命令透過 Inband transport 發送，語法與 SMBus 版本相同，只有 Transport 和 IC bit 不同。

### 4.1 Read Data Structure（DTYP 0x0–0x4）

**Test 8.6**

```bash
# NVM Subsystem Information（DTYP=0x0）
mi -t 0x1 -T inband -s $sanblaze -d $slot 0x0 0x0 -v

# Port Information（DTYP=0x1）
mi -t 0x1 -T inband -s $sanblaze -d $slot 0x0 0x1 -p $port -v

# Controller List（DTYP=0x2）
mi -t 0x1 -T inband -s $sanblaze -d $slot 0x0 0x2 -v

# Controller Information（DTYP=0x3）
mi -t 0x1 -T inband -s $sanblaze -d $slot 0x0 0x3 -c $controller_id -v

# Optional Commands Supported（DTYP=0x4）
mi -t 0x1 -T inband -s $sanblaze -d $slot 0x0 0x4 -v
```

**Inband 特有注意事項：**
- Endpoint Discovery 步驟會被跳過（`SKIPPED: DoEndpointDiscovery`）
- 若 MI 版本 >= 1.2，會先確認 Inband 支援位元

---

### 4.2 Configuration Get（Opcode 0x4）— Inband 版本

**Test 5.2, 5.4**

```bash
# Configuration Get — Health Status Change（IC=0，Inband 正確）
mi -T inband -s $sanblaze -d $slot -m 04080000040000000200000000000000 -v

# Configuration Get — MCTP TUS（使用高層語法）
mi -t 0x1 -T inband -s $sanblaze -d $slot 0x4 0x3 -p $mctp_port -v

# Configuration Get — SMBus/I2C Frequency（帶 CSI）
mi -t 0x1 -T inband -s $sanblaze -d $slot 0x4 0x1 -p $smbus_pcie_port -C 0 -v
mi -t 0x1 -T inband -s $sanblaze -d $slot 0x4 0x1 -p $smbus_pcie_port -C 1 -v
```

**Config Get Health Status Change Inband Raw Byte 解析（`04 08 00 00 04 00 00 00 02 00 00 00 00 00 00 00`）：**

| Bytes | 值 | 欄位 | 說明 |
|-------|-----|------|------|
| 0 | `04` | IC + MsgType | IC=0（Inband），MsgType=0x4 |
| 1–3 | `080000` | Header Flags | |
| 4–7 | `04000000` | Opcode | Config Get (0x04) LE |
| 8–11 | `02000000` | Config ID | Health Status Change (0x02) LE |
| 12–15 | `00000000` | Port | Port=0 |

---

### 4.3 Controller Health Status Poll（Opcode 0x2，raw bytes）

**Test 8.5**

```bash
# Inband IC=0 版本（cmd_byte0="04"）
mi -T inband -s $sanblaze -d $slot \
   -m 0408000002000000${contID}00871f000000 -v

# 含 filter bits
mi -T inband -s $sanblaze -d $slot \
   -m 0408000002000000${contID}00871f000080 -v
```

**回應長度計算（Inband 特有）：**
```bash
# Inband 回應長度計算方式不同
struct_len=$(( mi_rsp_length - 4096 ))   # 或
struct_len=$(( mi_rsp_length - 4088 ))   # 依 header 大小而定

# SMBus 版本的計算方式（供對比）：
struct_len=$(( mi_rsp_length - 12 ))
```

---

## 5. Inband Admin Commands（64-byte Capsule 格式）

這些命令使用完整的 64-byte NVMe Admin Capsule 透過 Inband 傳送。  
**用途：** 測試設備對「透過 MI Inband 傳送 Admin 命令」的**拒絕行為**（因為 spec 禁止）。

### 5.1 Get Features — Inband Capsule 格式

**Test 9.3**

```bash
mi -T inband -s $sanblaze -d $slot \
   -m 041000000a${cflgs_inband}${contID}000000000000000000000000000000000000000000000000${dlen_inband}00000000000000000000${subopcode_inband}0000000000000000000000000000000000000000000000 \
   $mi_length -v
```

**64-Byte Capsule Byte 解析：**

| Byte | 值 | 欄位 | 說明 |
|------|-----|------|------|
| 0 | `04` | IC + MsgType | IC=0, MsgType=0x4（Inband）|
| 1 | `10` | Flags | Payload length flags |
| 4 | `0a` | Admin Opcode | Get Features (0x0A) |
| 5 | `${cflgs_inband}` | Control Flags | Feature selection flags |
| 6–7 | `${contID}` | Controller ID | 目標 Controller（LE）|
| 8–27 | `0000...` | Reserved | NVMe CDB Reserved |
| 28–29 | `${dlen_inband}` | Data Length | `0010`=4096B, `0800`=8B, `0002`=512B |
| 40 | `${subopcode_inband}` | FID | Feature Identifier |
| 41–63 | `0000...` | Reserved | |

**常用 `dlen_inband` 值：**

| 值 | 長度 | 說明 |
|----|------|------|
| `0010` | 4096 bytes | Host Metadata 類 FID |
| `0800` | 8 bytes | Timestamp (FID 0x0E) |
| `0200` | 512 bytes | Host Behavior (FID 0x16) |

---

### 5.2 Set Features — Inband Capsule 格式

**Test 9.3**

```bash
mi -T inband -s $sanblaze -d $slot \
   -m 041000000901${contID}000000000000000000000000000000000000000000000000000000000000000000000000${subopcode_inband}0000000000000000000000000000000000000000000000 \
   -v
```

**Byte 解析：**

| Byte | 值 | 欄位 | 說明 |
|------|-----|------|------|
| 0 | `04` | IC + MsgType | IC=0，Inband |
| 1 | `10` | Flags | |
| 4 | `09` | Admin Opcode | Set Features (0x09) |
| 5 | `01` | Control Flags | Save bit |
| 6–7 | `${contID}` | Controller ID | |
| 40 | `${subopcode_inband}` | FID | Feature Identifier |

---

### 5.3 Get Features — Namespace Metadata（FID=0x7F）

**Test 10.3**

```bash
# Get Features FID=0x7F（Namespace Metadata）via Inband
mi -T inband -s $sanblaze -d $slot \
   -m 041000000a01${contID}0000000000000000000000000000000000000000000000000010000000000000000000007f0000000000000000000000000000000000000000000000 \
   -l 4096 -v
```

**Byte 解析重點：**

| Byte | 值 | 說明 |
|------|-----|------|
| 4 | `0a` | Get Features |
| 5 | `01` | Selection |
| 6–7 | `${contID}` | Controller ID |
| 28–29 | `0010` | Data Length = 4096 bytes |
| 40 | `7f` | FID = Namespace Metadata |

---

### 5.4 Set Features — Namespace Metadata（FID=0x7F）

**Test 10.3**

```bash
mi -T inband -s $sanblaze -d $slot \
   -m 041000000901${contID}0000000000000000000000000000000000000000000000001000000000000000000000007f0000000000000000000000000000000000000000000000${value_to_set} \
   -v
```

---

### 5.5 Get Features — Controller Metadata（FID=0x7E）

**Test 10.4**

```bash
mi -T inband -s $sanblaze -d $slot \
   -m 041000000a01${contID}0000000000000000000000000000000000000000000000000010000000000000000000007e0000000000000000000000000000000000000000000000 \
   -l 4096 -v
```

---

### 5.6 Set Features — Controller Metadata（FID=0x7E）

**Test 10.4**

```bash
mi -T inband -s $sanblaze -d $slot \
   -m 041000000901${contID}0000000000000000000000000000000000000000000000001000000000000000000000007e0000000000000000000000000000000000000000000000${value_to_set} \
   -v
```

---

### 5.7 Get Log Page — Persistent Event Log（LID=0x0D，帶 Retry）

**Test 9.2**

```bash
mi -T inband -s $sanblaze -d $slot \
   -m 841000000201${contID}ffffffff0000000000000000000000000000000000000000${length_hex}00000000000000000d${rae}17f000000000000000000000000000000000000000000 \
   -k 5 -v
```

**Byte 解析：**

| Byte | 值 | 說明 |
|------|-----|------|
| 0 | `84` | IC=1（此處 Inband Persistent Event Log 使用 IC=1）|
| 4 | `02` | Admin Opcode = Get Log Page |
| 5 | `01` | Control flags |
| 6–7 | `${contID}` | Controller ID |
| 28–29 | `${length_hex}` | Data transfer length |
| 40 | `0d` | LID = Persistent Event Log (0x0D) |
| 41 | `${rae}` | RAE bit |
| 42–43 | `17f0` | LSI |

**特殊參數 `-k 5`：** 設定 5 秒 timeout（Persistent Event Log 回應可能較慢）

---

## 6. Inband 特有行為差異

### 6.1 Endpoint Discovery 跳過

所有測試腳本在偵測到 `mi_transport == "inband"` 時，自動跳過 Endpoint Discovery：
```bash
if [ $mi_transport == "inband" ]; then
    # DoEndpointDiscovery 被跳過
    SKIPPED: This test isn't applicable to the MI inband transport
fi
```

### 6.2 Read Data Structure — 選用性處理

Inband 上的 Read Data Structure 是選用（Optional）的。若設備回傳錯誤：
```bash
if [ $mi_transport == "inband" ]; then
    OptionalNVMEECommandSkippedMessageOrError "$cmd_error_descr" 0
    # → 記錄為 SKIP 而非 ERROR
fi
```

### 6.3 回應長度計算差異

```bash
# SMBus 版本
struct_len=$(( mi_rsp_length - 12 ))

# Inband 版本（response 內含 4096-byte NVMe Admin response buffer）
struct_len=$(( mi_rsp_length - 4096 ))
# 或帶 header 偏移：
struct_len=$(( mi_rsp_length - 4088 ))
```

### 6.4 Inband Capability 確認（MI v1.2 以上）

```bash
if [ $mi_transport == "inband" ] && [ $mi_ver_num -ge 12 ]; then
    GetMICmdSupportOverInband 0   # 0 = Read Data Structure opcode
    if (( ! $csupp_bit )); then
        SKIPPED: Can't continue the test
    fi
fi
```

---

## 7. SMBus vs. Inband 命令對照表

| 命令 | SMBus 版本 | Inband 版本 | 差異 |
|------|-----------|-------------|------|
| **Read Data Structure** | `mi -t 0x1 -T smbus ... 0x0 0x0 -v` | `mi -t 0x1 -T inband ... 0x0 0x0 -v` | 語法相同，Transport 不同 |
| **Config Get Health Status** | `mi -t 0x1 -T smbus ... 0x4 0x2 -p 0 -v` | `mi -T inband ... -m 04080000 04000000 02000000 00000000 -v` | Inband 需用 raw bytes（IC=0）|
| **Controller Health Poll** | `-m 84080000 02000000...` (IC=1) | `-m 04080000 02000000...` (IC=0) | 只有 Byte 0 不同 |
| **Get Features** | `mi -t 0x2 -T smbus ... 0xa 0x${FID} -n $ns -c $ctrl -v` | `mi -T inband ... -m 041000000a01 ${contID}...${FID}... -l 4096 -v` | Inband 使用 64-byte capsule |
| **Set Features** | `mi -t 0x2 -T smbus ... 0x9 0x${FID} ... -w $val -v` | `mi -T inband ... -m 04100000 0901 ${contID}...${FID}...${value}... -v` | 同上 |
| **Control Primitive（Replay）** | `mi -t 0x0 -T smbus ... 0x4 0x0 -v` | `mi -T inband ... -m 0400000004000000 -v` | **Inband 禁用，預期失敗** |
| **MCTP Get Endpoint ID** | `mi -t 0x10 -T smbus ... 0x2 -v` | **不適用（N/A）** | Inband 沒有 MCTP |
| **Admin via MI（msg_type=0x2）**| `mi -t 0x2 -T smbus ... 0xa 0x7F -v` | `mi -T inband ... -m 041000000a...7f... -v` | **Inband 禁用 MI 封裝，預期失敗** |

---

## 附錄：mi 命令 Inband 速查

```bash
# === 通用全域參數 ===
# -T inband    Transport = PCIe Inband
# -s $sanblaze SANBlaze IP
# -d $slot     Slot 號碼
# -v           Verbose 輸出

# === NVMe-MI Commands（-t 0x1 語法可用）===
mi -t 0x1 -T inband -s $sanblaze -d $slot 0x0 0x0 -v         # Read NVM Subsys Info
mi -t 0x1 -T inband -s $sanblaze -d $slot 0x0 0x3 -c $ctrl -v # Read Controller Info
mi -t 0x1 -T inband -s $sanblaze -d $slot 0x4 0x3 -p $port -v # Config Get TUS

# === Inband Raw Messages（IC=0, cmd_byte0=04）===
# Config Get Health Status Change
mi -T inband -s $sanblaze -d $slot -m 04080000040000000200000000000000 -v

# Controller Health Status Poll（IC=0）
mi -T inband -s $sanblaze -d $slot -m 0408000002000000${contID}00871f000080 -v

# === 64-byte Admin Capsule（測試禁用行為）===
# Get Features FID=0x7F
mi -T inband -s $sanblaze -d $slot \
   -m 041000000a01${contID}...7f... -l 4096 -v

# Persistent Event Log（帶 timeout）
mi -T inband -s $sanblaze -d $slot \
   -m 841000000201${contID}...0d${rae}... -k 5 -v

# === 禁用命令測試（預期回傳錯誤）===
# Control Primitive（禁用）
mi -T inband -s $sanblaze -d $slot -m 0400000004000000 -v   # FAIL expected

# IC=1 on Inband（規範違反）
mi -T inband -s $sanblaze -d $slot -m 84080000040000000200000000000000 -v  # FAIL expected
```
