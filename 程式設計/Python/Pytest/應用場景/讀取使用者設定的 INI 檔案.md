## 問題
使用者希望能夠透過 INI 設定檔案來配置測試參數，以便根據不同的測試需求動態調整設定值。這樣可以避免將參數硬編碼在程式碼中，提升測試的 `可配置性` 以及 `可維護性`。

## 解決方法
在專案目錄下建立或修改 `conftest.py`，加上 `pytest_addoption` 來處理 `--ini-file` 參數：

```python
import pytest

def pytest_addoption(parser):
    """
    加入命令列選項來指定 ini 設定檔
    """
    parser.addoption(
        "--ini-file",
        action="store",
        default="myconfig.ini",  # 預設設定檔案
        help="Path to the configuration ini file",
    )

@pytest.fixture
def config_file(request):
    """
    取得 --ini-file 參數值
    """
    return request.config.getoption("--ini-file")
```

執行測試時，您需要手動指定 `--ini-file` 參數，例如：

```shell
$ pytest --ini-file=myconfig.ini
```

如果省略 `--ini-file`，則會自動使用 `default="myconfig.ini"` 作為預設值。

```python
def pytest_addoption(parser):
    """
    加入命令列選項來指定 ini 設定檔
    """
    parser.addoption(
        "--ini-file",
        action="store",
        default="myconfig.ini",  # 預設設定檔案
        help="Path to the configuration ini file",
    )
```