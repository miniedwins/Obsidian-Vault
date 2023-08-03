Bash 利用 `$1...$9` 變數來代表參數的順序，也就是位置

`$#` 代表有多少個參數傳遞

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