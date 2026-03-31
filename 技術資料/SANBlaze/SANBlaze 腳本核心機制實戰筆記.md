這份筆記整理了撰寫與維護 SANBlaze [測試](../../Obsidian/測試.md)腳本時，最核心的執行生命週期與狀態控制機制。

---

## 1. 核心控制引擎：`checkState` 的角色與呼叫時機

`checkState` 是整個測試框架的「心跳」與「控制樞紐」。它不直接判定測試是否通過，但負責**監控進度、更新網頁 UI、以及接收外部指令 (暫停/停止)**。

> [!IMPORTANT]
> 任何需要耗時執行、或是需要跑多個 Pass 的腳本，都**必須**在特定的地方呼叫 `checkState`！

### 呼叫的 3 大關鍵時機與範例

#### 📍 A. 主迴圈前 (腳本初始化)
**目的：** 等待所有同行腳本 (Peer scripts) 就緒同步起跑，並設定計時器初始值。
```bash
# 腳本剛開始，準備進入迴圈前，必須先呼叫一次
checkState

while (( keeprunning )); do
    ...
```

#### 📍 B. 發生 `break` 提前跳出前
**目的：** 如果因為硬體不支援或發生致命錯誤，必須中斷這個 Pass 時，需要在 `break` 之前呼叫，好讓網頁 UI 知道「這個 Pass 已經提早結束了」。
```bash
DetermineSecuritySupport
if (( $skip_test )); then
    doLogEcho "SKIPPED: Security 不支援，跳過測試。"
    checkState      # <--- 同步中斷狀態給 GUI
    break           # <--- 跳出 while 迴圈
fi
```

#### 📍 C. 每個 Pass 結尾 (最重要)
**目的：** 當這輪測試邏輯跑完，`checkState` 會更新進度條 `%complete`，並計算剩餘等待時間 (Passtimer)。
```bash
while (( keeprunning )); do
    # ... 執行一大堆硬碟讀寫測試 ...

    # 這一行絕對不能刪除！這是每一個 Pass 結束的打卡點
    checkState      
done
```

---

## 2. 生命週期與總開關：`keeprunning` 變數

`keeprunning` 是一個全域旗標 (Flag)，扮演著腳本的**「煞車線」**。

> [!WARNING]
> 一定要配置 `while (( keeprunning )); do` 迴圈。如果寫成 `while true; do` 或完全不加迴圈，腳本將變成無法從網頁停止的「殭屍程序 (Zombie Process)」，且無法遵守 GUI 設定的執行次數 (Passes)。

### `keeprunning` 什麼時候會變成 0 (強制中斷)？

1. **錯誤超標：** `checkState` 發現累積的 `errors` 大於 `allowederrors` (預設為 0)。
2. **外部強停：** 使用者在 Web GUI 點擊 **STOP** 或 **ABORT**。
3. **完成任務：** 測試已經完成了使用者設定的所有 `passes` 數量。
4. **夥伴失聯：** 在「初始化階段」等待其他腳本同步超過 600 秒。

---

## 3. 測試判定機制：Pass / Fail / Warning / Skipped

SANBlaze 判定測試結果，**不是**依靠 `checkState` 一眼決定，而是依賴「實體檔案累加器」 (`errors`, `warnings`, `skipped`)。

> [!TIP]
> 這些函式（如 `countErrors`）呼叫後**不會立刻中止腳本**，它們只做一件事：把數字 +1 寫入檔案。真正終止腳本的工作是交給下一次呼叫的 `checkState` 去判斷的。

### 實際範例對照表

#### ❌ 範例：發生錯誤 (Failed)
```bash
io_result=`io /iport0/target0lun0 Read ...`
if (( $? )); then
    doLogEcho " ERROR: IO Read Command failed"
    countErrors 1     # 錯誤數 +1。因為預設 allowederrors=0，這將導致測試 Failed
    checkState        # checkState 看到 errors=1，立刻將 keeprunning 設為 0
    break             # 腳本跳出迴圈
fi
```

#### ⚠️ 範例：非致命警告 (Warning)
```bash
if (( $temperature > 80 )); then
    doLogEcho "WARNING: 溫度稍微偏高"
    countWarnings 1   # 警告數 +1，但不影響 errors
    # 不呼叫 break，讓腳本繼續往下跑 !
fi
```

#### ⏭️ 範例：條件未滿足跳過 (Skipped)
```bash
if [[ $ZNS_support == 0 ]]; then
    doLogEcho "SKIPPED: 此 LUN 不支援 ZNS"
    skip_test=1       # 自訂旗標，告訴主程式要跳過
    countSkipped 1    # 跳過數 +1
fi
```

#### ✅ 範例：完美通過 (Passed)
什麼計數器都不要呼叫！順順地把 `while` 迴圈跑完，結果自然就是 Passed。

---

## 4. 最終收尾裁判：`doExit()` 運作邏輯

`doExit 0` 是所有腳本的終點站。不管腳本是正常跑完，還是中途 `break` 跳出，最後一定會進入 `doExit()` 來宣判成績。

> [!NOTE]
> `doExit 0` 裡面的 `0` 只是給 Linux Shell 系統看的 Exit Code。對於 SANBlaze 系統而言，**真正的測試結果是 `doExit` 內部自己算出來的**，跟你傳 0 還是傳 1 無關。

### `doExit` 的判斷優先順序 (Decision Tree)

1. **是否有指定 `$EXITSTATUS`？** 
   若腳本或 `checkState` 已經提前寫入 `EXITSTATUS="Failed"`，則直接尊重該結果，不再看計數器。
2. **`errors > allowederrors`？** 
   是的話，強制判定為 **`Failed`**。
3. **使用者按下中斷？** 
   是的話，判定為 **`Stopped`**。
4. **有警告嗎 (`warnings > 0`)？**
   是的話，判定為 **`Warning`**。
5. **有跳過嗎 (`skipped > 0`)？**
   是的話，判定為 **`Skipped`**。
6. **以上皆非！**
   恭喜，完美 **`Passed`**。

---

## 5. 狀態通訊與 Bash 腳本特性 (進階觀念)

### A. 全域變數的共用 (`$skip_test`)
在 SANBlaze 腳本中，常會透過 `source` 載入 Library（例如 `NVMe_TCG_Library.sh`）。
因為 `source` 會在同一個 Shell 環境中執行，所以 Library 中的 Function 可以直接修改主程式的變數。

```bash
# 位於主腳本 (UCT_01)
skip_test=0                   # 初始化

# 呼叫 Library (NVMe_TCG_Library.sh) 的函式
DetermineSecuritySupport      # 這個函式內部只要執行 `skip_test=1`

# 主腳本直接讀取全域變數
if (( $skip_test )); then     # 這裡就會抓到 1，進而觸發跳出邏輯
    checkState
    break
fi
```

### B. 安全字串比對與轉小寫：`[ "x${state,,}" != "xstopped" ]`
這是 `SANBlaze_Test_Include.sh` 裡極度經典的防呆語法。

1. **`${state,,}` (雙逗號)**：
   Bash 4.0 以上的功能。強制將變數 `$state` 裡所有的字母轉換為**小寫** (例如 `STOPPED` 會變成 `stopped`)，用來做忽略大小寫的比對 (Case-insensitive)。
2. **`"x..." != "x..."` (加前綴字)**：
   為了防止 `$state` 剛好沒有值（String is empty）或是有特殊符號而導致 Bash Parsing 壞掉。
   * 若 `$state` 為空，原本 `[ != "stopped" ]` 會報錯。
   * 改寫後變成 `[ "x" != "xstopped" ]`，語法完全合法且安全。
