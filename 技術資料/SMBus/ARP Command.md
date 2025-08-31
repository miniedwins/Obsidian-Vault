## Prepare to ARP

### 動作與參數
**Action** : Always ACK/PROCESS
**AR Flag** : CLEAR
**AV Flag** : NO CHANGE

### 概述說明
ARP Controller 發出命令 `Prepare ARP` ，用於通知所有 ARP Capable 設備：
1. ARP 流程即將開始，所有設備需準備進入地址分配狀態。    
2. 強制清除設備的 `AR`（Address Resolved）標誌，表示當前地址可能被重新分配。    
3. 取消所有待處理的 [[Notify ARP Controller]] 請求，避免衝突。

### 執行後的狀態解釋
所有支援 ARP 的設備必須要做下列動作：
1. ACK（確認）此命令的所有位元組 
    - 若任何位元組未被 ACK，ARP Controller 會認為總線上無 ARP 設備（可能因雜訊干擾導致 NACK）。        
    - ARP Controller 會重試此命令，以排除雜訊影響。 
2. 立即清除 `AR` 標誌
    - `AR = 0` 表示設備尚未完成地址解析，需等待後續 `Assign Address` 命令。
3. 取消待處理的 [[Notify ARP Controller]] 命令
    - 設備若是有支援 Host Notify，上電後會發送該命令。因此防止設備在 ARP 過程中主動發送請求，干擾 Controller 的主導權。

## Get UDID

### Directed Get UDID
#### 動作與參數
- **Action** : if (AV = 1) then ACK/PROCESS; else NACK/REJECT.
	- **AV = 0** → 裝置還沒拿到地址 → 回傳 **NACK**。    
	- **AV = 1** → 裝置已經拿到地址 → 回傳 **ACK 並回傳 UDID**。
- **AR Flag** : NO CHANGE
- **AV Flag** : NO CHANGE

#### 概述說明
UDID（Unique Device Identifier）在 **Direct 模式** 下，代表一個控制器想要「直接詢問」匯流排上是否有某個特定裝置存在。

一旦裝置經過 ARP 流程並被分配到 Target Address → **AV = 1**。之後 Controller 對這個裝置發送 **Get UDID (directed)** 時，它才會 ACK 並回傳資料。

#### 執行後的狀態解釋
- 若該 UDID 的裝置存在 → 這個裝置會回應，並與控制器建立 **確認關係**（例如回覆 ACK，或後續配置動態位址）。    
- 若該 UDID 的裝置不存在 → 匯流排上就不會有任何回應，控制器便知道這個裝置不在線。    
- 匯流排上的其他裝置 → 看到這個 Direct 命令，但因為 UDID 不符合自己，就會保持 **靜默**。

### General Get UDID 
#### 動作與參數
- **Action** : if (AR = 0) then ACK/PROCESS; else NACK/REJECT.
- **AR Flag** : NO CHANGE
- **AV Flag** : NO CHANGE

#### 概述說明
ARP Controller 向 bus 上所有「ARP-capable 或可被 Discover」的裝置查詢：    
- 你的 **UDID (Unique Device Identifier)**        
- 以及你目前的 **Target Address**        
- 回覆資料的最後一個 byte = **Data17 (8 bits)**，其中：    
    - **Bit0 (LSB)** = 必須為 `1` (協定規定)        
    - 其他 7 bits = 根據裝置狀態來填

#### 執行後的狀態解釋
- 這樣設計是為了讓 **ARP Controller 可以馬上判斷哪些裝置還沒有有效地址 (AV=0)**。
- 裝置會根據當前 AV Flag ( `0` 或是 `1` ) 狀態回覆
	- **AV=0 (Clear)** : 
		- 如果回傳的 Data17 = `0xFF` (11111111b)，就代表「這個裝置還沒分配 Target Address，需要後續指派」。    
	- **AV=0 (Clear)** : 
		- 如果回傳的是別的 (ex. `0x83` = 1000 0011b)，那就代表「裝置有一個已分配的 Target Address = 0x41 (0x82 >> 1)」。

## Assign Address
#### UDID 比對成功
如果裝置完整比對所有 16 個 UDID 位元組，它必須：
- 立即採用新的 SMBus Address
- 如果支援 Persistent Target Address，要更新它的記憶體設定  

#### NACK 回應時機
這讓 ARP Controller 可透過偵測哪個位元組 NACK，知道哪個裝置「不是」目標。
- 所有 ARP Capable 裝置都必須「監控整個 UDID」內容    
- 若某裝置在比對過程中某一個位元組不符，就應該：
    - 立即送出 NACK（理想情況）
    - 或是在下一個位元組送出 NACK（若無法及時） 

## Reset Device
### General
#### 動作與參數
- **Action**：Always ACK / PROCESS    
- **AR Flag**：清除 (CLEAR)    
- **AV Flag**：依裝置類型而定：    
    - **Non-PTA** → CLEAR        
    - **DTA** → SET        
    - **PTA** → NO CHANGE

#### 概述說明
此命令會讓所有 ARP-capable 裝置回到「初始狀態」，主要影響 ARP 狀態旗標 (AR / AV) 與 Target Address 的有效性。 它不是一般的硬體重置，而是針對 SMBus ARP 機制的邏輯重置。

#### 執行後的狀態解釋
- **DTA (Default Target Address)** 裝置：
    - Reset 後，它會回到「預設目標地址 (Default Address)」。        
    - 既然有一個有效的 Default Address → AV 必須設為 SET。        
- **PTA (Persistent Target Address)** 裝置：    
    - Reset 後，它會保留原本的地址 (因為它是 Persistent)。        
    - 所以AV Flag 不變 (NO CHANGE)**。        
- **Non-PTA (沒有 Persistent Target Address)** 裝置：    
    - Reset 後，它會清除自己的 AV Flag (因為沒有固定的地址)。        
    - 所以 AV = CLEAR。