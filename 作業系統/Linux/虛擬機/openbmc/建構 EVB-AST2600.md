安裝編譯所需要的套件。

``` shell
sudo apt install git python3-distutils gcc g++ make file wget gawk diffstat bzip2 cpio chrpath zstd lz4 bzip2
```

下載原始碼，並且切換到當前最新版本 ( 當前版本 : v2.14.0 )。

```
$ git clone https://github.com/openbmc/openbmc.git
$ cd openbmc
$ git checkout -b v2.14.0 2.14.0
```

設定建構環境 `evb-ast2600`

```
$ source setup evb-ast2600
```

開始進行下載套件以及編譯

```
$ bitbake obmc-phosphor-image
```
