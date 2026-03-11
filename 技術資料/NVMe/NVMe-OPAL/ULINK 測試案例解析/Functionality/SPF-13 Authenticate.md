## 測試目的
核心目的是在測試硬碟（TPer）是否支援「在連線建立之後，進行『明確的額外身分驗證 (Explicit Authentication)』」的機制

## 測試描述 (草稿待修改)


## 測試流程拆解

1. **建立一般連線 (StartSession)**： 測試程式首先向 Admin SP 發起 `StartSession` 建立連線，但**沒有**在參數裡帶入特殊的簽章權限（HostSigningAuthority）與密碼。這代表此時的連線可能只具備最低的 Anybody 權限。

2. **中途發起認證 (Invoke Authenticate method)**： 在連線開啟的狀態下，測試程式對硬碟發送 `Authenticate` 方法，並附上兩個參數：
    - `Authority`：指定我要認證為 `SID`（硬碟擁有者、最高管理者）。
    - `Proof`：附上 SID 的密碼（C_PIN_SID 的 PIN 值）。

3. **驗證權限是否生效 (Invoke Get method)**： 為了確認剛剛的 `Authenticate` 真的有讓這個連線取得 SID 的權限，測試程式接著發送 `Get` 方法，嘗試去讀取 SID 密碼物件 (C_PIN) 的 UID 欄位。

4. **結束連線 (Close Session)**： 關閉連線。