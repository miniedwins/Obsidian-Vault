相關依賴套件如下 : 
* [libnvme](https://github.com/linux-nvme/libnvme)
* [json-c](https://github.com/json-c/json-c)
* pkg-config
* uuid-dev
* libssl-dev

首先可以透過 `APT` 安裝發行版本所提供的套件

```shell
$ apt install git pkg-config uuid-dev libhugetlbfs-dev libssl-dev libdus-dev
```

然後接下來另外兩個套件 `libnvme` 以及 `json-c` 需要透過原始碼方式安裝，安裝方法如下 : 

**libnvme** 

```shell
$ git clone https://github.com/linux-nvme/libnvme.git
$ cd nvme-cli
$ meson setup .build
$ meson compile -C .build
$ meson install -C .build
$ make
$ make install
``````

**json-c**

```shell
$ git clone https://github.com/json-c/json-c.git
$ mkdir json-c-build
$ cd json-c-build
$ cmake ../json-c
$ make
$ make test
$ make install
```
