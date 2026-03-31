
## 📦 模組與匯入方式
所有與硬體電源、PCI 控制掛鉤的 API，皆實作於 SANBlaze Python API 核心庫：
`sanblaze_py_api.sanblaze_test_api_actions`

在撰寫自定義的 Python 測試腳本時，請直接從該模組引入這些控制函式。

---

## ⚙️ 核心 API 功能與底層實作

### 1. `power_on(dut, fail_type='error')`
- **功能描述**：對指定的待測設備（DUT, Device Under Test）發送送電指令，並等待插槽電壓恢復。
- **使用情境**：欲將設備從徹底沒電（被關閉）的狀態重新喚醒。
- **底層原理**：利用 SANBlaze 內建指令 `sb_i2c -n <node> -d <slot> -f HP_PWREN -w 1` 開啟硬體的熱插拔電源 (Hot-Plug Power Enable)。送出後，程式會以輪詢方式不斷讀取電壓（執行 `sb_i2c -m`），待電壓升至 `3000mV` 以上視為送電成功。

### 2. `power_off(dut, fail_type='error')`
- **功能描述**：對指定的待測設備進行硬體斷電。
- **使用情境**：測試前置的狀態清理準備，或模擬系統電源關閉狀態。
- **底層原理**：呼叫 `sb_i2c -f HP_PWREN -w 0` 切斷硬體電源供應。同樣監視其電壓直至降落到 `1000mV` 以下，方視為成功徹底斷電。

### 3. `power_cycle(dut, wait=True, fail_type='test', ready_wait_time=127.5, vf=0)`
- **功能描述**：安全地重新啟動設備 (Graceful Restart)。這是一個複合動作，旨在避免作業系統層（如 Linux Kernel）因為突然失去 PCIe 裝置而崩潰或卡死。
- **使用情境**：常規的設備重啟測試，例如重設控制器狀態 (Controller Reset)，或是熱插拔 (Hot-plug) 的正常復原測試。
- **底層動作步驟**：
  1. 呼叫 `remove_from_pci(dut)`（針對系統層級安全卸載，系統會執行 `echo power_off=0000:<PCI位址> > /proc/vlun/nvme`）
  2. 呼叫 `power_off(dut)`（物理斷電）
  3. 呼叫 `power_on(dut)`（物理送電）
  4. 如果 `wait=True`，呼叫 `wait_for_controller(dut)` 確認 NVMe 控制器的暫存器 (CC.EN / CSTS.RDY) 進入 Ready 狀態。

### 4. `surprise_power_cycle(dut, fail_type='test')`
- **功能描述**：模擬無預警斷電 (Surprise Power Loss, SPL) 後的重啟。
- **使用情境**：專門針對 SPOR (Sudden Power Off Recovery)、Dormant Data TTR 或 OCP Datacenter SSD 等資料寫入與斷電容錯相關的極端測項。
- **底層動作步驟** (注意：順序與正常重啟刻意相反)：
  1. 呼叫 `power_off(dut)`（直接從硬體端切斷電源，絕不給磁碟韌體任何 Flush Cache 或善後的機會）
  2. 呼叫 `remove_from_pci(dut)`（替 Linux 系統擦屁股，強制移除作業系統中懸空的殘留 PCI 裝置，避免系統 Kernel Panic）
  3. 呼叫 `power_on(dut)`（重新送電啟動）

### 5. `power_cycle_quarch(dut, ...)` [選配擴充]
- **功能描述**：強制透過外接的 Quarch 儀器執行極度精確的物理斷開/送電。如果您在設定檔 `/virtualun/python.conf` 綁定了 Quarch 裝置，呼叫原生的 `power_cycle` 時，系統會自動切換路由，使用這個函式來控制實體層的針腳開關。

---

## 💻 虛擬範例腳本 (如何在 Python 中呼叫)

以下示範如何在以 Python 撰寫的 SANBlaze 測試腳本中，調用這些 API 來達成斷送電的情境測試：

```python
from sanblaze_test_api_actions import power_cycle, power_on, power_off, surprise_power_cycle
from sb_logger import logging
import time

def my_power_test(dut):
    # ==========================================
    # 範例 1：執行一次正常的 Power Cycle 並等待它完成啟動
    # ==========================================
    logging.note("準備進行常規 Power Cycle 測試")
    # wait=True 表示送電後會阻塞程式，直到控制器 NVMe 狀態回報為 RDY
    power_cycle(dut, wait=True, fail_type='warning')
    logging.info("常規開關機結束且 Controller 已經 Ready")

    # ==========================================
    # 範例 2：執行一次非預期意外掉電 (Surprise Power Loss)
    # ==========================================
    logging.note("開始模擬意外掉電 (Surprise Power Loss)")
    # 此 API 會殘酷地直接切斷硬體供電，不預先移除 PCI 註冊
    surprise_power_cycle(dut, fail_type='error')
    logging.info("非預期掉電重啟完成，準備驗證磁碟的資料復原狀態...")
    
    # ==========================================
    # 範例 3：拆解動作，單獨控制斷電與送電
    # ==========================================
    logging.note("手動斷電 (Power Off)...")
    power_off(dut)
    
    # 在徹底斷電的狀態下可以做的事（例如等待電容徹底放電、等待第三方儀器抓取隔離訊號）
    logging.detail("等待 10 秒鐘讓磁碟完全放電")
    time.sleep(10)
    
    logging.note("手動重新送電 (Power On)...")
    power_on(dut)
```