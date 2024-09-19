# Install Poetry
```shell
# Install Poetry Module
$ curl -sSL https://install.python-poetry.org | python3 -

# 設定 PATH 環境變數
$ export PATH=$PATH:$HOME/.local/bin

# 建立虛擬環境
$ poetry env use [version] 

# Example: python3.10
$ poetry env use python3.10

# 
```

# Poetry 常用指令清單

```shell
# 初始化，建立 pyproject.toml
$ poerty init

# 新增套件
$ poetry add [module]

# 新增套件 dev-dependencies
$ poetry add [module] --group dev

# 移除套件
$ poetry remove [module]

# 移除套件 dev-dependencies
$ poetry remove [module] --group dev

# 更新套件
$ poetry update

# 指定特定套件更新
$ poetry update flask

# 列出全部套件清單 (顯示套件依賴層級)
$ poetry show --tree 

# Change to env
$ poetry env use [version] # example: python3.10

# 啟動虛擬環境
# 如果虛擬環境尚未建立，則會直接自動幫你建立虛擬環境並使用
$ poetry shell

# 退出虛擬環境
$ exit

# 輸出 requirements.txt
# For tool.poetry.dependencies
$ poetry export -f requirements.txt -o requirements.txt --without-hashes

# For tool.poetry.group.dev.dependencies
$ poetry export -f requirements.txt -o requirements.txt --without-hashes --dev
```

# Poetry PATH 

```shell
 ~/Desktop/workspace/study/py/poetry-demo  ls -l ~/.cache/pypoetry/virtualenvs                                                           ok  poetry-demo-jNWKs6r--py3.10 py  16:22:38 
total 16
-rw-rw-r-- 1 edwin edwin  114  九  16 17:24 envs.toml
drwxrwxr-x 4 edwin edwin 4096  九  18 16:21 poetry-demo-jNWKs6r--py3.10
drwxrwxr-x 4 edwin edwin 4096  九  16 17:24 poetry-export-Q8rhi4Ih-py3.10
drwxrwxr-x 4 edwin edwin 4096  九  16 17:24 poetry-export-Q8rhi4Ih-py3.12
```

# Use different python version

The command can be used to switch between different Python versions.

```shell
$ poetry env use python3.10
Using virtualenv: /home/edwin/.cache/pypoetry/virtualenvs/poetry-demo-jNWKs6r--py3.10

$ poetry shell
Spawning shell within /home/edwin/.cache/pypoetry/virtualenvs/poetry-demo-jNWKs6r--py3.10
 ~/Desktop/workspace/study/py/poetry-demo  emulate bash -c '. /home/edwin/.cache/pypoetry/virtualenvs/poetry-demo-jNWKs6r--py3.10/bin/activate' 
```

# 別台主機上重現專案的 Poetry 虛擬環境

You have both `poetry.lock` and `pyproject.toml` files in your project

You can specify a specific Python version.

```shell
$ poetry env use python3.12
Creating virtualenv poetry-demo-jNWKs6r--py3.12 in /home/edwin/.cache/pypoetry/virtualenvs
Using virtualenv: /home/edwin/.cache/pypoetry/virtualenvs/poetry-demo-jNWKs6r--py3.12
```

因為是舊專案，不需要init, poetry.lock 記載的套件版本安裝到虛擬環境中

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

# 移除並虛擬環境

## (1) 移除1

```shell
 ~/Desktop/workspace/study/py/poetry-demo  ls -l ~/.cache/pypoetry/virtualenvs                                                                                           ok  15:39:54 
total 20
-rw-rw-r-- 1 edwin edwin  113  九  19 14:03 envs.toml
drwxrwxr-x 4 edwin edwin 4096  九  18 16:21 poetry-demo-jNWKs6r--py3.10
drwxrwxr-x 4 edwin edwin 4096  九  19 14:03 poetry-demo-jNWKs6r--py3.12
drwxrwxr-x 4 edwin edwin 4096  九  16 17:24 poetry-export-Q8rhi4Ih-py3.10
drwxrwxr-x 4 edwin edwin 4096  九  16 17:24 poetry-export-Q8rhi4Ih-py3.12

 ~/Desktop/workspace/study/py/poetry-demo  poetry env remove 3.12                                                                                                        ok  15:40:05 
Deleted virtualenv: /home/edwin/.cache/pypoetry/virtualenvs/poetry-demo-jNWKs6r--py3.12

 ~/Desktop/workspace/study/py/poetry-demo  ls -l ~/.cache/pypoetry/virtualenvs                                                                                           ok  15:40:16 
total 16
-rw-rw-r-- 1 edwin edwin   57  九  19 15:40 envs.toml
drwxrwxr-x 4 edwin edwin 4096  九  18 16:21 poetry-demo-jNWKs6r--py3.10
drwxrwxr-x 4 edwin edwin 4096  九  16 17:24 poetry-export-Q8rhi4Ih-py3.10
drwxrwxr-x 4 edwin edwin 4096  九  16 17:24 poetry-export-Q8rhi4Ih-py3.12

 ~/Desktop/workspace/study/py/poetry-demo  poetry env remove 3.10                                                                                                        ok  15:40:27 
Deleted virtualenv: /home/edwin/.cache/pypoetry/virtualenvs/poetry-demo-jNWKs6r--py3.10

 ~/Desktop/workspace/study/py/poetry-demo  ls -l ~/.cache/pypoetry/virtualenvs                                                                                           ok  15:40:38 
total 12
-rw-rw-r-- 1 edwin edwin   57  九  19 15:40 envs.toml
drwxrwxr-x 4 edwin edwin 4096  九  16 17:24 poetry-export-Q8rhi4Ih-py3.10
drwxrwxr-x 4 edwin edwin 4096  九  16 17:24 poetry-export-Q8rhi4Ih-py3.12
```


## (2) 移除2
Go to the virtual environment folder and remove it directly.

```shell
ls -l ~/.cache/pypoetry/virtualenvs/
total 20
-rw-rw-r-- 1 edwin edwin  113  九  19 14:03 envs.toml
drwxrwxr-x 4 edwin edwin 4096  九  18 16:21 poetry-demo-jNWKs6r--py3.10
drwxrwxr-x 4 edwin edwin 4096  九  19 14:03 poetry-demo-jNWKs6r--py3.12
drwxrwxr-x 4 edwin edwin 4096  九  16 17:24 poetry-export-Q8rhi4Ih-py3.10
drwxrwxr-x 4 edwin edwin 4096  九  16 17:24 poetry-export-Q8rhi4Ih-py3.12
```

Remove the environment folder.

```shell
rm -rf ~/.cache/pypoetry/virtualenvs/poetry-export-Q8rhi4Ih-py3.12/
```

# Poetry 的版本管理能力

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
