# 安裝 Poetry 套件

下載 Poetry 套件並安裝

```shell
$ curl -sSL https://install.python-poetry.org | python3 -
```

Poetry 實際安裝路徑如下：

- `$HOME/.local/bin` for Unix or Linux
- `%APPDATA%\Python\Scripts` on Windows

設定 `Poetry PATH` 環境變數

```shell
$ export PATH=$PATH:$HOME/.local/bin
$ source ~/.bashrc
```

或是透過軟連結將執行檔案連結到 `/usr/bin` or `/usr/local/bin`

```shell
$ ln -s $PATH:$HOME/.local/bin /usr/bin
$ ln -s $PATH:$HOME/.local/bin /usr/local/bin
```

# 建立 Poetry 專案

## 初始化 Poetry

首先建立專案資料夾，然後進入專案目錄中。

```shell
$ mkdir poerty-demo
$ cd poerty-demo
```

初始化 Poetry，使用 `poerty init` 命令，這會產生下列兩個檔案 : 

- `poetry.lock` : 
- `pyproject.toml` : 

```shell
$ poerty init
```

初始化所使用的 Python 版本，會根據系統所安裝的版本作為開發環境所使用。

另外，也可以指定 Python 特定的版本，如下設定 : 

```shell
$ poerty init python3.12
```

## 進入開發環境

初始化完成後，啟動虛擬環境

```shell
poetry shell
```

剛建立完的新專案並未安裝任何套件，因此可以用命令 `poetry add` 新增套件。

下列範例為安裝 Pytest 套件，如下 : 

```shell
$ poetry add pytest
```

安裝完成後，安裝完成的套件會記錄在 `pyproject.toml` 檔案中，套件安裝區分為開發以及佈署

- `tool.poetry.dependencies`: 佈署
- `tool.poetry.group.dev.dependencies`: 開發

```shell
[tool.poetry.dependencies]
python = "^3.10"
pytest = "^8.3.3"

[tool.poetry.group.dev.dependencies]
black = "^24.8.0"
```

# 管理虛擬環境

## Displaying the environment information

```shell
$ poetry env info
Virtualenv
Python:         3.12.6
Implementation: CPython
Path:           /home/edwin/.cache/pypoetry/virtualenvs/poetry-demo-jNWKs6r--py3.12
Executable:     /home/edwin/.cache/pypoetry/virtualenvs/poetry-demo-jNWKs6r--py3.12/bin/python
Valid:          True

Base
Platform:   linux
OS:         posix
Python:     3.12.6
Path:       /usr
Executable: /usr/bin/python3.12
```

## 使用不同的虛擬環境開發

開發中可能會需要建立不同的虛擬環境，`poetry env use` 能讓使用者指定不同的 Python 版本。

```shell
$ poetry env use python3.10
Using virtualenv: /home/edwin/.cache/pypoetry/virtualenvs/poetry-demo-jNWKs6r--py3.10
```

設定完成後，進入虛擬環境就可以看到現在使用的是 `Python 3.10`

```shell
$ poetry shell
Spawning shell within /home/edwin/.cache/pypoetry/virtualenvs/poetry-demo-jNWKs6r--py3.10
 ~/Desktop/workspace/study/py/poetry-demo  emulate bash -c '. /home/edwin/.cache/pypoetry/virtualenvs/poetry-demo-jNWKs6r--py3.10/bin/activate' 
```

虛擬環境所產生的位置是在，本地路徑 `~/.cache/pypoetry/virtualenvs` 資料夾中

- poetry-demo : 
	- py3.10
- poetry-export : 
	- py3.10
	- py3.12

```shell
$ ls -l ~/.cache/pypoetry/virtualenvs
-rw-rw-r-- 1 edwin edwin  114  九  16 17:24 envs.toml
drwxrwxr-x 4 edwin edwin 4096  九  18 16:21 poetry-demo-jNWKs6r--py3.10
drwxrwxr-x 4 edwin edwin 4096  九  16 17:24 poetry-export-Q8rhi4Ih-py3.10
drwxrwxr-x 4 edwin edwin 4096  九  16 17:24 poetry-export-Q8rhi4Ih-py3.12
```

上面說明 `poetry-demo` 目前只有建立 `py3.10`，若是要使用 `py3.12`，需要進入到 `poetry-demo` 資料夾中，使用 `poetry env use` 指定虛擬環境版本，例如下列範例 : 

```shell
$ cd poetry-demo
$ poetry env use python3.12
```

最後再啟動虛擬環境

```shell
$ poetry shell
```
## 重新建立相同的專案

主要目的是為了將開發所使用的套件或是設定，重新建立到不同的平台上

將下列檔案複製到新的專案資料夾中
- poetry.lock
- pyproject.toml

```shell
$ mkdir poetry-new
$ cd poetry-new
$ cp ../poerty-old/poetry.lock .
$ cp ../poerty-old/pyproject.toml .
```

然後使用 `poetry env use` 指定要執行的虛擬環境版本

```shell
$ poetry env use python3.12
Creating virtualenv poetry-demo-jNWKs6r--py3.12 in /home/edwin/.cache/pypoetry/virtualenvs
Using virtualenv: /home/edwin/.cache/pypoetry/virtualenvs/poetry-demo-jNWKs6r--py3.12
```

因為是舊專案，不需要 `init`，直接進入新專案虛擬環境

```shell
$ poetry shell
```

使用 `poetry install` 會依據 `poetry.lock` 記載的套件版本安裝到虛擬環境中

```shell
$ poetry install
Installing dependencies from lock file
Package operations: 15 installs, 0 updates, 0 removals
  - Installing markupsafe (2.1.5)
  - Installing blinker (1.8.2)
  - Installing click (8.1.7)
  - Installing iniconfig (2.0.0)
  - Installing itsdangerous (2.2.0)
  - Installing jinja2 (3.1.4)
  - Installing mypy-extensions (1.0.0)
  - Installing packaging (24.1)
  - Installing pathspec (0.12.1)
  - Installing platformdirs (4.3.3)
  - Installing pluggy (1.5.0)
  - Installing werkzeug (3.0.4)
  - Installing black (24.8.0)
  - Installing flask (3.0.3)
  - Installing pytest (8.3.3)
```

# 移除虛擬環境

## (1) 使用 env remove

每個專案所使用的虛擬環境不一樣，移除哪一個專案的虛擬環境需要進入該專案目錄中

```shell
$ ls -l ~/.cache/pypoetry/virtualenvs
-rw-rw-r-- 1 edwin edwin  113  九  19 14:03 envs.toml
drwxrwxr-x 4 edwin edwin 4096  九  18 16:21 poetry-demo-jNWKs6r--py3.10
drwxrwxr-x 4 edwin edwin 4096  九  19 14:03 poetry-demo-jNWKs6r--py3.12
drwxrwxr-x 4 edwin edwin 4096  九  16 17:24 poetry-export-Q8rhi4Ih-py3.10
drwxrwxr-x 4 edwin edwin 4096  九  16 17:24 poetry-export-Q8rhi4Ih-py3.12
```

執行指定的 Python 版本移除，這裡我們指定移除 `3.12`

```shell
$ ~/home/edwin/poetry-demo/poetry env remove 3.12
Deleted virtualenv: /home/edwin/.cache/pypoetry/virtualenvs/poetry-demo-jNWKs6r--py3.12
```

可以看到 `poetry-demo-jNWKs6r--py3.12` 檔案會被移除 

```shell
$ ls -l ~/.cache/pypoetry/virtualenvs
-rw-rw-r-- 1 edwin edwin   57  九  19 15:40 envs.toml
drwxrwxr-x 4 edwin edwin 4096  九  18 16:21 poetry-demo-jNWKs6r--py3.10
drwxrwxr-x 4 edwin edwin 4096  九  16 17:24 poetry-export-Q8rhi4Ih-py3.10
drwxrwxr-x 4 edwin edwin 4096  九  16 17:24 poetry-export-Q8rhi4Ih-py3.12
```

## (2) 直接移除檔案

進入到虛擬環境檔案路徑，找到要移除專案使用的虛擬環境資料夾

```shell
ls -l ~/.cache/pypoetry/virtualenvs/
-rw-rw-r-- 1 edwin edwin  113  九  19 14:03 envs.toml
drwxrwxr-x 4 edwin edwin 4096  九  18 16:21 poetry-demo-jNWKs6r--py3.10
drwxrwxr-x 4 edwin edwin 4096  九  19 14:03 poetry-demo-jNWKs6r--py3.12
drwxrwxr-x 4 edwin edwin 4096  九  16 17:24 poetry-export-Q8rhi4Ih-py3.10
drwxrwxr-x 4 edwin edwin 4096  九  16 17:24 poetry-export-Q8rhi4Ih-py3.12
```

然後透過 `rm -rf` 命令直接移除檔案，這裡我們移除 `poetry-export` 所使用的 `py3.12` 虛擬環境

```shell
$ rm -rf ~/.cache/pypoetry/virtualenvs/poetry-export-Q8rhi4Ih-py3.12/
```

# 版本管理能力

## (1) 使用^符號（文件）

指定 Django 版本為 >=4.2.9 且 <5.0.0（允許 4.2.9 及以上版本，但不包括 5.0.0，即最大版號不能變更）:

```shell
poetry add django@^4.2.9
```
這意味著它會接受所有 4.x.x 的更新，只要版本號小於 5.0.0。這是一個常見的做法，因為它允許套件自動更新到任何非重大變更的新版本。

## (2) 使用~符號（文件）

指定 Django 版本為 >=4.2.9 且 <4.3.0（允許 4.2.9 及以上版本，但不包括 4.3.0，即只能升級最小版號）:

```shell
poetry add django@~4.2.9
```
這個選項更加保守，只會接受 4.2.x 系列的更新。這適合想要進一步限制更新的範圍，但又保留一些更新的彈性——僅包括 bug 修正和小幅度的改進。

## (3) 使用>=符號

指定 Django 版本為 >=4.2.9（沒有上限）:

```shell
# 注意，這裡需要使用「字串」表示
$ poetry add "django>=4.2.9"
```
主版號（即上面的 4.x.x 中的 4）升級時，通常有更大機率引入 API 變更、棄用舊有的 API 等，也就是所謂的 breaking change。
這樣的更新可能會導致你的專案無法正常運作，需要一併修改程式碼。所以一般不建議使用這種方式。

# 常用指令清單

```shell
# 初始化 Poetry
$ poerty init

# 新增套件
$ poetry add <module>

# 新增開發套件 dev-dependencies
$ poetry add <module> --group dev

# 移除套件
$ poetry remove <module>

# 移除開發套件 dev-dependencies
$ poetry remove <module> --group dev

# 更新 poetry 版本
$ poetry self update

# 更新套件
$ poetry update

# 指定特定套件更新
$ poetry update flask

# 列出全部套件清單 (顯示套件依賴層級)
$ poetry show --tree 

# 設定虛擬環境版本 
# Example: python3.10
$ poetry env use <version> 

# 啟動虛擬環境
$ poetry shell

# 退出虛擬環境
$ exit

# 輸出 requirements.txt 檔案
# tool.poetry.dependencies (不包含開發套件)
$ poetry export -f requirements.txt -o requirements.txt --without-hashes

# For tool.poetry.group.dev.dependencies (包含開發套件)
$ poetry export -f requirements.txt -o requirements.txt --without-hashes --dev
```
