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

