
下載原始碼

```
$ git clone https://github.com/linux-nvme/libnvme.git
```

安裝 libnvme 所需要的依賴套件

```

```

編譯 libnvme 函式庫

```shell
$ cd nvme-cli
$ meson setup .build
$ meson compile -C .build
$ meson install -C .build
```

編譯加入其它功能參數

-Dlibdbus=enabled