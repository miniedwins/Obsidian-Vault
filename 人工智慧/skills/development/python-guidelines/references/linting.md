# Python 靜態分析與風格規範 (Linting & Static Analysis)

本規範定義專案的靜態檢驗門檻，確保程式碼具備高度的型別安全性與風格一致性。

## 1. 靜態型別安全防線 (Static Type Gateway)

- **零妥協政策**：所有交付的模組必須無條件通過 `mypy --strict` 靜態掃描。
- **限制繞過機制**：不接受以 `Any` 為藉口的隨意繞過。若因特殊技術原因需局部繞過，必須在 PR / MR 中提出明確解釋。
- **第三方庫型別**：若使用的第三方庫缺乏型別宣告，應安裝對應的 `types-` 套件或在 `pyproject.toml` 中配置排除。

## 2. 自動化風格審查 (Style Rules Gateway)

- **交付檢驗約束**：所有交付的程式碼必須無條件通過 `ruff check` 與 `ruff format --check`。
- **整潔原則**：不接受有未使用的 Import 或未清除的印出語句 (`print`)，此類問題應由 ruff 自動攔截並在本地開發階段修正。
- **Docstring 規範**：建議重要模組與函式應包含符合 PEP 257 標準的 Docstrings。

## 3. 執行工具鏈 (Toolchain)

- **一鍵檢查**：建議配置 `pre-commit` 鉤子，在 git commit 前自動執行上述檢查。
- **IDE 整合**：開發者應在編輯器（如 VS Code 或 PyCharm）中啟用 mypy 與 ruff 的即時回饋功能。
