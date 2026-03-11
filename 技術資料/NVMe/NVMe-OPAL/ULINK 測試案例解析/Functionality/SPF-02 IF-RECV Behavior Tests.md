
## 測試目的
的主要目的，是為了驗證硬碟（TPer）在面對不合理或極端的 IF-RECV（接收指令）時，是否能做出符合規範的提示反應。

## 測試描述
主機是向硬碟寫入一大包資料 (1024 Rows)，然後故意用一個長度太小的 IF-RECV (Transfer Length=1) 去收結果，藉此驗證硬碟會不會正確回報「傳輸長度不足 (insufficient transfer length request)」並給出 `MinTransfer` 的提示。

![](assets/SPF-02%20IF-RECV%20Behavior%20Tests/file-20260311110730055.png)

## 期望結果


## 測試行為




