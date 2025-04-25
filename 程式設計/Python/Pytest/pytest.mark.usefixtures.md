在 `pytest` 中，`@pytest.mark.usefixtures` 是一個裝飾器（decorator），用於將一個或多個 **fixtures** 應用到測試函數或測試類中，而無需在測試函數的參數列表中顯式聲明它們。這在以下情況下特別有用：

- 當多個測試函數或測試類需要相同的 fixtures 時，可以避免重複代碼。
    
- 當 fixture 主要用於 **setup/teardown**（例如初始化資源、清理資料庫）而不需要直接返回值時。
    

---

### **基本用法**

#### 1. **應用於測試函數**

假設有一個 fixture `setup_database`，你想在多個測試函數中使用它，但不需要它的返回值：

python

复制

import pytest

@pytest.fixture
def setup_database():
    print("\nSetting up database...")
    yield  # 這裡可以進行 teardown
    print("\nTearing down database...")

@pytest.mark.usefixtures("setup_database")
def test_query_data():
    print("Running test_query_data")
    assert True

def test_another_function():
    print("This test does NOT use setup_database")

**輸出**：

复制

Setting up database...
Running test_query_data
Tearing down database...
This test does NOT use setup_database

#### 2. **應用於測試類**

如果整個測試類都需要某個 fixture，可以將 `@pytest.mark.usefixtures` 應用到類上：

python

复制

@pytest.mark.usefixtures("setup_database")
class TestDatabase:
    def test_insert(self):
        print("Running test_insert")
        assert True

    def test_delete(self):
        print("Running test_delete")
        assert True

**輸出**：

复制

Setting up database...
Running test_insert
Tearing down database...

Setting up database...
Running test_delete
Tearing down database...

---

### **進階用法**

#### 1. **多個 Fixtures**

可以同時應用多個 fixtures（按順序執行）：

python

复制

@pytest.fixture
def fixture_a():
    print("\nFixture A")

@pytest.fixture
def fixture_b():
    print("Fixture B")

@pytest.mark.usefixtures("fixture_a", "fixture_b")
def test_multiple_fixtures():
    print("Running test")

**輸出**：

复制

Fixture A
Fixture B
Running test

#### 2. **與參數化 Fixtures 結合**

如果 fixture 需要參數化（例如透過 `@pytest.fixture(params=...)`），`@pytest.mark.usefixtures` 也會自動處理參數化邏輯：

python

复制

@pytest.fixture(params=["apple", "banana"])
def fruit(request):
    return request.param

@pytest.mark.usefixtures("fruit")
def test_fruit(fruit):  # 仍然可以接收 fixture 的返回值
    assert fruit in ["apple", "banana"]

---

### **注意事項**

1. **返回值的使用**：
    
    - 如果需要在測試中訪問 fixture 的返回值，仍需在測試函數的參數列表中聲明該 fixture。
        
    - `@pytest.mark.usefixtures` 僅適用於不需要返回值的 fixtures（例如 setup/teardown）。
        
2. **執行順序**：
    
    - Fixtures 會按照 `@pytest.mark.usefixtures` 中列出的順序執行。
        
3. **與 `autouse=True` 的區別**：
    
    - `@pytest.fixture(autouse=True)` 會自動應用於所有測試，無需標記。
        
    - `@pytest.mark.usefixtures` 則需要顯式標記測試函數或類。
        

---

### **實際應用場景**

- **初始化資源**：例如啟動瀏覽器（Selenium）、連接資料庫。
    
- **清理環境**：測試後刪除臨時文件或重置資料庫狀態。
    
- **共用配置**：例如設定全域變數或模擬登入狀態。
    

透過 `@pytest.mark.usefixtures`，可以讓測試代碼更簡潔，並集中管理共同的依賴邏輯。