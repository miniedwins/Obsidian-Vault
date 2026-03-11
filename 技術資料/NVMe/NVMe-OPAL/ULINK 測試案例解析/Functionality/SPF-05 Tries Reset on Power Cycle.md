## 測試目的
主要目的是驗證當硬碟經歷斷電重啟 (Power Cycle) 時，TPer 是否會依照規範，正確地將該權限身份 (Authorities) 的密碼錯誤次數計數器 (`Tries`) 自動歸零 (Reset)。

## 測試描述
為了防止惡意人士使用暴力破解法猜測密碼，系統會透過 `Tries` 欄位記錄每個身分（如 Admin 或 User）連續登入失敗的次數，並在達到上限（`TryLimit`）時鎖定該權限。然而，為了避免使用者因意外被永久鎖定，規範同時定義了錯誤次數的**持久性 (Persistence) 規則**。

1. **非持久性狀態的清除 (Volatile State Clearing)：** 根據規範，密碼物件 (C_PIN) 中設有一個 `Persistence`（持久性）屬性。當該屬性設定為 `False`（通常為出廠預設值）時，表示其累積的錯誤次數 (`Tries`) 屬於「暫態資料」。當硬碟經歷真正的實體斷電並重新供電 (Power Cycle) 後，系統必須自動將這些非持久性的錯誤計數徹底清除歸零。

2. **重置機制的嚴格區分 (Reset Type Differentiation)：** 此機制要求 TPer（硬碟端）必須具備嚴格區分「斷電重啟 (Power Cycle)」與其他軟硬體重置（如 Hardware Reset 或 TCG Reset）的能力。因為規範特別要求，只有真正的「斷電」才能洗掉非持久性的錯誤次數，其他的重置方式均不允許修改 `Tries` 的值，藉此防堵攻擊者利用快速發送 Reset 指令來規避鎖定機制。