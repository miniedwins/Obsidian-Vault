參數 : offset=int ( byes or percentage )
說明 : 若是給百分比，offset 會根據硬碟單位 blocksize  ( 512B or 4K ) 對齊

範例 1 : offset=1%

```shell
$ fio fio --filename=/dev/sdx --name=test --ioengine=libaio --iodepth=32 --bs=4k --size=100% --offset=1% --rw=write
```

範例 2 : offset=1MB

```shell
$ fio fio --filename=/dev/sdx --name=test --ioengine=libaio --iodepth=32 --bs=4k --size=100% --offset=1MB --rw=write
```

---

參數 : offset_increment=int ( byes or percentage )
說明 1 : 設定跟 offset 大致相同
說明 2 : 若是有給設定值，最終的偏移量會是 offset + offset_increment

```shell
$ fio --
```