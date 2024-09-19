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
# 新增套件
$ poetry add [module]

# 新增套件 dev-dependencies
$ poetry add [module] --group dev

# 移除套件
$ poetry remove [module]

# 更新套件
$ poetry update

# 指定特定套件更新
$ poetry update flask

# 套件
$ poetry show --tree 

# Change to env
$ poetry env use [version] # example: python3.10

# 啟動虛擬環境
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

