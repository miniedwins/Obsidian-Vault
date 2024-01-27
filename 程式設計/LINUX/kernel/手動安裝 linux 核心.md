安裝編譯核心所需要的套件

```
sudo apt install build-essential libncurses-dev libssl-dev libelf-dev bison flex -y
```

複製當前使用的 Linux 發行版本 (Ubuntu) 設定檔案

```
cp -v /boot/config-$(uname -r) /home/user_name/kernel/.config
```

開始編譯前檔案需要設定 `.config`，這邊我們使用 `make oldconfig` 

- 核心組態設定檔案 (.config) : 
	- 如果 `.config` 存在，運行 `make config/menuconfig` 的預設設定是當前 `.config` 設定。
	- 若對設定進行了修改 `.config` 將被更新。

- oldconfig : 
	- 備份當前 `.config` 檔案為 `.config.old`。
	- 編譯新的核心時候，會套用當前這份設定檔案，也可以再使用 `make menucofnig` 更新設定。
	- 若是執行 `make config or menuconfig`，若是設定不正常可用於恢復先前的 `.config`。

- localmodconfig :  
	- 執行 `lsmod` 查看當前系統中載入了哪些模組 (Modules)，最後將原來的 `.config`  中不需要的模組去掉，僅保留前面 `lsmod` 出來的這些模組，從而簡化了核心的組態過程

```
$ make oldconfig
```

執行下列設定，否則編譯核心會失敗

```
$ scripts/config --disable SYSTEM_TRUSTED_KEYS
$ scripts/config --disable SYSTEM_REVOCATION_KEYS
$ scripts/config --set-str CONFIG_SYSTEM_TRUSTED_KEYS ""
$ scripts/config --set-str CONFIG_SYSTEM_REVOCATION_KEYS ""
```

編譯核心以及模組 (Modules)

```
#　使用
$ make -j4 

$ make modules_install
$ make install
```

