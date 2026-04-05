---
name: zh-tw-localizer
description: 專門用於批量掃描指定目錄，並將檔名（包含簡體中文、日文漢字/假名、英文句子）智慧化轉為台灣標準繁體中文。支援「預覽 -> 確認 -> 執行」流程，並嚴格遵循技術術語保留原則。
disable-model-invocation: true
allowed-tools:
  - Read
  - Write
  - Bash(python *)
---

# 檔案本地化專家 (Traditional Chinese File Localizer)

## 1. 何時使用 (When to use)
- 當下載的資源檔名包含「簡體中文」或「日文假名」，需要標準化為繁體時。
- 當大量檔案名稱為雜亂的英文描述，希望透過 AI 翻譯成易讀的繁體中文時。
- 需要在正式改名前進行「人工預覽」，以確保翻譯品質與檔名衝突。

## 2. 先決條件 (Prerequisites)
- **環境**: Python 3.10+
- **必要套件**: `pip install opencc deep-translator`
- **系統權限**: 需具備目標資料夾的讀寫權限。

## 3. 命名準則與限制 (Rules & Constraints)
- **核心策略**: 
  - 優先使用 `OpenCC (s2twp)` 處理簡轉繁，確保用語符合台灣習慣。
  - 對於英文/日文內容，使用 `Google Translator` 並優化語意。
- **術語保留**: 
  - 嚴格保留英文技術術語（如：AI, RAG, Agent, CLI, SDK, GPT）。
  - 保留檔名中的日期、版本號（如：v1.2, 2026-04-03）。
  - 除非使用者明確要求，否則不翻譯專業縮寫。
- **安全性**:
  - **嚴禁修改副檔名**（如 .mp4, .pdf 必須保持原樣）。
  - 自動剔除 Windows 系統禁用的特殊字元：`\ / : * ? " < > |`。
  - 偵測重複命名：若新檔名已存在，自動加上 `_1`, `_2` 序號。

## 4. 腳本操作範例 (Script Usage)
該技能依賴內部腳本 `scripts/localizer.py`，其參數說明如下：

**預覽清單 (Dry Run)**
```bash
# 輸出範例: 一張包含 [舊檔名 | 建議新檔名] 的 Markdown 表格。
python scripts/localizer.py --dir "C:\Path" --ext ".mp4" --preview
```

**正式執行 (Apply)**
```bash
# 正式對檔案進行重新命名
python scripts/localizer.py --dir "C:\Path" --ext ".mp4" --apply
```

**指定僅進行簡繁轉換 (S2T Only)**
```bash
# 僅將簡體中文檔名轉為繁體，跳過純英文/日文翻譯
python scripts/localizer.py --dir "C:\Path" --mode s2t --preview
```

## 5. 執行流程 (Standard Workflow)
當使用者啟動此技能時（例如：使用 `/zh-tw-localizer` 指令）：

1. **解析輸入**: 接收 `$0` (目錄路徑) 與 `$1` (檔案類型，如 .mp4) 及其他參數。
2. **預覽階段 (Dry Run)**: 
   - 呼叫 `python scripts/localizer.py --dir $0 --ext $1 --preview`。
   - 將產出的「原檔名 vs 新檔名」表格呈現給使用者確認。
3. **人工審核**: 詢問使用者：「是否確認以上更名操作？(Y/N)」。
4. **正式執行**: 
   - 獲得許可後，呼叫 `python scripts/localizer.py --dir $0 --ext $1 --apply`。
   - 報告成功與失敗的數量。
