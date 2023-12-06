## 語法

```
target: 目標檔1 目標檔2 
<tab>gcc -o 欲建立的執行檔 目標檔1 目標檔2
```

- makefile 語法中之 `<tab>` 與空白：
    - 所有的法則必須在同一行，而且行首必須為 `<tab>`；不能為空白。
    - 行尾如果有一個空白，會造成 make 命令執行錯誤。

## 特別字元

```
.PHONY: hello
hello:
	@echo "Hello World"

.PHONY: clean
	-rm *.o
```

- `@` 不要顯示執行的命令
	- 因執行 make 命令後會在終端機印出正在執行的命令。

- `-` 表示即使該行命令出錯，也不會中斷後續的執行動作
	-  make 只要遇到任何錯誤就會中斷執行。
	- 但像是在進行 clean 時，也許根本沒有任何檔案可以 clean，導致 make 中斷執行。

## 註解

```
target: object
# 我是 Makefile 註解
```

`Makefile` 的註解（comment）：
    - `#` 只有行首的文字都是註解。