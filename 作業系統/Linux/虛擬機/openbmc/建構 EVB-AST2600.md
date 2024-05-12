安裝編譯所需要的套件

``` shell
sudo apt install git python3-distutils gcc g++ make file wget gawk diffstat bzip2 cpio chrpath zstd lz4 bzip2
```

下載原始碼，並且切換到當前最新版本 ( 當前版本 : v2.14.0 )

```
$ git clone https://github.com/openbmc/openbmc.git
$ cd openbmc
$ git checkout -b v2.14.0 2.14.0
```

編譯針對 `evb-ast2600` 系統鏡像

```
$ source setup evb-ast2600
```

開始進行下載套件以及編譯

備註 : 若遇到錯誤訊息，可以重新再執行一次，或許就不會發生錯誤。

```
$ bitbake obmc-phosphor-image
```

等待一段時間，可以得到編譯好的 64MB 的系統鏡像

```shell
ls -l tmp/deploy/images/evb-ast2600/obmc-phosphor-image-evb-ast2600.static.mtd
```

 qemu 啟動虛擬機器

```
$ qemu-system-arm -m 512 -M ast2600-evb -nographic -drive file=./obmc-phosphor-image-evb-ast2600.static.mtd,format=raw,if=mtd -net nic
```