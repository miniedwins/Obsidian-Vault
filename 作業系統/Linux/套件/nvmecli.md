- 安裝前需要手動安裝相依套件 : 
	- **[[json-c]]**
	- **[[libnvme]]**

- 安裝 nvmecli 編譯所需相依套件

```shell
$ apt install pkg-config uuid-dev libhugetlbfs-dev libssl-dev libdus-dev
```

- 安裝 nvme-cli 工具

```
$ git clone https://github.com/linux-nvme/nvme-cli.git
$ cd nvme-cli
$ meson setup .build
$ meson compile -C .build
$ meson install -C .build
```