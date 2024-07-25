參數 : offset=int ( byes or percentage )
說明 : 若是給百分比，offset 會根據硬碟單位 blocksize  ( 512B or 4K ) 對齊

範例 1 : offset=10%

```shell
$ fio --offset=10%
```

範例 2 : offset=1GB

```shell
$ fio --offset=1GB
```

---

參數 : offset_increment=int
說明 :

```shell
$ fio --
```