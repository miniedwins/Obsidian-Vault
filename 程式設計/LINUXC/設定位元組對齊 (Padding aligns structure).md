設定方法 (一)

``` c
typedef struct struct_A {
    char a;
    int b;
    char c;

} __attribute__((__packed__)) struct_t;
```

設定方法 (二)

``` c
typedef struct  __attribute__((__packed__)) mystruct_A {
    char a;
    int b;
    char c;
} mystruct_t;
```