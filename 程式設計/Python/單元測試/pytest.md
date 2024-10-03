# Pytest

## @pytest.mark.skip

### 設定跳過整個模組

當 allow_module_level=True 時，可以設定在模組等級跳過整個模組

Args : 
- msg = "Your Reason"
- allow_module_level = True

Example : 
```python
if sys.platform.startswith("linux"):
    pytest.skip("Only tests for Windows platform", allow_module_level=True)
```
