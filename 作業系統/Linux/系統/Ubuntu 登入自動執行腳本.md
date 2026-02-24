
### 1. 啟動應用程式 (Startup Applications)

在 **指令 (Command)** 欄位填入：

```shell
gnome-terminal --maximize -- bash -c "sudo /home/user/test.sh; exec bash"
```

- `--maximize`: 視窗最大化。    

- `exec bash`: 腳本執行完後保持視窗開啟，不自動關閉。




### 2. 免密碼權限設定

若要讓腳本自動執行而不彈出密碼要求，請執行：

```shell
sudo visudo
```

在檔案末尾新增以下內容（請將 `username` 替換為實際使用者名稱）：

**方案 A：僅針對該腳本免密碼（推薦，較安全）**

```shell
username ALL=(ALL) NOPASSWD: /home/user/test.sh
```

**方案 B：該使用者所有指令均免密碼（最簡便，風險高）**

```shell
username ALL=(ALL:ALL) NOPASSWD:ALL
```

或是直接適用所有使用者

```shell
%sudo ALL=(ALL:ALL) NOPASSWD:ALL
```

> 💡 小提醒
> - 請確保腳本具有執行權限：`chmod +x /home/user/test.sh`    
> - 路徑 `/home/user/test.sh` 必須使用**絕對路徑**。