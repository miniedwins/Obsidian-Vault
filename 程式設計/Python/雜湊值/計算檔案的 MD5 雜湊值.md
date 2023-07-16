計算一個檔案的 MD5 雜湊值，先讀取檔案內容，再使用`hashlib.md5()`來計算雜湊值

```python
import hashlib

# 檔案名稱
filename = "file.in"
m = hashlib.md5()

# 讀取檔案內容，計算 MD5 雜湊值
with open(filename, "rb") as f:
  buffer = f.read()
  m.update(buffer)

# 取得 MD5 雜湊值
h = m.hexdigest()
print(h)
```

如果檔案比較大的話，可以分批次讀取，每次讀取一部分的內容，並且使用 `update` 來更新雜湊值

下列範例使用 `iter` 迭帶方式讀取資料，直到讀取到空的資料為止

```python
import hashlib

# 檔案名稱
filename = "file.in" 
m = hashlib.md5() 

# 讀取檔案內容，計算 MD5 雜湊值
with open(filename, "rb") as f:
  for chunk in iter(lambda: f.read(4096), b""):
    m.update(chunk) 

# 取得 MD5 雜湊值
h = m.hexdigest()
print(h)
```
