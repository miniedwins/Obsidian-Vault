## 測試目的
驗證當主機 (Host) 在建立連線時給定了一個**「任意且非預設的 HSN」，硬碟端是否能正確識別，並在後續的回應中正確對應並回傳這組由主機提供的 HSN。

## 測試描述
主機向 Admin SP 發起 `StartSession` 方法要求建立連線（使用 SID 權限），但這次故意將參數 `HostSessionID` 填入一個任意變化的 HSN (ARBITRARILY_VARYING HSN)，而不是平常的 `1`。

## 期望結果
