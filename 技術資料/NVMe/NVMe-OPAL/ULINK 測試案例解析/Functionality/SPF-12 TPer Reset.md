## 測試目的
本測試的主要目的是驗證：當硬碟（TPer）接收到 `TPER_RESET` 指令（即 Programmatic Reset 程式化重置）。

如果某個鎖定範圍（Locking Range）的重置觸發條件（`LockOnReset`）包含了 `Programmatic`，則在執行 `TPER_RESET` 後，該範圍必須從「解鎖狀態」自動恢復為「上鎖狀態（ReadLocked 與 WriteLocked 變成 TRUE）」。

## 測試描述 (草稿待修改)
### Test Case 1

MBREnable=FALSE

驗證當硬碟的 `MBRControl` 表格中 `DoneOnReset` 包含 `Programmatic` 條件時，發送 `TPER_RESET` 是否會強制將 `Done` 欄位重置為 `FALSE`，從而恢復 MBR 的唯讀遮蔽狀態。

### Test Case 2

MBREnable=TRUE

驗證當特定資料鎖定範圍 (Locking Range) 的 `LockOnReset` 屬性包含 `Programmatic` 條件時，發送 `TPER_RESET` 是否會自動將該範圍的讀寫權限重新上鎖。