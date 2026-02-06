

Windows 安裝

```shell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

安裝最新版本 (不指定版本會安裝最新版)
uv python install

指定安裝特定的版本：
uv python install 3.10

移除指定安裝版本：
uv python uninstall 3.10

安裝多個版本
uv python install 3.10 3.11

