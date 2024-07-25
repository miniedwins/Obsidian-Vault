參數 : bssplit=blocksize/percentage:blocksize/percentage
說明 : 對每一個 IO大小設定不同比例，最終所有的比例相加要等於 100%

```shell
$ fio --filename=/dev/sdx --name=test --ioengine=libaio --iodepth=32 --size=100% -- bssplit=4k/80:128k/10:1024k/10 --rw=randwrite
```