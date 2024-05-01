使用 `time.h` 標頭檔

```
#include <time.h>
```

範例程式碼  : 

```
time_t timestamp = time(NULL);
printf("Timestamp: %ld\n", timestamp); // 1685268417

struct tm *timeinfo;
timeinfo = localtime(&timestamp);

char buffer[32];
strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", timeinfo);
printf("Date: %s\n", buffer); // 2023-05-28 18:06:57
```