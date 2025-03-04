## 參數說明
`BeforeValidator` 用於在 **型別驗證之前** 執行自定義邏輯。它通常用於對輸入資料進行預處理或轉換。

## 使用場景
1. **資料清理**：
    - 在驗證之前，清理或格式化輸入資料。        
    - 例如：去除字串的前後空白、將字串轉換為小寫等。
2. **資料轉換**：
    - 將輸入資料轉換為適合驗證的格式。
    - 例如：將字串數字轉換為整數、將 JSON 字串解析為字典等。
3. **預處理**：
    - 在驗證之前，對資料進行一些必要的處理。
    - 例如：將空值替換為預設值、合併多個欄位等。

## 範例
```python
from pydantic import BaseModel, BeforeValidator
from typing import Annotated

def to_lower(value: str) -> str:
    return value.lower()

class User(BaseModel):
    username: Annotated[str, BeforeValidator(to_lower)]

# 測試
user = User(username="JohnDoe")
print(user.username)  # 輸出: johndoe
```

- **說明**：
    - `BeforeValidator(to_lower)` 會在驗證 `username` 之前，將其轉換為小寫。