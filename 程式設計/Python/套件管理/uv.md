

Windows 安裝

```shell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

初始化專案
uv init uv-demo (不指定版本會使用最新版)
uv init uv-demo --python 3.10

安裝 Python 版本 
uv python install (不指定版本會安裝最新版)
uv python install 3.10 (指定安裝特定的版本)
uv python install 3.10 3.11 (安裝多個版本)

移除 Python 版本：
uv python uninstall (移除最新版)
uv python uninstall 3.10 (指定特定的版本移除)

顯示已安裝的 Python 版本
uv python list --only-installed

指定特定 Python 版本運行 
uv run .\show_version.py
uv run --python 3.10 .\show_version.py (指定特定的版本運行)