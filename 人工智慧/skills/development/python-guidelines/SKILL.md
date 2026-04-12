---
name: python-guidelines
description: 執行 Python 專案開發，涵蓋架構設計與代碼審查，並嚴格遵循團隊開發參考規範。
---

# Python 開發規範 (Development Guidelines)

本 Skill 作為 Python 專案的開發規範執行者，負責確保程式碼品質、架構合理性與交付標準。

## 1. 參考規範總覽 (References Overview)

在進行任何實作或架構決策前，請務必查閱 `references/` 目錄下的專屬指南。這些指南定義了專案在各個工程維度上的標準與最佳實踐：

| 檔案名稱 | 職責說明 (Responsibility) |
| :--- | :--- |
| `core.md` | 架構設計原則、介面解耦策略、領域錯誤處理與日誌紀錄標準。 |
| `linting.md` | 靜態型別分析 (`mypy`) 與程式碼排版風格 (`ruff`) 要求。 |
| `env.md` | 專案依賴管理 (`uv`) 與環境變數、系統配置的存取架構。 |
| `testing.md` | 動態測試的結構組織、AAA 模式標記與 Fixture 隔離策略。 |
| `checklist.md` | 交付程式碼前必須通過的內部自我檢核與防線驗證清單。 |

## 2. 核心開發工作流 (Core Workflow)

在處理使用者的開發任務時，請遵循以下標準作業程序 (SOP)：

1. **規範查閱 (Review Standards)**
   - 針對任務涉及的領域（如：需要設定 DB 連線就看 `env.md`，需要定義架構就看 `core.md`），優先讀取對應的參考文件以同步專案上下文。
2. **實作與驗證 (Implement & Verify)**
   - 撰寫符合高標準（如：無裸露異常、無 print、嚴格型別）的業務邏輯程式碼。
   - 所有核心邏輯的變更，必須附帶符合隔離標準的 `pytest` 單元測試。
3. **交付前審查 (Pre-Delivery Review)**
   - 在交付最終程式碼前，啟動並閱讀 `checklist.md`。
   - 將該清單作為你的**內部思考驗證標準 (Meta-Prompt)**，全域掃描你即將交付的程式碼。確保所有規範皆已落實後，再行輸出最終結果。
