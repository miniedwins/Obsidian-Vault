下載 libnvme 原始碼

```
$ git clone https://github.com/linux-nvme/libnvme.git
```

安裝 libnvme 編譯所需套件

```
$ apt install libssl-dev libkeyutils-dev libdbus-dev python3-dev
```

編譯 libnvme 函式庫

```
$ cd nvme-cli
$ meson setup .build
$ meson compile -C .build
$ meson install -C .build
```

編譯加入其它功能參數

-Dlibdbus=enabled