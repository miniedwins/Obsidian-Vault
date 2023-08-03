主要目的是為了取得輸入的傳遞參數，藉由判斷來設定參數。

**$#** 代表有多少個參數傳遞

測試參數長度是否大於1，然後 **shift** 由右往左移動參數，每移位長度就減一，直到 0 為止跳出迴圈。

```shell
while [ "$#" -ge "1" ]; do
	echo "current parameter: $1" 
	shift 
done
```

執行結果如下

```shell
$ shift.sh 1 2 3
current parameter: 1
current parameter: 2
current parameter: 3
```

若是想要取得參數後面的有接設定值，則是需要移位兩次

如下範例所示 : 

```shell
sections=()

while (($#)); do
        case "$1" in
                -s) echo "s=$1"; sections+=("$2"); shift; shift;;
                -v) echo "v=$1"; sections+=("$2"); shift; shift;;
                -q) quit=1; shift;;
                -h) usage; break;;
                *)usage; exit 1;;
        esac
done
```

執行結果如下 :

```shell
$ ./shift.sh -s 1 -v 2
s=-s
v=-v
1 2
```