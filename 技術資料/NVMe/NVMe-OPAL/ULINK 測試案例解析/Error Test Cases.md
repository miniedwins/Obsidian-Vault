
## ETC-05: Unexpected Token Outside of Method – Regular Session

#### 測試說明
驗證當 TPer 遇到「Token 錯位（也就是格式錯誤）」時，是否會正確地啟動防呆機制並強制中止連線。

#### 期望結果
回傳 ABORT SESSION

#### 測試行為
1. 設定 User1 Authority = False (以一個簡單的設定方式作為驗證手段)
2. 設定 Payload 內容把，最後的 **End list Token** 放在了 **Call Token** 之前，因此造成了 Token 錯位，也就是 Unexpected Token。

![](assets/Error%20Test%20Cases/file-20260309111224464.png)

2. 然後主機發送 IF-RECV 命令讀取執行結果，回傳的會是 TPer Close Session。

![](assets/Error%20Test%20Cases/file-20260309111255531.png)


## ETC-06: Unexpected Token in Method Header – Regular Session

#### 測試說明

#### 期望結果
回傳 NOT_AUTHORIZED。

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

返回執行結果 no further data，但是官方測試案例則表示回傳 NOT_AUTHORIZED。

這邊猜測應該是 no further data 比較會是對的。因為測試身份是使用  Admin1 去調用不存在的Invoking ID，因此不應該回傳未授權 ( NOT_AUTHORIZED ) 的狀態。

![[Pasted image 20250519144343.png]]

### 測試案例 (2)
#### 測試說明 
此測試驗證在位元組表 ( Byte Table )上呼叫 Get 方法，但是沒有權限可以檢索內容。

#### 期望結果
回傳 NOT_AUTHORIZED or SUCCESS 以及 Empty Result List。

#### 測試行為
1. 啟動了一個 Session，使用的是 Locking SP（安全提供者）的 UID，並以 Anybody 的身份作為授權者。
2. 調用 Get method on Invoking UID of 00 00 10 01 00 00 00 00 ( DataStore table )

![[Pasted image 20250519152137.png]]

返回執行結果 NOT_AUTHORIZED。

![[Pasted image 20250519152226.png]]

### 測試案例 (3)
#### 測試說明 


#### 期望結果
回傳 SUCCESS and only returns the CharSet, TryLimit, and Tries column values。 

#### 測試行為
1. 啟動了一個 Session，使用的是 Locking SP（安全提供者）的 UID，並以 Admin1（管理者1）的身份作為授權者。
2. 調用 Get method on Invoking UID of 00 00 00 0B 00 01 00 01 ( C_PIN_Admin1 )

![[Pasted image 20250520074422.png]]

3. Data Payload 會帶有要取得 CharSet, TryLimit, and Tries 相關欄位資訊。04h 06h 應該有表示
 C_PIN Table Description 欄位的 Column Number 範圍 ***（目前尚未確定）***。

![[Pasted image 20250520074444.png]]

返回執行結果可以取得 C_PIN Table Description（CharSet, TryLimit, and Tries）。

![[Pasted image 20250520072911.png]]


![[Pasted image 20250520073304.png]]

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
