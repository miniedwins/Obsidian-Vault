
# Context Engineering 實戰：Hello 專案完整指南

## 📋 目錄
1. [Context Engineering Prompt 設計](#prompt-設計)
2. [專案結構](#專案結構)
3. [完整程式碼](#完整程式碼)
4. [使用說明](#使用說明)

---

## 🎯 Prompt 設計

### **給 AI 的完整 Context Engineering Prompt**

```
你是一位資深的 Python 軟體工程師,擅長設計清晰、可維護的專案架構。

# 任務
請為我建立一個 Python Hello 專案,包含完整的程式碼和資料夾結構。

# 核心功能需求
1. **基本問候功能**
   - 輸入: 使用者名稱
   - 輸出: "Hello ! Edward"
   - 範例: print_hello("Edward") → "Hello ! Edward"

2. **帶日期的問候功能**
   - 輸入: 使用者名稱
   - 輸出: "Hello ! Edward, 2025/12/15"
   - 日期格式: YYYY/MM/DD
   - 範例: print_hello_with_date("Edward") → "Hello ! Edward, 2025/12/15"

# 專案結構要求
1. **資料夾結構**
   - 使用模組化設計
   - 分離設定、核心邏輯、工具函數
   - 包含測試檔案
   - 提供 README 說明文件

2. **全域規則設定**
   - 集中管理所有設定參數
   - 包含日期格式規則
   - 包含問候語格式規則
   - 支援多語言擴展
   - 支援時區設定

# 額外要求（請 AI 自行補充的內容）
1. **錯誤處理**
   - 輸入驗證（空字串、None、特殊字元）
   - 例外處理機制
   - 友善的錯誤訊息

2. **擴展功能**
   - 支援批量問候
   - 支援自訂問候語
   - 支援時段感知（早安、午安、晚安）
   - 支援多種日期格式

3. **程式碼品質**
   - 遵循 PEP 8 規範
   - 完整的 docstring 註解
   - 型別提示（Type Hints）
   - 單元測試

4. **專案管理**
   - requirements.txt（依賴套件）
   - .gitignore
   - 版本控制說明
   - 使用範例

# 輸出格式
請提供:
1. 完整的資料夾結構樹狀圖
2. 每個檔案的完整程式碼
3. 使用說明和範例
4. 測試方法

# 風格要求
- 程式碼註解使用繁體中文
- 變數命名使用英文（遵循 Python 慣例）
- 函數說明使用 Google Style Docstring
- 範例程式碼要可以直接執行
```

---

## 📁 專案結構

```
hello_project/
├── README.md                   # 專案說明文件
├── requirements.txt            # 依賴套件列表
├── .gitignore                 # Git 忽略檔案
├── config/
│   ├── __init__.py
│   └── settings.py            # 全域設定檔
├── core/
│   ├── __init__.py
│   └── greeting.py            # 核心問候邏輯
├── utils/
│   ├── __init__.py
│   ├── date_helper.py         # 日期處理工具
│   └── validator.py           # 輸入驗證工具
├── tests/
│   ├── __init__.py
│   ├── test_greeting.py       # 問候功能測試
│   └── test_validator.py      # 驗證功能測試
├── examples/
│   └── demo.py                # 使用範例
└── main.py                    # 主程式進入點
```

---

## 💻 完整程式碼

### 1. `config/settings.py` - 全域設定

```python
"""
全域設定模組
定義專案中所有的常數、規則和設定
"""

from typing import Dict, Tuple


class GlobalSettings:
    """全域設定類別"""
    
    # ========== 基本問候設定 ==========
    DEFAULT_GREETING: str = "Hello"
    GREETING_SEPARATOR: str = "!"
    
    # ========== 日期格式規則 ==========
    DATE_FORMAT_SHORT: str = "%Y/%m/%d"
    DATE_FORMAT_LONG: str = "%Y/%m/%d %H:%M:%S"
    DATE_FORMAT_ISO: str = "%Y-%m-%d"
    
    # ========== 時區設定 ==========
    TIMEZONE: str = "Asia/Taipei"
    
    # ========== 名稱格式規則 ==========
    CAPITALIZE_NAME: bool = True
    TRIM_WHITESPACE: bool = True
    MAX_NAME_LENGTH: int = 50
    
    # ========== 時段問候語對應 ==========
    TIME_GREETINGS: Dict[str, Tuple[int, int, str]] = {
        "morning": (5, 12, "Good morning"),
        "afternoon": (12, 18, "Good afternoon"),
        "evening": (18, 22, "Good evening"),
        "night": (22, 5, "Good night")
    }
    
    # ========== 多語言支援 ==========
    SUPPORTED_LANGUAGES: Dict[str, Dict[str, str]] = {
        "en": {
            "hello": "Hello",
            "good_morning": "Good morning",
            "good_afternoon": "Good afternoon",
            "good_evening": "Good evening"
        },
        "zh": {
            "hello": "你好",
            "good_morning": "早安",
            "good_afternoon": "午安",
            "good_evening": "晚安"
        }
    }
    
    # ========== 表情符號設定 ==========
    EMOJI_ENABLED: bool = True
    EMOJI_MAP: Dict[str, str] = {
        "default": "👋",
        "morning": "🌅",
        "afternoon": "☀️",
        "evening": "🌆",
        "night": "🌙"
    }
    
    # ========== 錯誤訊息 ==========
    ERROR_MESSAGES: Dict[str, str] = {
        "empty_name": "名稱不能為空",
        "invalid_name": "名稱包含無效字元",
        "name_too_long": f"名稱長度不能超過 {MAX_NAME_LENGTH} 字元",
        "invalid_date_format": "日期格式無效"
    }


# 建立全域設定實例
settings = GlobalSettings()
```

### 2. `utils/validator.py` - 輸入驗證工具

```python
"""
輸入驗證工具模組
提供各種輸入驗證功能
"""

import re
from typing import Tuple
from config.settings import settings


class InputValidator:
    """輸入驗證器"""
    
    @staticmethod
    def validate_name(name: str) -> Tuple[bool, str]:
        """
        驗證名稱的有效性
        
        Args:
            name: 要驗證的名稱
            
        Returns:
            (是否有效, 錯誤訊息)
            
        Examples:
            >>> InputValidator.validate_name("Edward")
            (True, "")
            >>> InputValidator.validate_name("")
            (False, "名稱不能為空")
        """
        # 檢查是否為空
        if not name or not name.strip():
            return False, settings.ERROR_MESSAGES["empty_name"]
        
        # 檢查長度
        if len(name) > settings.MAX_NAME_LENGTH:
            return False, settings.ERROR_MESSAGES["name_too_long"]
        
        # 檢查是否包含特殊字元（允許字母、數字、空格、中文）
        if not re.match(r'^[\w\s\u4e00-\u9fff]+$', name, re.UNICODE):
            return False, settings.ERROR_MESSAGES["invalid_name"]
        
        return True, ""
    
    @staticmethod
    def sanitize_name(name: str) -> str:
        """
        清理和格式化名稱
        
        Args:
            name: 原始名稱
            
        Returns:
            清理後的名稱
        """
        if settings.TRIM_WHITESPACE:
            name = name.strip()
        
        if settings.CAPITALIZE_NAME:
            name = name.title()
        
        return name
```

### 3. `utils/date_helper.py` - 日期處理工具

```python
"""
日期處理工具模組
提供日期格式化和時段判斷功能
"""

from datetime import datetime
from typing import Optional
from config.settings import settings


class DateHelper:
    """日期處理助手"""
    
    @staticmethod
    def get_current_date(format_type: str = "short") -> str:
        """
        獲取當前日期
        
        Args:
            format_type: 格式類型 ("short", "long", "iso")
            
        Returns:
            格式化的日期字串
            
        Examples:
            >>> DateHelper.get_current_date("short")
            '2025/12/15'
            >>> DateHelper.get_current_date("long")
            '2025/12/15 14:30:25'
        """
        now = datetime.now()
        
        format_map = {
            "short": settings.DATE_FORMAT_SHORT,
            "long": settings.DATE_FORMAT_LONG,
            "iso": settings.DATE_FORMAT_ISO
        }
        
        date_format = format_map.get(format_type, settings.DATE_FORMAT_SHORT)
        return now.strftime(date_format)
    
    @staticmethod
    def get_time_period() -> str:
        """
        根據當前時間判斷時段
        
        Returns:
            時段名稱 ("morning", "afternoon", "evening", "night")
            
        Examples:
            >>> # 假設現在是上午 10:00
            >>> DateHelper.get_time_period()
            'morning'
        """
        current_hour = datetime.now().hour
        
        for period, (start, end, _) in settings.TIME_GREETINGS.items():
            if start < end:
                if start <= current_hour < end:
                    return period
            else:  # 跨日情況（如夜間 22:00-5:00）
                if current_hour >= start or current_hour < end:
                    return period
        
        return "default"
    
    @staticmethod
    def get_time_based_greeting() -> str:
        """
        獲取基於時段的問候語
        
        Returns:
            問候語字串
        """
        period = DateHelper.get_time_period()
        
        for key, (_, _, greeting) in settings.TIME_GREETINGS.items():
            if key == period:
                return greeting
        
        return settings.DEFAULT_GREETING
    
    @staticmethod
    def format_custom_date(
        date_obj: datetime,
        format_string: Optional[str] = None
    ) -> str:
        """
        自訂格式化日期
        
        Args:
            date_obj: 日期物件
            format_string: 格式字串
            
        Returns:
            格式化的日期字串
        """
        if format_string is None:
            format_string = settings.DATE_FORMAT_SHORT
        
        return date_obj.strftime(format_string)
```

### 4. `core/greeting.py` - 核心問候邏輯

```python
"""
核心問候邏輯模組
實現所有問候相關功能
"""

from typing import List, Optional
from config.settings import settings
from utils.validator import InputValidator
from utils.date_helper import DateHelper


class GreetingEngine:
    """問候引擎類別"""
    
    def __init__(self, language: str = "en"):
        """
        初始化問候引擎
        
        Args:
            language: 語言代碼 (預設: "en")
        """
        self.language = language
        self.validator = InputValidator()
        self.date_helper = DateHelper()
    
    def print_hello(self, name: str) -> str:
        """
        基本問候功能
        
        Args:
            name: 使用者名稱
            
        Returns:
            問候訊息
            
        Raises:
            ValueError: 當名稱無效時
            
        Examples:
            >>> engine = GreetingEngine()
            >>> engine.print_hello("Edward")
            '👋 Hello ! Edward'
        """
        # 驗證輸入
        is_valid, error_msg = self.validator.validate_name(name)
        if not is_valid:
            raise ValueError(error_msg)
        
        # 清理名稱
        clean_name = self.validator.sanitize_name(name)
        
        # 組合問候語
        greeting = f"{settings.DEFAULT_GREETING} {settings.GREETING_SEPARATOR} {clean_name}"
        
        # 添加表情符號
        if settings.EMOJI_ENABLED:
            emoji = settings.EMOJI_MAP["default"]
            greeting = f"{emoji} {greeting}"
        
        return greeting
    
    def print_hello_with_date(
        self,
        name: str,
        date_format: str = "short"
    ) -> str:
        """
        帶日期的問候功能
        
        Args:
            name: 使用者名稱
            date_format: 日期格式類型
            
        Returns:
            帶日期的問候訊息
            
        Raises:
            ValueError: 當名稱無效時
            
        Examples:
            >>> engine = GreetingEngine()
            >>> engine.print_hello_with_date("Edward")
            '👋 Hello ! Edward, 2025/12/15'
        """
        # 驗證輸入
        is_valid, error_msg = self.validator.validate_name(name)
        if not is_valid:
            raise ValueError(error_msg)
        
        # 清理名稱
        clean_name = self.validator.sanitize_name(name)
        
        # 獲取當前日期
        current_date = self.date_helper.get_current_date(date_format)
        
        # 組合問候語
        greeting = f"{settings.DEFAULT_GREETING} {settings.GREETING_SEPARATOR} {clean_name}, {current_date}"
        
        # 添加表情符號
        if settings.EMOJI_ENABLED:
            emoji = settings.EMOJI_MAP["default"]
            greeting = f"{emoji} {greeting}"
        
        return greeting
    
    def smart_hello(
        self,
        name: str,
        include_date: bool = True,
        use_time_greeting: bool = True
    ) -> str:
        """
        智能問候功能（根據時間自動調整）
        
        Args:
            name: 使用者名稱
            include_date: 是否包含日期
            use_time_greeting: 是否使用時段問候語
            
        Returns:
            智能問候訊息
            
        Examples:
            >>> engine = GreetingEngine()
            >>> # 假設現在是早上
            >>> engine.smart_hello("Edward")
            '🌅 Good morning ! Edward, 2025/12/15'
        """
        # 驗證輸入
        is_valid, error_msg = self.validator.validate_name(name)
        if not is_valid:
            raise ValueError(error_msg)
        
        # 清理名稱
        clean_name = self.validator.sanitize_name(name)
        
        # 選擇問候語
        if use_time_greeting:
            greeting_text = self.date_helper.get_time_based_greeting()
            time_period = self.date_helper.get_time_period()
        else:
            greeting_text = settings.DEFAULT_GREETING
            time_period = "default"
        
        # 組合問候語
        greeting = f"{greeting_text} {settings.GREETING_SEPARATOR} {clean_name}"
        
        # 添加日期
        if include_date:
            current_date = self.date_helper.get_current_date()
            greeting += f", {current_date}"
        
        # 添加表情符號
        if settings.EMOJI_ENABLED:
            emoji = settings.EMOJI_MAP.get(time_period, settings.EMOJI_MAP["default"])
            greeting = f"{emoji} {greeting}"
        
        return greeting
    
    def batch_hello(
        self,
        names: List[str],
        include_date: bool = False
    ) -> List[str]:
        """
        批量問候功能
        
        Args:
            names: 名稱列表
            include_date: 是否包含日期
            
        Returns:
            問候訊息列表
            
        Examples:
            >>> engine = GreetingEngine()
            >>> engine.batch_hello(["Edward", "Sarah"])
            ['👋 Hello ! Edward', '👋 Hello ! Sarah']
        """
        results = []
        
        for name in names:
            try:
                if include_date:
                    greeting = self.print_hello_with_date(name)
                else:
                    greeting = self.print_hello(name)
                results.append(greeting)
            except ValueError as e:
                results.append(f"錯誤 ({name}): {str(e)}")
        
        return results
    
    def custom_hello(
        self,
        name: str,
        greeting_text: Optional[str] = None,
        separator: Optional[str] = None,
        suffix: Optional[str] = None
    ) -> str:
        """
        自訂問候功能
        
        Args:
            name: 使用者名稱
            greeting_text: 自訂問候語
            separator: 自訂分隔符號
            suffix: 自訂後綴
            
        Returns:
            自訂問候訊息
            
        Examples:
            >>> engine = GreetingEngine()
            >>> engine.custom_hello("Edward", "Hi", "~", "Have a nice day!")
            '👋 Hi ~ Edward Have a nice day!'
        """
        # 驗證輸入
        is_valid, error_msg = self.validator.validate_name(name)
        if not is_valid:
            raise ValueError(error_msg)
        
        # 清理名稱
        clean_name = self.validator.sanitize_name(name)
        
        # 使用自訂值或預設值
        greeting_text = greeting_text or settings.DEFAULT_GREETING
        separator = separator or settings.GREETING_SEPARATOR
        
        # 組合問候語
        greeting = f"{greeting_text} {separator} {clean_name}"
        
        if suffix:
            greeting += f" {suffix}"
        
        # 添加表情符號
        if settings.EMOJI_ENABLED:
            emoji = settings.EMOJI_MAP["default"]
            greeting = f"{emoji} {greeting}"
        
        return greeting
```

### 5. `main.py` - 主程式

```python
"""
主程式進入點
展示各種問候功能的使用方式
"""

from core.greeting import GreetingEngine
from utils.date_helper import DateHelper


def print_section(title: str):
    """列印區塊標題"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def main():
    """主函數"""
    print_section("Context Engineering 實戰：Hello 專案示範")
    
    # 建立問候引擎
    engine = GreetingEngine()
    
    # 1. 基本 Hello 功能
    print_section("功能 1：基本 Hello")
    print(engine.print_hello("Edward"))
    print(engine.print_hello("sarah"))
    print(engine.print_hello("JOHN doe"))
    
    # 2. 帶日期的 Hello 功能
    print_section("功能 2：帶日期的 Hello")
    print(engine.print_hello_with_date("Edward"))
    print(engine.print_hello_with_date("Sarah", date_format="long"))
    print(engine.print_hello_with_date("John", date_format="iso"))
    
    # 3. 智能 Hello（時段感知）
    print_section("功能 3：智能 Hello（時段感知）")
    print(engine.smart_hello("Edward"))
    print(engine.smart_hello("Sarah", include_date=False))
    print(engine.smart_hello("John", use_time_greeting=False))
    
    # 4. 批量問候
    print_section("功能 4：批量問候")
    names = ["Edward", "Sarah", "John", "Emily"]
    greetings = engine.batch_hello(names, include_date=True)
    for greeting in greetings:
        print(greeting)
    
    # 5. 自訂問候
    print_section("功能 5：自訂問候")
    print(engine.custom_hello("Edward", "Hi", "~", "Have a great day!"))
    print(engine.custom_hello("Sarah", "Hey", "🎉"))
    
    # 6. 錯誤處理示範
    print_section("功能 6：錯誤處理")
    try:
        print(engine.print_hello(""))
    except ValueError as e:
        print(f"捕捉到錯誤: {e}")
    
    try:
        print(engine.print_hello("a" * 100))
    except ValueError as e:
        print(f"捕捉到錯誤: {e}")
    
    # 7. 顯示系統資訊
    print_section("系統資訊")
    date_helper = DateHelper()
    print(f"當前時段: {date_helper.get_time_period()}")
    print(f"當前日期 (短): {date_helper.get_current_date('short')}")
    print(f"當前日期 (長): {date_helper.get_current_date('long')}")
    print(f"時段問候語: {date_helper.get_time_based_greeting()}")
    
    print("\n" + "=" * 60)
    print("示範完成！")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
```

### 6. `tests/test_greeting.py` - 單元測試

```python
"""
問候功能單元測試
"""

import unittest
from core.greeting import GreetingEngine


class TestGreetingEngine(unittest.TestCase):
    """測試問候引擎"""
    
    def setUp(self):
        """測試前準備"""
        self.engine = GreetingEngine()
    
    def test_print_hello_basic(self):
        """測試基本問候"""
        result = self.engine.print_hello("Edward")
        self.assertIn("Edward", result)
        self.assertIn("Hello", result)
    
    def test_print_hello_with_date(self):
        """測試帶日期問候"""
        result = self.engine.print_hello_with_date("Edward")
        self.assertIn("Edward", result)
        self.assertIn("/", result)  # 日期包含斜線
    
    def test_empty_name_raises_error(self):
        """測試空名稱會拋出錯誤"""
        with self.assertRaises(ValueError):
            self.engine.print_hello("")
    
    def test_name_capitalization(self):
        """測試名稱大寫"""
        result = self.engine.print_hello("edward")
        self.assertIn("Edward", result)
    
    def test_batch_hello(self):
        """測試批量問候"""
        names = ["Edward", "Sarah", "John"]
        results = self.engine.batch_hello(names)
        self.assertEqual(len(results), 3)
        self.assertIn("Edward", results[0])


if __name__ == "__main__":
    unittest.main()
```

### 7. `requirements.txt` - 依賴套件

```
# 無額外依賴，使用 Python 標準庫
# Python >= 3.7

# 開發依賴（可選）
pytest>=7.0.0
black>=22.0.0
flake8>=4.0.0
mypy>=0.950
```

### 8. `README.md` - 專案說明

```markdown
# Hello Project - Context Engineering 實戰範例

## 專案簡介
這是一個展示 Context Engineering 的實戰專案，實現了一個功能完整、結構清晰的 Python 問候系統。

## 功能特色
✅ 基本問候功能
✅ 帶日期問候功能
✅ 智能時段問候（早安/午安/晚安）
✅ 批量問候處理
✅ 自訂問候語
✅ 完整的輸入驗證
✅ 錯誤處理機制
✅ 模組化設計
✅ 單元測試

## 快速開始

### 安裝
```bash
git clone <repository-url>
cd hello_project
```

### 執行
```bash
python main.py
```

### 測試
```bash
python -m pytest tests/
```

## 使用範例

```python
from core.greeting import GreetingEngine

# 建立引擎
engine = GreetingEngine()

# 基本問候
print(engine.print_hello("Edward"))
# 輸出: 👋 Hello ! Edward

# 帶日期問候
print(engine.print_hello_with_date("Edward"))
# 輸出: 👋 Hello ! Edward, 2025/12/15

# 智能問候
print(engine.smart_hello("Edward"))
# 輸出: 🌅 Good morning ! Edward, 2025/12/15
```

## 專案結構
見上方完整的資料夾結構說明

## 自訂設定
修改 `config/settings.py` 來客製化行為：
- 日期格式
- 問候語樣式
- 表情符號
- 語言設定

## 授權
MIT License
```

---

## 🚀 使用說明

### 執行步驟

1. **創建專案資料夾**
```bash
mkdir hello_project
cd hello_project
```

2. **建立所有檔案**
   按照上方的程式碼，建立對應的資料夾和檔案

3. **執行主程式**
```bash
python main.py
```

4. **執行測試**
```bash
python -m pytest tests/ -v
```

### 輸出範例

```
============================================================
  Context Engineering 實戰：Hello 專案示範
============================================================

============================================================
  功能 1：基本 Hello
============================================================
👋 Hello ! Edward
👋 Hello ! Sarah
👋 Hello ! John Doe

============================================================
  功能 2：帶日期的 Hello
============================================================
👋 Hello ! Edward, 2025/12/15
👋 Hello ! Sarah, 2025/12/15 14:30:25
👋 Hello ! John, 2025-12-15

============================================================
  功能 3：智能 Hello（時段感知）
============================================================
🌅 Good morning ! Edward, 2025/12/15
🌅 Good morning ! Sarah
👋 Hello ! John, 2025/12/15
```

---

## 🎓 Context Engineering 關鍵學習點

### 1. **清晰的需求定義**
   - 明確列出核心功能
   - 定義輸入輸出格式
   - 提供具體範例

### 2. **結構化的專案組織**
   - 模組化設計
   - 關注點分離
   - 清晰的命名規範

### 3. **完整的錯誤處理**
   - 輸入驗證
   - 例外處理
   - 友善的錯誤訊息

### 4. **可擴展性**
   - 支援多種格式
   - 支援自訂設定
   - 易於添加新功能

### 5. **文件化**
   - Docstring 註解
   - README 說明
   - 使用範例

---

## 📝 總結

這個專案展示了如何使用 **Context Engineering** 來設計一個完整的程式專案：

1. ✅ **明確的 Prompt 設計** - 清楚告訴 AI 需要什麼
2. ✅ **完整的專案結構** - 模組化、可維護
3. ✅ **全域規則管理** - 集中設定、易於修改
4. ✅ **擴展功能** - 超越基本需求的額外價值
5. ✅ **最佳實踐** - 遵循業界標準

透過良好的 Context Engineering，我們不僅完成了基本需求，還獲得了：
- 🎯 完整的錯誤處理
- 🎯 彈性的擴展功能
- 🎯 清晰的程式碼結構
-