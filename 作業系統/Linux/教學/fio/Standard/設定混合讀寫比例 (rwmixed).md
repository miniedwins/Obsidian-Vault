參數 : rwmixwrite=int
說明 : 混合寫的比例為多少, default=50% (50% write + 50% read)
範例 : Write=30%，Read=70%

```shell
$ fio --filename=/dev/sdx --name=test --ioengine=libaio --iodepth=1 --bs=128k --size=1Gb --rwmixwrite=30
```

參數 : rwmixread=int
說明 : 混合讀的比例為多少, default=50% (read=50% write=50%)
範例 : Read=30%，Write=70%

```shell
$ fio --filename=/dev/sdx --name=test --ioengine=libaio --iodepth=1 --bs=128k --size=1Gb --rwmixread=30
```
