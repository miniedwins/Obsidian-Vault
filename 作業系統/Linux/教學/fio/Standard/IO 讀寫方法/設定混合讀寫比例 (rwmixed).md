**參數** : `rwmixwrite=int`
**說明** : 
- 設定混合寫操作的比例，剩餘比例自動分配給讀操作。
- 預設值為 `50`，即 50% 寫入 + 50% 讀取。
**範例** :
- 若將寫入比例設為 `30%`（讀取比例自動為 `70%`）
```shell
$ fio --filename=/dev/sdx --name=test --direct=1 --ioengine=libaio --iodepth=32 --bs=128k --rwmixwrite=30 --size=100%
```

---

**參數** : `rwmixread=int`
**說明** : 
- 設定混合寫操作的比例，剩餘比例自動分配給讀操作。
- 預設值為 `50`，即 50% 讀取 + 50% 寫入。
**範例** : 
- 若將讀取比例設為 `30%`（寫入比例自動為 `70%`）
```shell
$ fio --filename=/dev/sdx --name=test --direct=1 --ioengine=libaio --iodepth=32 --bs=128k --rwmixread=30 --size=100% 
```
