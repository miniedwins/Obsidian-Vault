
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
