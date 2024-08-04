參數 : offset=int ( byes or percentage )
說明 : 若是給百分比，offset 會根據硬碟單位 blocksize  ( 512B or 4K ) 對齊

範例 1 : offset=1%

```shell
$ fio fio --filename=/dev/sdx --name=test --direct=1 --ioengine=libaio --iodepth=32 --bs=4k --offset=1% --rw=write --size=100%
```

範例 2 : offset=1MB

```shell
$ fio --filename=/dev/sdx --name=test --direct=1 --ioengine=libaio --iodepth=32 --bs=4k --offset=1MB --rw=write --size=100%
```

寫入的資料是從偏移量 offset=1MBytes 開始，因此可以看到 offset=00100000 前面的資料都是為零。

```shell
$ hexdump -C -n 1049088 /dev/sdb
00000000  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
00100000  c6 fd a8 a8 90 71 19 02  b8 1f 32 96 dd d9 64 1e  |.....q....2...d.|
00100010  f7 43 ea a2 22 d0 e5 06  7e c8 61 32 8f 68 cc 02  |.C.."...~.a2.h..|
...
001001d0  dd cf cb 84 59 1e 8e 05  fb f9 aa 48 65 01 50 0d  |....Y......He.P.|
001001e0  3f df 17 2c d7 5b 14 14  e7 7b e3 f5 6e f5 8f 0b  |?..,.[...{..n...|
001001f0  7c ef c8 20 bc 83 4b 1c  ef 1d 5b 0c 13 60 0f 1f  ||.. ..K...[..`..|
```

---

參數 : offset_increment=int ( byes or percentage )
說明 : 通常搭配 threads or numjobs 使用

```shell
$ 
```