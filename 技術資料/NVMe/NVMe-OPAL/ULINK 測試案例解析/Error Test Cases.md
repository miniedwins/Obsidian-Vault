
## ETC-05: Unexpected Token Outside of Method – Regular Session

#### 測試說明
1. 驗證當 TPer 遇到「Token 錯位（也就是格式錯誤）」且該錯位發生在「方法呼叫範圍之外 (Outside of Method)」時，是否會正確地啟動防呆機制強制中斷會話 (Abort Session)。
2. 測試會刻意將一個 **End List Token** 放在開頭的 **Call Token** 之前來觸發異常。

#### 期望結果
1. 包含錯位 Token 的指令將無法獲得正常的 Method 執行回應
2. `IF-RECV` 會讀取到空封包 (“All Response(s) returned - no further data”)或是收到由 TPer 發出的 `CloseSession` 通知 (代表連線已被強制中斷)。
3. 該異常封包內的 Set 方法將被 TPer 捨棄，設定不會生效。

#### 測試行為
1. **前置確認**：開啟正常連線，確認 User1 Authority 的 Enabled 欄位狀態為 `TRUE`。
2. **觸發異常**：發送一個嘗試將 User1 Enabled 設為 `FALSE` 的 Payload，但刻意將一個 **End List Token** 放在開頭的 **Call Token** 之前，製造 Unexpected Token 錯位。

![](assets/Error%20Test%20Cases/file-20260309111224464.png)

3. **接收結果**：透過 `IF-RECV` 讀取緩衝區，驗證是否收到空封包或 `CloseSession`。

![](assets/Error%20Test%20Cases/file-20260309111255531.png)


## ETC-06: Unexpected Token in Method Header – Regular Session

#### 測試說明

#### 期望結果
回傳 NOT_AUTHORIZED。

#### 測試行為

## ETC-07: Unexpected Token Outside of Method – Control Session

#### 測試說明

#### 期望結果

#### 測試行為

## ETC-08: Unexpected Token in the Method Parameter List – Control Session

#### 測試說明

#### 期望結果

#### 測試行為

## ETC-09: Exceeding Transaction Limit
#### 測試說明
1. 這是測試兩次傳送 IF-SEND 命令
2. 基本最大傳送會是設定為1次

#### 期望結果

#### 測試行為

## ETC-10 Invalid Invoking ID - Get

### 測試案例 (1)
#### 測試說明 
此測試是要驗證調用 LockingInfo table 不存在的 Invoking ID。

#### 期望結果
回傳 NOT_AUTHORIZED。

#### 測試行為
1. 啟動了一個 Session，使用的是 Locking SP（安全提供者）的 UID，並以 Admin1（管理者1）的身份作為授權者。
2. 調用無效的 Invoking UID : 00 00 08 01 AA BB CC DDh ( UNKNOWN )
3. 調用有效的 Method UID : 00 00 00 06 00 00 00 17h ( Set )

![[Pasted image 20250519141449.png]]

返回執行結果為 NOT_AUTHORIZED。

![](assets/Error%20Test%20Cases/file-20260309170541528.png)

### 測試案例 (2)
#### 測試說明 
此測試驗證在位元組表 ( Byte Table )上呼叫 Get 方法，但是沒有權限可以檢索內容。

#### 期望結果
回傳 NOT_AUTHORIZED or SUCCESS 以及 Empty Result List。

#### 測試行為
1. 啟動了一個 Session，使用的是 Locking SP（安全提供者）的 UID，並以 Anybody 的身份作為授權者 (Admins 權限才可以檢索 DataStore內容)。
2. 調用 Get method on Invoking UID of 00 00 10 01 00 00 00 00 ( DataStore table )

![[Pasted image 20250519152137.png]]

返回執行結果為 NOT_AUTHORIZED。

![[Pasted image 20250519152226.png]]

### 測試案例 (3)
#### 測試說明 
這個測試驗證的是登入者的權限，去讀取一個 Object Tabel，但是該 ACE 表格有限定誰可以讀取的權限，以及這個表格是否有限定那些欄位一定是無法讀取，若是無法讀取則會不回傳，可以讀取的則會回傳

#### 期望結果
回傳 SUCCESS and only returns the CharSet, TryLimit, and Tries column values。 

#### 測試行為
1. 啟動了一個 Session，使用的是 Locking SP（安全提供者）的 UID，並以 Admin1（管理者1）的身份作為授權者。
2. 調用 Get method on Invoking UID of 00 00 00 0B 00 01 00 01 ( C_PIN_Admin1 )

![[Pasted image 20250520074422.png]]

3. Data Payload 會帶有要取得 CharSet, TryLimit, and Tries 相關欄位資訊。

![[Pasted image 20250520074444.png]]

返回執行結果可以取得 C_PIN Table Description（CharSet, TryLimit, and Tries）。

![[Pasted image 20250520072911.png]]


![[Pasted image 20250520073304.png]]

### 測試案例 (4)

#### 測試說明
這個是測試 ACL Table 表格中不存在的組合，例如: 呼叫一個 InvokingID/MethodID，但是該UID 在表格中並沒有提到可以使用 Get MethodID 去檢索這個 Object。

#### 期望結果
回傳 NOT_AUTHORIZED。

#### 測試行為

---
### ETC-11 Invalid Invoking ID – Non-Get
#### 測試說明
1. 此測試是要驗證調用 LockingInfo table 不存在的 Invoking ID。
2. 該測試所調用的是 Set Method。

#### 期望結果
回傳 NOT_AUTHORIZED。

#### 測試行為
1. 調用無效的 Invoking UID : 00 00 08 01 00 00 00 05h ( UNKNOWN )
2. 調用有效的 Method UID : 00 00 00 06 00 00 00 17h ( Set )

備註 : 官方測試案例所調用的是無效的 UID of 00 00 08 01 00 00 00 05。

![[Pasted image 20250407092200.png]]

返回執行結果 NOT_AUTHORIZED。

![[Pasted image 20250407092621.png]]

---
### ETC-13 Malformed ComPacket Header Regular Session
#### 測試說明
此測試是要驗證 **ComPacket 的長度超過 `MaxComPacketSize-20`** 時，TPer 的處理行為是否正確。

#### 期望結果
回傳 no further data。

#### 參數說明
MaxComPacketSize = 10B8h
MaxPacketSize = 10A6h
Data Pay Load = 10A6h - 20Bytes ( ComPacket Header )

#### 測試行為
- 不太清楚為什要用 MaxComPacketSize - 20 作為 Data Pay Load。
- ComPacket 封包會因為 Payload 大小而最終導致超過 MaxComPacket Size，符合測試案例。

![[Pasted image 20250407073546.png]]

---
### ETC-14 Exceed TPer Properties Regular Session
#### 測試說明
此測試是要模擬主機端發送 MaxSubPackets + 1 時，也就是 Packet 帶有多個 SubPacket。

#### 期望結果
回傳 no further data。

#### 參數說明
MaxSubPackets: TPer 宣告的最大可接受封包數量。

#### 測試行為
1. 寫入資料到 Data Store Table
2. 發送多個 Subpacket 封包 ( Subpacket 1  +Subpacket 2 )

![[Pasted image 20250407062258.png]]

---
