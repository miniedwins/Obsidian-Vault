
> 作者：Antigravity AI Assistant ｜ 日期：2026-08-13
> 目的：提供 NVMe-MI 測試團隊評估將 Shell 腳本遷移至 Python Module 的完整技術分析

---

## 目錄

1. [MCTP 掉包與重送機制測試能力](NVMe-MI%20Python%20Module%20Analysis.md#q1)
2. [MCTP 封包 MIC 計算責任歸屬](NVMe-MI%20Python%20Module%20Analysis.md#q2)
3. [MIC 錯誤檢查責任歸屬](NVMe-MI%20Python%20Module%20Analysis.md#q3)
4. [Python Module 封裝可行性評估](NVMe-MI%20Python%20Module%20Analysis.md#q4)
5. [程式開發建議](NVMe-MI%20Python%20Module%20Analysis.md#q5)
6. [結論與建議](NVMe-MI%20Python%20Module%20Analysis.md#conclusion)

---

## Q1：MCTP 掉包/重送機制，可以測試嗎？ {#q1}

### 結論：**完全可以測試，且現有腳本已覆蓋多種場景**

### 目前腳本可以測試的 MCTP 封包行為

| 測試項目 | 腳本 | 方式 |
|---|---|---|
| SOM=0 EOM=0（middle packet）設備應 silently drop | `01.04.01_MCTPBadPacket1` | `-H` 注入特定 MCTP Header |
| SOM=0 EOM=1（end packet）設備應 silently drop | `01.04.01_MCTPBadPacket1` | `-H 01{eid}{eid}48` |
| Packet Sequence Number 驗證 | `01.02_MCTPPacketSeqNum` | 逐封包讀 `smbus_rsp` raw byte |
| Response Message Replay（全部重傳） | `07.04_RespMessageReplay` | Control Primitive opcode=0x4 |
| Response Replay Offset（指定從第 N 個封包重傳）| `07.05_RespReplayOffset` | Control Primitive + RRO 欄位 |
| Replay 封包數量驗證 | `07.05` | 計數 `smbus_rsp` 行數 |
| Replay 後 SOM bit 驗證 | `07.05` / `07.08` / `07.09` | 解析 `smbus_rsp` raw byte bit7 |

### 關鍵技術細節

`mi` 命令透過 **`-H` 參數**直接注入自訂 MCTP Header，繞過正常組包邏輯：

```bash
# 注入 SOM=0 EOM=0（模擬中間封包，測試設備是否 drop）
mi -t 0x10 -T smbus -s $sanblaze -d $slot 0x2 \
   -H 01${dest_eid}${src_eid}08 -v > $file1
#                               ^^
#               MCTP Header byte 4: 0x08 = 0000_1000
#               bit7(SOM)=0, bit6(EOM)=0

# 驗證設備確實 drop 封包（沒有 mi_rsp: 出現）
CheckMCTPCommandDropStatus 0
```

### MCTP 重傳的觸發機制

> [!IMPORTANT]
> MCTP 協定**本身沒有自動重傳**（不像 TCP）。Replay 必須由**主機端主動發送 Control Primitive: Replay**。
> 這是 Test 7.x 系列的核心測試目標：驗證設備正確執行 Replay 行為。

```
主機（SANBlaze）                        設備（DUT）
     |--- VPD Read Request ------------->|
     |<-- MCTP pkt[0] ------------------|  SOM=1
     |<-- MCTP pkt[1] ------------------|
     |   （假設主機決定要重傳第3~5包）
     |--- Control Primitive Replay(RRO=2)->|
     |<-- ACK ---------------------------|
     |<-- MCTP pkt[2] ------------------|  SOM=1 (Replay 首包標記)
     |<-- MCTP pkt[3] ------------------|
     |<-- MCTP pkt[4] ------------------|  EOM=1
```

---

## Q2：每個 MCTP 封包需要自己計算 MIC 嗎？ {#q2}

### 結論：**不需要，`mi` 工具自動處理 MIC 計算**

### MIC vs PEC 的層次區分

| 層次 | 保護範圍 | 誰計算 | 你需要處理？ |
|---|---|---|---|
| SMBus PEC | 單個 SMBus 幀 | 硬體/驅動 | 完全透明，不需處理 |
| MCTP CRC | 無封包層 CRC | N/A | N/A |
| NVMe-MI MIC | 整個 Message | mi 工具 | 自動處理，不需計算 |

### MIC（Message Integrity Check）規格

- **位置**：NVMe-MI Message 的最後 4 bytes（CRC-32C）
- **保護範圍**：從 Message Header 到 Message Body（不含 MIC 本身）
- **演算法**：CRC-32C（Castagnoli polynomial）

### `mi` 工具的 MIC 控制介面

`-M` 參數允許**故意送出錯誤的 MIC** 以測試設備的拒絕行為：

```bash
# 正常送出（mi 自動計算正確 MIC）
mi -t 0x1 -T smbus -s $sanblaze -d $slot 0x4 0x3 -p 0 -v

# 故意送壞 MIC（-M 1 = 送錯誤 MIC）
# 用於 Test 5.6 驗證設備是否 silently drop 掉 bad MIC 的請求
mi -t 0x1 -T smbus -s $sanblaze -d $slot 0x4 0x3 -p 0 -M 1 -v
```

> [!NOTE]
> Script 的任務是「觀察結果」：當送出壞 MIC 時，`mi_rsp:` 應該不出現（設備 silent drop），
> 若仍然有 response，則報告 `ERROR`。計算本身由 `mi` 工具處理。

---

## Q3：MIC 錯誤檢查，需要自行驗證嗎？ {#q3}

### 結論：**不需要自行計算，但需要判斷「設備行為是否符合規格」**

### 兩種不同的 MIC 驗證場景

#### 場景一：驗證設備「拒絕」壞 MIC 的請求

```bash
# 送出 bad MIC（-M 1）
mi ... -M 1 -v > $file1

# Script 只需確認設備 silently drop（無 mi_rsp: 出現）
ProcessFile_mi $file1 $file2 $file3
if (( $mi_rsp_flag )); then
    # 有回應 = 設備沒有正確拒絕 -> ERROR
    echo "ERROR: Command wasn't silently dropped"
    countErrors 1
else
    # 無回應 = 設備正確拒絕 -> PASS
    echo "DETAIL: Command was silently dropped"
fi
```

#### 場景二：驗證設備「送出」的 Response MIC 是否正確

這個場景在現有腳本中**是間接驗證的**：
`mi` 工具在收到 Response 時已驗證 MIC，若 MIC 錯誤，`mi` 工具不會產生 `mi_rsp:` 區段，
命令返回值 `$?` 也會非零。Script 透過 `$?` 和 `mi_rsp_flag` 間接確認 MIC 正確。

```bash
mi ... -v > $file1
i=$?  # 非零代表 mi 工具本身認為 response 有問題（包含 MIC 失敗）

if [ $i != 0 ]; then
    cmd_pass=0
fi
```

### IC bit（Integrity Check bit in Message Header）

不同於 MIC（4 byte CRC），IC bit 是 NVMe-MI Message Header 的 bit7：

```
NVMe-MI Message Header Byte 0:
Bit 7: Integrity Check Bit (IC)  <- 告知設備這個 message 有附 MIC
Bit 6-0: Message Type
```

- `IC=1`：Message 末尾附 MIC（4 bytes CRC-32C）
- `IC=0`：不附 MIC，設備應直接 drop（Out-of-band 要求）

透過 `-m` 直接控制 Header byte 測試這個行為：

```bash
# IC=1（正常，byte0 = 0x84 = 1000_0100）
mi -T $mi_transport -s $sanblaze -d $slot -m 84080000040000000200000000000000 -v

# IC=0（故意清除，byte0 = 0x04 = 0000_0100，設備應 drop）
mi -T $mi_transport -s $sanblaze -d $slot -m 04080000040000000200000000000000 -v
```

---

## Q4：Python Module 封裝可行性評估 {#q4}

### 整體評估

| 面向 | 評估 | 說明 |
|---|---|---|
| 技術可行性 | 高 | SANBlaze 已有 Python API 架構 |
| 工程複雜度 | 中高 | mi 命令 output 解析是核心難點 |
| MIC/PEC 計算 | 免實作 | mi 工具已封裝，只需 subprocess 呼叫 |
| MCTP Header 注入 | 可行 | 透過 `-H` / `-M` 參數傳遞 |
| 測試邏輯遷移 | 需重構 | Shell 的 regex 解析需改寫成 Python 解析 |

### 架構觀察：SANBlaze 已有 Python 基礎

```
sanblaze_py_api/
├── api_core.py                   # 核心 API（REST + subprocess 已有）
├── sanblaze_test_api.py          # 測試 API 框架
├── sanblaze_test_api_util.py     # execute_subprocess() 已存在
└── sanblaze_test_api_actions.py  # 各種 action（subprocess.run 模式）
```

`execute_subprocess()` 在 `sanblaze_test_api_util.py:L1576` 已實作，
這意味著**呼叫 `mi` 命令可以直接用既有的 `execute_subprocess()` 完成**。

### 可行路徑對照

```
Shell 腳本                    Python Module
──────────                    ──────────────
mi ... -v > $file1   ->   output = subprocess.run(['mi', '-t', '0x1', ...])
ProcessFile_mi()     ->   parse_mi_response(output)      # 新實作
ConvertHexToDecimal  ->   int(bytes_str, 16)              # Python 原生
grep / cut / xxd     ->   re.search() / struct.unpack     # Python 原生
countErrors 1        ->   add_error() / fail_test()       # 已有框架函數
```

### 困難點分析

#### 困難點 1：mi 命令 output 解析（最大難點）

`mi -v` 輸出格式包含三個區段，需要分別解析：

```
smbus_req[0]: 20 08 01 08 C8 01 81 00 00 00 ...  <- MCTP Request Raw
smbus_rsp[0]: 10 08 01 C8 08 80 00 08 4C ...      <- MCTP Response Packet 1
smbus_rsp[1]: 10 08 01 C8 ...                      <- MCTP Response Packet 2
mi_rsp:                                            <- NVMe-MI Response 起始 marker
01 00 00 00 00 00 ...                              <- NVMe-MI Message bytes
mi_rsp len: 8                                      <- 長度
Response Status: 00h                               <- Human-readable
Number of Ports: 2
```

```python
# Python parser 範例架構
class MiCommandOutput:
    def __init__(self, raw_output: list[str]):
        self.smbus_req_packets = []   # List[List[int]]  MCTP Request
        self.smbus_rsp_packets = []   # List[List[int]]  MCTP 封包層
        self.mi_rsp_bytes = []        # List[int]        NVMe-MI Message 層
        self.mi_rsp_len = 0
        self.response_status = None
        self.human_readable = {}      # {"Number of Ports": "2", ...}
        self._parse(raw_output)

    def _parse(self, lines):
        in_mi_rsp = False
        for line in lines:
            if line.startswith('smbus_req['):
                self.smbus_req_packets.append(self._parse_hex_line(line))
            elif line.startswith('smbus_rsp['):
                self.smbus_rsp_packets.append(self._parse_hex_line(line))
            elif line.startswith('mi_rsp:'):
                in_mi_rsp = True
            elif in_mi_rsp and line.startswith('mi_rsp len:'):
                self.mi_rsp_len = int(line.split(':')[1].strip())
                in_mi_rsp = False
            elif in_mi_rsp:
                self.mi_rsp_bytes.extend(self._parse_hex_line(line))
```

#### 困難點 2：MCTP Header Bit 解析（Python 更直觀）

```python
# Shell 做法（繁瑣）
# som_byte_bin=$(printf "\x${som_byte}" | xxd -b | cut -d ' ' -f 2)
# re="(.)(.)......"
# [[ $som_byte_bin =~ $re ]]

# Python 做法（清晰直觀）
def parse_mctp_flags(byte_val: int) -> dict:
    return {
        'SOM':    (byte_val >> 7) & 1,
        'EOM':    (byte_val >> 6) & 1,
        'TO':     (byte_val >> 5) & 1,
        'PktSeq': (byte_val >> 4) & 0b11,
    }

flags = parse_mctp_flags(0xC0)  # SOM=1, EOM=1, PktSeq=0
```

#### 困難點 3：`mi` 命令依賴 SANBlaze 硬體平台

> [!WARNING]
> `mi` 是 SANBlaze 平台的 **proprietary binary**，只能在 SANBlaze 測試機上執行。
> Python Module 是「在 SANBlaze 平台上的 wrapper」，不是跨平台的純 Python NVMe-MI 實作。
> 若未來需要脫離 SANBlaze 環境，則需要評估直接用 Python 實作 SMBus/MCTP Stack。

#### 困難點 4：檔案型 IPC（`/iport`、`/proc`）

目前腳本大量讀取 SANBlaze 的 `/iport{port}/target{target}` proc 檔案，
Python 可以用 `open()` + `re` 直接讀這些檔案，這部分遷移是直接的。

---

## Q5：程式開發建議 {#q5}

### 建議策略：漸進式三層封裝

```
Phase 1（短期 2~3 週）：薄層 Wrapper
Phase 2（中期 1~2 個月）：完整 Python Module
Phase 3（長期 3 個月以上）：pytest Test Suite Framework
```

### Phase 1：薄層 Wrapper 程式碼範例

```python
# nvme_mi_wrapper.py
import subprocess
from dataclasses import dataclass, field
from typing import Optional
import re


@dataclass
class MCTPPacket:
    """代表一個 MCTP 封包的 raw bytes 及解析後的 Header 欄位"""
    raw_bytes: list = field(default_factory=list)
    som: int = 0
    eom: int = 0
    tag_owner: int = 0
    pkt_seq: int = 0


@dataclass
class MiResponse:
    """mi 命令的解析結果"""
    success: bool = False
    mctp_packets: list = field(default_factory=list)
    mi_rsp_bytes: list = field(default_factory=list)
    mi_rsp_len: int = 0
    response_status: Optional[int] = None
    human_readable: dict = field(default_factory=dict)


class NVMeMIClient:
    """封裝 mi 命令的 Python wrapper"""

    def __init__(self, transport: str, sanblaze: str, slot: str):
        self.transport = transport  # "smbus" | "vdm" | "inband"
        self.sanblaze = sanblaze
        self.slot = slot

    def _run_mi(self, *args, mctp_header=None, bad_mic=False):
        """執行 mi 命令並回傳解析後的 MiResponse"""
        cmd = ['mi', '-T', self.transport, '-s', self.sanblaze, '-d', self.slot, '-v']
        cmd.extend(args)
        if mctp_header:
            cmd.extend(['-H', mctp_header])
        if bad_mic:
            cmd.extend(['-M', '1'])
        result = subprocess.run(cmd, capture_output=True, encoding='utf-8')
        return self._parse_output(result.stdout.splitlines(), result.returncode)

    def _parse_output(self, lines, returncode):
        """狀態機解析 mi -v 的輸出"""
        resp = MiResponse()
        in_mi_rsp = False
        for line in lines:
            m = re.match(r'smbus_rsp\[(\d+)\]:\s*(.*)', line)
            if m:
                pkt = self._parse_mctp_packet(m.group(2))
                resp.mctp_packets.append(pkt)
            elif line.startswith('mi_rsp:'):
                in_mi_rsp = True
                resp.success = True
            else:
                m2 = re.match(r'mi_rsp len:\s*(\d+)', line)
                if m2:
                    resp.mi_rsp_len = int(m2.group(1))
                    in_mi_rsp = False
                elif in_mi_rsp:
                    resp.mi_rsp_bytes.extend(int(b, 16) for b in line.split())
                else:
                    m3 = re.match(r'Response Status:\s*([0-9a-fA-F]+)h', line)
                    if m3:
                        resp.response_status = int(m3.group(1), 16)
        return resp

    def _parse_mctp_packet(self, hex_str, pkt_seq_byte_idx=8):
        """解析 smbus_rsp 行的 hex bytes，提取 MCTP Header flags"""
        raw = [int(b, 16) for b in hex_str.split()]
        pkt = MCTPPacket(raw_bytes=raw)
        if len(raw) > pkt_seq_byte_idx:
            flags_byte = raw[pkt_seq_byte_idx]
            pkt.som       = (flags_byte >> 7) & 1
            pkt.eom       = (flags_byte >> 6) & 1
            pkt.tag_owner = (flags_byte >> 5) & 1
            pkt.pkt_seq   = (flags_byte >> 4) & 0b11
        return pkt

    # ── NVMe-MI Commands ─────────────────────────────────────────

    def get_endpoint_id(self):
        return self._run_mi('-t', '0x10', '0x2')

    def vpd_read(self, length=256):
        return self._run_mi('-t', '0x1', '0x5')

    def configuration_set_tus(self, port, size):
        return self._run_mi('-t', '0x1', '0x3', '0x3',
                            '-p', str(port), '-w', f'{size:08x}')

    def control_primitive_replay(self, rro=0):
        return self._run_mi('-t', '0x0', '0x4', hex(rro))

    def configuration_get(self, port, bad_mic=False):
        return self._run_mi('-t', '0x1', '0x4', '0x3',
                            '-p', str(port), bad_mic=bad_mic)

    def send_raw_message(self, raw_bytes_hex):
        """送出完整 raw bytes（對應 -m 參數）"""
        return self._run_mi('-m', raw_bytes_hex)
```

### Phase 2：完整 Python Module 結構設計

```
nvme_mi_python/
├── __init__.py
├── transport/
│   ├── smbus.py          # SMBus transport 封裝
│   ├── vdm.py            # PCIe VDM transport 封裝
│   └── inband.py         # Inband transport 封裝
├── mctp/
│   ├── packet.py         # MCTPPacket dataclass + 解析
│   ├── message.py        # MCTP Message 重組邏輯
│   └── flags.py          # SOM/EOM/PktSeq 位元操作
├── nvme_mi/
│   ├── client.py         # NVMeMIClient（mi 命令 wrapper）
│   ├── commands/
│   │   ├── mctp_ctrl.py  # MCTP Control Messages
│   │   ├── mi_cmds.py    # NVMe-MI Commands（Health Status, VPD, etc.）
│   │   └── admin_cmds.py # NVMe-MI Admin Commands（Identify, Get Log Page）
│   ├── response.py       # Response 解析
│   └── primitives.py     # Control Primitives（Replay, Pause, Resume）
├── verification/
│   ├── som_eom.py        # SOM/EOM 驗證邏輯
│   ├── mic.py            # MIC 相關驗證
│   ├── replay.py         # Replay 行為驗證
│   └── packet_count.py   # 封包數量驗證
└── tests/
    ├── test_01_mctp.py   # 對應 Test Group 1（MCTP）
    ├── test_05_integrity.py  # Test Group 5（Integrity）
    ├── test_07_replay.py     # Test Group 7（Replay）
    └── ...
```

### Phase 3：Test Case 實作範例（Test 7.5）

以下是 Test 7.5（Replay Offset）的 Python 版本：

```python
# tests/test_07_replay.py
import pytest
from nvme_mi_python.nvme_mi.client import NVMeMIClient
from sanblaze.sanblaze_test_api_util import add_error, step


@pytest.fixture
def mi_client(dut):
    """建立 NVMeMIClient fixture"""
    return NVMeMIClient(
        transport='smbus',
        sanblaze=dut.sanblaze,
        slot=dut.slot
    )


def test_7_5_response_replay_offset(mi_client):
    """
    Test 7.5: NVMe-MI Response Replay Offset (RRO)
    驗證帶 Offset 的 Replay 只回傳指定範圍的封包（pkt 3, 4, 5）

    Example:
        pytest tests/test_07_replay.py::test_7_5_response_replay_offset -v
    """
    # Step 1-2: Issue VPD Read (5 packets expected)
    with step("Issue VPD Read (256 bytes)"):
        vpd_resp = mi_client.vpd_read(length=256)
        assert vpd_resp.success, "VPD Read failed"
        if len(vpd_resp.mctp_packets) != 5:
            add_error(f"Expected 5 MCTP packets, got {len(vpd_resp.mctp_packets)}")

    # 記錄原始 Message Header 供後續比對
    original_header = vpd_resp.mctp_packets[0].raw_bytes[9:13]

    # Step 3: Issue Control Primitive Replay with RRO=2
    with step("Issue Control Primitive Replay (RRO=2)"):
        replay_resp = mi_client.control_primitive_replay(rro=2)
        assert replay_resp.success, "Replay command failed"

    # Step 4: Verify 3 packets were replayed (total - 1 ACK)
    with step("Verify 3 packets were replayed"):
        replayed_count = len(replay_resp.mctp_packets) - 1
        if replayed_count != 3:
            add_error(f"Expected 3 replayed packets, got {replayed_count}")

    # Step 5: Verify SOM=1 on first replayed packet
    with step("Verify first replayed packet has SOM=1"):
        first_pkt = replay_resp.mctp_packets[1]  # index 0 = ACK
        if first_pkt.som != 1:
            add_error(f"First replayed packet SOM={first_pkt.som}, expected 1")

    # Step 6: Verify Message Header matches original
    with step("Verify Message Header matches original response"):
        replayed_header = first_pkt.raw_bytes[9:13]
        if replayed_header != original_header:
            add_error(f"Header mismatch: expected {original_header}, got {replayed_header}")
```

---

## 結論與建議 {#conclusion}

### 技術摘要

| 問題 | 答案 |
|---|---|
| MCTP 掉包測試 | 可以，透過 `-H` 注入 bad SOM/EOM，或主動發 Replay Primitive |
| MIC 自行計算 | 不需要，`mi` 工具自動計算正確 MIC |
| MIC 錯誤自行檢查 | 不需要，透過 `-M 1` 觸發 bad MIC，觀察設備是否 silent drop |
| Python Module 可行性 | 高度可行，已有 `execute_subprocess` 基礎框架 |

### 給 NVMe-MI 團隊的建議

> [!IMPORTANT]
> **短期（立即可做，2~3 週）**：用 Python 的 `subprocess.run` 呼叫 `mi`，
> 實作 `MiCommandOutput` parser，此工作量可覆蓋所有 Shell 腳本的功能。

> [!TIP]
> **中期（1~2 個月）**：將 Shell Library 函數（`ProcessFile_mi`、`ConvertHexToDecimal`、
> `VerifyReservedFieldIsZero` 等）逐一轉為 Python class method，建立完整的 `NVMeMIClient`。

> [!NOTE]
> **長期（3 個月以上）**：建立 pytest-based 測試框架，讓每個 UNH-IOL Test Case
> 對應一個 Python test function，並整合 SANBlaze 的 `add_error`/`skip_test`/`step` 框架。

### 關鍵風險

1. **`mi` binary 依賴**：Python Module 無法脫離 SANBlaze 硬體平台獨立運作，這是架構上的根本限制。
2. **Output 格式穩定性**：若 SANBlaze 未來改變 `mi -v` 的輸出格式，所有 parser 需要跟著更新。
3. **Timing 敏感度**：部分測試依賴 `sleep`，需確認 Python 版本的計時行為與 Shell 一致。

### 優先建議詢問 SANBlaze 的問題

1. `mi` 命令是否支援 **JSON / structured output** 模式（避免 text parsing 的脆弱性）？
2. 是否有 `mi` 的 **Python binding 或 shared library**（最佳解，可直接 import 而非 subprocess）？
3. SANBlaze Python API（`api_core.py`）是否已有 **NVMe-MI 相關的 method** 尚未在腳本中使用？

---

*本文件由 AI Assistant 根據腳本分析自動生成，供 NVMe-MI 測試團隊參考討論。*
