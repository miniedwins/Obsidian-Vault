## 語法

```
target: 目標檔1 目標檔2 
<tab>gcc -o 欲建立的執行檔 目標檔1 目標檔2
```

- makefile 語法中之 `<tab>` 與空白：
    - 所有的法則必須在同一行，而且行首必須為 `<tab>`；不能為空白。
    - 行尾如果有一個空白，會造成 make 命令執行錯誤。

## 註解

```
target: object
# 我是 Makefile 註解
```

`Makefile` 的註解（comment）：
    - `#` 為行首的文字都是註解。


## 執行 shell 命令

```
.PHONY: hello
hello:             
    echo "Hello World"
```

這時當我們執行 `make hello`，呈現的結果如下：

```
echo "Hello World"
Hello World
```

執行的命令與結果會一起輸出，若是想要命令不會輸出到 `stdout` 可以加入符號 `@` 避免

```
@echo "Hello World"
```

我們再執行 `make hello`，則結果如下：

```
Hello World
```