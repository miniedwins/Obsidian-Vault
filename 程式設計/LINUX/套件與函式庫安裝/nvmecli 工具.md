

```shell
$ apt install meson pkg-config uuid-dev libhugetlbfs-dev libssl-dev libdus-dev
```

需要預先安裝依賴套件 : 

* [libnvme](https://github.com/linux-nvme/libnvme)
* [json-c](https://github.com/json-c/json-c)

```
$ git clone https://github.com/linux-nvme/nvme-cli.git
$ cd nvme-cli
$ meson setup .build
$ meson compile -C .build
$ meson install -C .build
```