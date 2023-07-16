
```python
import hashlib

# 建立 MD5 物件
m = hashlib.md5()

# 計算雜湊值的資料
data = "md5"

# 更新雜湊值
m.update(data)

# 取得 MD5 雜湊值
v = m.hexdigest() // return string value
print(v)
```