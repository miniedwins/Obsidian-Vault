## 參數說明
`AfterValidator` 用於在 **型別驗證之後** 執行自定義邏輯。它通常用於對驗證後的資料進行進一步的檢查或處理。

## 使用場景
1. **資料驗證**： 
    - 在型別驗證之後，執行更複雜的驗證邏輯。
    - 例如：檢查數字是否在特定範圍內、檢查字串是否符合特定格式等。        
2. **資料後處理**：    
    - 在驗證之後，對資料進行進一步的處理。        
    - 例如：將資料轉換為特定的格式、計算衍生欄位等。        
3. **業務邏輯檢查**：    
    - 檢查資料是否符合業務規則。        
    - 例如：檢查用戶名是否已存在、檢查訂單金額是否超過限額等。

## 範例
```python
from pydantic import BaseModel, AfterValidator, ValidationError
from typing import Annotated

def is_even(value: int) -> int:
    if value % 2 == 1:
        raise ValueError(f'{value} is not an even number')
    return value

class Model(BaseModel):
    number: Annotated[int, AfterValidator(is_even)]

# 測試
try:
    model = Model(number=1)
except ValidationError as e:
    print(e)  # 輸出: 1 validation error for Model number Value error, 1 is not an even number [type=value_error, input_value=1, input_type=int]
```

- **說明**：
    - `AfterValidator(is_even)` 會在驗證 `number` 之後，檢查其是否為偶數。