安裝編譯核心所需要的套件

```
sudo apt install build-essential libncurses-dev libssl-dev libelf-dev bison flex -y
```

複製當前使用的 Linux 發行版本 (Ubuntu) 設定檔案

```
cp /boot/config-6.5.0-15-generic /home/user_name/kernel/.config
```

然後執行讀取舊有的設定檔案

```
$ make oldconfig
$ make menucofnig
```


