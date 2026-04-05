# Python 測試驅動規範 (Testing)

本規範旨在約束測試代碼的「結構性」與「隔離性」，避免測試代碼成為難以維護的技術債。

## 1. 測試結構與組織 (Test Architecture)

- **行為驅動命名**：測試函式必須精確描述情境與預期。強制格式：`test_<受測對象>_<情境描述>_<預期結果>`（例如 `test_login_with_expired_token_should_raise_error`）。
- **情境類別化 (Test Classes)**：當針對同一模組有 3 個以上的關聯測試時，**禁止使用扁平函式**。必須將其封裝至 `class Test<Module>:` 中，以便共享 Setup/Teardown 邏輯。
- **AAA 區塊強制**：每個測試函式內部必須顯式使用註解標出 `# Arrange`, `# Act`, `# Assert`，嚴禁將準備資料與斷言邏輯混雜。

## 2. 狀態隔離與複用 (Isolation & Reuse)

- **禁止測試內迴圈**：針對多組測試數據，嚴禁在測試函式內使用 `for` 迴圈驗證，必須無條件使用 `@pytest.mark.parametrize`。
- **Fixture 生命週期完整性**：所有涉及 IO、檔案、資料庫或全域狀態修改的 `pytest.fixture`，**禁止單向初始化**。必須使用 `yield` 取代 `return`，並在 yield 後確保資源徹底還原/清理 (Teardown)。
- **邊界防禦**：除快樂路徑 (Happy Path) 外，必須主動加入 `None`、空結構 (`[]`, `{}`) 與極端數值的參數化測試。
