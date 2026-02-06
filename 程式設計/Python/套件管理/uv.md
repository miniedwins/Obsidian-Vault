
## UV 管理套件安裝

### Windows

```shell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Linux

Use `curl` to download the script and execute it with `sh`:

```
$ curl -LsSf https://astral.sh/uv/install.sh | sh
```

If your system doesn't have `curl`, you can use `wget`:

```shell
wget -qO- https://astral.sh/uv/install.sh | sh
```

## 初始化專案

```shell
uv init uv-demo
uv init uv-demo --python 3.10 (指定安裝特定的版本)
```

## 安裝 Python 版本

```shell
$ uv python install
$ uv python install 3.10 (指定安裝特定的版本)
$ uv python install 3.10 3.11 (安裝多個版本)
```

## 移除 Python 版本

```shell
$ uv python uninstall (移除最新版)
$ uv python uninstall 3.10 (指定特定的版本移除)
```

## 顯示已安裝的 Python 版本

```shell
$ uv python list --only-installed
```

## 指定特定 Python 版本運行 

```shell
$ uv run .\show_version.py
$ uv run --python 3.10 .\show_version.py (指定特定的版本運行)
```

如果想要設定 uv 預設使用的 Python 版本，可以使用 `uv python pin`。

設定之後，如果再執行 Python 程式，就會改用剛剛指定的版本。

```shell
$ uv python pin 3.10
Updated `.python-version` from `3.14` -> `3.10`
```

## 安裝與移除依賴套件

```shell
$ uv add pandas (正式環境依賴)
$ uv add pytest --dev (開發環境依賴)

$ uv remove pandas
$ uv remove pytest --group dev (需要指定開發環境群組)
```

dependencies : 程式執行時必須具備的套件
dependency-groups : 開發者才需要的工具

```shell
[project]
name = "uv-lab"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.14"
dependencies = [
    "pandas~=2.3.3",
]

[dependency-groups]
dev = [
    "pytest>=9.0",
]
```

## 安裝指定套件版本

#### Compatible Release

```shell
$ uv add pandas~=2.3.3
```

這個符號的意思是：**「我要 2.3.3 以上的版本，但必須與 2.3.3 相容」**。

- **等義於：** `>= 2.3.3, == 2.3.*`    
- **允許範圍：** 會自動升級到 `2.3.4`, `2.3.5` 等（Patch 補丁更新），但**絕對不會**升級到 `2.4.0`。    
- **核心邏輯：** 鎖定「次要版本（Minor Version）」，只允許安裝修復 Bug 的小更新。這通常是最安全的做法，因為同一個次要版本內的 API 通常是穩定的。

**補充知識：`~=` 的小陷阱** 如果你寫 `~= 2.3`（只有兩位數），它的行為會變成 `>= 2.3, == 2.*`。也就是說，它會允許升級到 `2.4`、`2.5`，但不會升到 `3.0`。 **重點在於：它會鎖定你「沒寫出來」的那位數之前的數字。**

#### Minimum Version

```shell
$ uv add pandas>=2.3.3
```

這個符號的意思是：**「只要不低於 2.3.3，隨便你要裝哪個新版本都行」**。

- **等義於：** `>= 2.3.3`（沒有上限）    
- **允許範圍：** 會安裝目前最新的版本，可能是 `2.4.0`、`2.5.0`，甚至是未來的 `3.0.0`。    
- **核心邏輯：** 只設下限，不設上限。這在開發初期很方便，但風險較高，因為當 Pandas 發布 `3.0.0` 這種可能有「破壞性改動（Breaking Changes）」的大版本時，你的程式碼可能會噴錯。

## 更新套件操作

```shell
$ uv sync (照著 lock 檔做，不更新版本)
$ uv lock --upgrade (pyproject.toml 限制內全部升級到最高)
$ uv lock --upgrade-package <name> (只升級特定套件)
```

你想看看如果你現在執行更新，`uv` 預計會幫你把哪些套件升級到什麼版本嗎？你可以執行 `uv lock --upgrade --dry-run` 來預覽，它不會真的改動任何檔案。


## 手動修改 pyproject.toml 檔

如果把其中有 dependency-groups 表格中的 pytest 那一行刪除：

```shell
[project]
name = "uv-lab"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.10"
dependencies = []

[dependency-groups]
dev = [
    "pytest>=9.0.2",
]
```

這時候必須執行 `uv lock` 指令，讓 uv.lock 檔的內容與 pyproject.toml 檔一致：

```shell
PS C:\Users\edwin\Desktop\src\study\uv-lab> uv lock
Resolved 1 package in 12ms
Removed colorama v0.4.6
Removed exceptiongroup v1.3.1
Removed iniconfig v2.3.0
Removed packaging v26.0
Removed pluggy v1.6.0   
Removed pygments v2.19.2
Removed pytest v9.0.2   
Removed tomli v2.4.0    
Removed typing-extensions v4.15.0
```

要依照 uv.lock 內容增刪套件，就必須再執行 `uv sync` 讓實際的 Python 環境與 uv.lock 檔的內容一致：

```shell
PS C:\Users\edwin\Desktop\src\study\uv-lab> uv sync
Resolved 1 package in 3ms
Uninstalled 9 packages in 116ms
 - colorama==0.4.6
 - exceptiongroup==1.3.1
 - iniconfig==2.3.0
 - packaging==26.0
 - pluggy==1.6.0
 - pygments==2.19.2
 - pytest==9.0.2
 - tomli==2.4.0
 - typing-extensions==4.15.0
```