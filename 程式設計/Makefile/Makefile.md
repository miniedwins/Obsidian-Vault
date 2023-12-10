## 語法

```
target: 目標檔1 目標檔2 
<tab>gcc -o 欲建立的執行檔 目標檔1 目標檔2
```

- makefile 語法中之 `<tab>` 與空白：
    - 所有的法則必須在同一行，而且行首必須為 `<tab>`；不能為空白。
    - 行尾如果有一個空白，會造成 make 命令執行錯誤。

- **變數（巨集）定義**  
    可讓我們脫離那些冗長乏味的編譯選項，縮減撰寫 `Makefile` 的撰寫成本，如︰  
    　`OBJECTS= filea.o fileb.o filec.o`   
    使用時在前面加 `$()` 的符號，如︰`$(OBJECTS)`
    
- `:=`  
    變數的值決定於它在 `Makefile` 中的位置，而非整個 `Makefile` 展開後最終的值
    
- `?=`  
    若變數未定義，則替它指定新的值。否則，採用原有的值。  
    如: `FOO ?= bar`  
    若 FOO 未定義，則 FOO = bar；若 FOO 已定義，則 FOO 的值維持不變。
    
- `+=`  
    此時 CFLAGS 的值就變成 -Wall -g -O2
```
CFLAGS = -Wall -g
CFLAGS += -O2
```

- 注意事項
    - `=` 與 `?=` 會延後至它們被使用時，才會被展開
    - `:=` 則會立即展開右邊的值

- SHELL HACK  
    若你想在專案編譯之前，執行一些 shell 命令，可藉由 `:=` 一開始便會被 make 執行的特性來達成
```
SHELL_HACK := $(shell mkdir -p BUILD)
```

## 目標

該專案所要建立的檔案，必須以 `:` 結尾。例：

```
foo.o: common.h
    gcc -c foo.c 
```

- `foo.o` 是這個專案要建立的檔案; `common.h` 是相依性的項目/檔案; `gcc -c foo.c` 則為要產生這個項目所要執行的命令。

- make 若發現 target（目標項目/檔案）比較新，也就是 dependencies（相依項目/檔案）都比 target 舊，那麼將不會重新建立 target，如此可以避免不必要的編譯動作。

- 若該項目並非檔案，則為 fake 項目。如此一來將不會建立 target 檔案。但為了避免 make 有時會無去判斷 target 是否為檔案或 fake 項目，建議利用 .PHONY 來指定該項目為 fake 項目。例：

```
.PHONY: clean
clean:
    rm *.o
```

- 在上例中，若不使用 `.PHONY` 來指定 `clean` 為 fake 項目的話，若目錄中同時存在了一個名為 clean 的檔案，則 clean 這個項目將被視為要建立 clean 這個檔案，但 clean 這個項目卻又沒有任何的 dependencies，也因此，clean 項目將永遠被視為 up-to-date，永遠不會被執行。

- 因為利用 `.PHONY` 來指定 clean 為 fake 項目，所以 make 不會去檢查目錄中是否存在一個名為 clean 的檔案。如此也可提昇 make 的執行效率。
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

## 自動化變數

- `$@` 工作目標檔名
- `$<` 第一個必要條件的檔名
- `$^` 所有必要條件的檔名，並以空格隔開這些檔名 (這份清單已移除重複的檔名)
- `$*` 工作目標的主檔名

## 萬用字元

`Makefile` 中所用的萬用字元是 `%`，代表所有可能的字串，前後可接指定的字串來表示某些固定樣式 (pattern) 的字串。例如 `%.c` 表示結尾是 `.c` 的所有字串。因此我們可改寫 `Makefile` 如下 :

```
CC = gcc
OBJS = a.o b.o c.o

all: test

%.o: %.c
  $(CC) -c -o $@ $<

test: $(OBJS)
  $(CC) -o $@ $^
```

## 註解

```
target: object
# 我是 Makefile 註解
```

`Makefile` 的註解（comment）：
    - `#` 只有行首的文字都是註解。