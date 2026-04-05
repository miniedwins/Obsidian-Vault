# Python 環境與配置規範 (Environment & Configuration)

本規範旨在約束 AI 與開發者在變更專案依賴與讀取系統配置時的行為，嚴防依賴混亂與配置散落。

## 1. 依賴變更約束 (Dependency Management)

- **唯一合法工具 `uv`**：當開發過程中需要新增或移除套件時，**絕對禁止**使用 `pip`, `poetry` 或直接編輯 `requirements.txt`。
- **嚴禁手動改檔**：所有的依賴變更必須透過 `uv add <package>` 或 `uv remove <package>` 指令執行。嚴禁手動編輯 `pyproject.toml` 中的 dependencies 區塊，以確保 `uv.lock` 永遠與專案狀態保持絕對一致。
- **開發依賴隔離**：若安裝的是僅供開發或測試使用的工具（如 `pytest`, `ruff`），必須加上開發群組標籤（使用 `uv add --dev <package>`）。

## 2. 配置存取架構 (Configuration Access)

- **禁止散落的 `os.getenv`**：嚴禁在任何業務邏輯、API 路由或資料處理模組中，直接引入 `os` 並呼叫 `getenv` 或 `environ`。
- **強型別單一入口**：所有環境變數與系統配置，必須集中於專屬的設定模組（例如透過 `pydantic-settings` 的 `BaseSettings` 或單一 `config.py` 宣告）。
- **依賴注入優先**：業務邏輯模組不得主動從全域載入配置實例。必須透過建構子注入（Constructor Injection）或函式參數將配置傳遞給需要的模組，確保模組具備 100% 的可測試性。
