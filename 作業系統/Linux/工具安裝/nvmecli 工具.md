安裝 nvmecli 編譯所需套件

```shell
$ apt install pkg-config uuid-dev libhugetlbfs-dev libssl-dev libdus-dev
```

以下函式庫需要手動安裝 : 
* [libnvme](https://github.com/linux-nvme/libnvme)
* [json-c](https://github.com/json-c/json-c)

安裝 nvme-cli 工具

```
$ git clone https://github.com/linux-nvme/nvme-cli.git
$ cd nvme-cli
$ meson setup .build
$ meson compile -C .build
$ meson install -C .build
```