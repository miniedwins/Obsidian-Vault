## 測試目的
主要目的是驗證當硬碟經歷斷電重啟 (Power Cycle) 時，TPer 是否會依照規範，正確地將該權限身份 (Authorities) 的密碼錯誤次數計數器 (`Tries`) 自動歸零 (Reset)。

## 測試描述
如果密碼物件 (C_PIN) 的 `Persistence` (持久性) 欄位設定為 `False` (出廠預設值)，則在發生 Power Cycle 後，先前累積的錯誤次數 (`Tries`) 必須被清除為 0。