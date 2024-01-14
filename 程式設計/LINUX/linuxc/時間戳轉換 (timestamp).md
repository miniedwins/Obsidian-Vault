首先獲取 timestamp

``` c
time_t timestamp = time(NULL); // 1685268417
printf("Timestamp: %ld\n", timestamp);
```

宣告 `timeinfo` 並且使用函數 `strftime` 將時間複製到 buffer array

``` c
struct tm *timeinfo;
timeinfo = localtime(&timestamp);

char buffer[32];
strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", timeinfo);
printf("Date: %s\n", buffer); // 2023-05-28 18:06:57
```
