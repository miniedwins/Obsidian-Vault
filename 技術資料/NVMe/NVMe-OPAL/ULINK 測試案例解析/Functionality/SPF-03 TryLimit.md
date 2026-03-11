## 測試目的
驗證各權限身份密碼錯誤次數限制 (TryLimit) 與權限鎖定機制。

## 測試描述
在 TCG 架構下，主機端 (Host) 與 TPer 的 Admin SP 或 Locking SP 建立連線時需進行身分驗證。系統內的各權限身份 (Authorities，包含管理者與一般使用者) 皆設有密碼以及「容錯次數上限 (TryLimit)」。

本測試主要驗證：當特定身分的**連續登入失敗次數 (Tries) 達到其設定上限 (TryLimit)** 時，TPer 是否能確實啟動安全防護機制，拒絕該身分後續的連線請求，並正確回傳 `AUTHORITY_LOCKED_OUT` (0x12) 的狀態碼。