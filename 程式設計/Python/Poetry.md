
# Command Line

```shell
# Install Poetry Module
$ curl -sSL https://install.python-poetry.org | python3 -

# Install Package
$ poetry add [module]

# Remove Package
$ poetry remove [module]

# Show package
$ poetry show --tree 

# Change to env
$ poetry env use [version] # example: python3.10

# Export requirements.txt
$ poetry export -f requirements.txt -o requirements.txt --without-hashes
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
