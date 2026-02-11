
## Linter
```shell
# --- Ruff 設定 (包含 PEP8, 排序, 格式化) ---
[tool.ruff]
# 每行最大長度 (PEP8 建議為 79-88)
line-length = 88

# 目標 Python 版本
target-version = "py310"

# 要檢查的資料夾
src = ["src"]

[tool.ruff.lint]
# 啟動的檢查規則：
# E/W: PEP8 錯誤與警告
# F: Pyflakes 邏輯檢查
# I: isort 自動排序
# N: pep8-naming 命名規範 (例如類別要大寫開頭)
# UP: pyupgrade 升級到新版語法

select = ["E", "W", "F", "I", "N", "UP"]

# 不想檢查的規則（可選）
ignore = []

[tool.ruff.lint.isort]
# 讓排序後的 Import 看起來更整齊
combine-as-imports = true
lines-after-imports = 2

# --- Pyright 設定 (靜態型別檢查) ---
[tool.pyright]
include = ["src"]
exclude = ["**/node_modules", "**/__pycache__", ".venv"]

# 檢查強度：'basic' 或 'strict' (嚴格)
typeCheckingMode = "basic"

# 確保分析時使用你的虛擬環境
venvPath = "."
venv = ".venv"

# --- UV 設定 (可選) ---
[tool.uv]
# 強制開發時一定要同步 .python-version 檔案
package = true
```

## pyright
