建立物件，計算雜湊值必須要設定編碼格式。

```python
import hashlib

# 建立 MD5 物件
m = hashlib.md5()

# 計算雜湊值的資料
data = "md5".encode('utf-8')

# 更新雜湊值
m.update(data)

# 取得 MD5 雜湊值
v = m.hexdigest() # 回傳字串
print(v) # 1bc29b36f623ba82aaf6724fd3b16718
```