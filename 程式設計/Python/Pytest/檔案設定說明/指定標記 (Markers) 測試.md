
使用標記可以用來分類、篩選或控制測試的行為。

## 範例
首先在 `pytest.ini` 文件中，使用 `markers` 來定義標記及其說明。例如：

```python
# pytest.ini
[pytest]
markers =
    web: Web相關的測試。
    quick: 快速運行的測試。
    slow: 時間較長的測試s。    
```

將需要的測試函數上加上裝飾器。

```python
import pytest

@pytest.mark.web
def test_web_feature():
    pass

@pytest.mark.quick
def test_quick_feature():
    pass
```

指定執行**特定標記的測試**。

```shell
$ pytest -m web test_demo_mark.py # 只運行標記為 "web" 的測試
$ pytest -m quick test_demo_mark.py # 只運行標記為 "quick" 的測試
```

## 進階功能
### (1) 組合標記
你可以同時為一個測試添加多個標記。例如：

```python
@pytest.mark.web
@pytest.mark.quick
def test_web_and_quick():
    assert True
```

運行時可以指定多個標記：

```shell
$ pytest -m "web and quick"
```

### (2) 排除特定標記
你可以使用 `not` 來排除特定標記的測試。例如：

```shell
# 運行所有非 "slow" 標記的測試
$ pytest -m "not slow"
```