
```c
#include <stdio.h>

#ifdef DEBUG
    #define debug(fmt,args...) printf (fmt ,##args)
    #define debugX(level,fmt,args...) if (DEBUG>=level) printf(fmt,##args);
#else
    #define debug(fmt,args...)
    #define debugX(level,fmt,args...)
#endif  
```

程式編譯階段定義 DEBUG 

```shell
$ gcc -DDEBUG debug.c -o test 
```
