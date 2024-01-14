
問題描述 : 
error: ‘O_DIRECT’ undeclared (first use in this function); did you mean ‘O_DIRECTORY’?

解決方法 :
在程式碼最頂端加入 `_GNU_SOURCE`，方法如下

```
#define _GNU_SOURCE
... 標頭檔

#inclue <stdio.h>
#inclue <stdlib.h>
```