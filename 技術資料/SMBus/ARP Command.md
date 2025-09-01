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

### 動作與參數
**Action** : always ACK; if (UDID match) then PROCESS.
**AR Flag** : SET if UDID matches.
**AV Flag** : SET if UDID matches.

### 概述說明
- 這個命令是 **ARP Controller 用來指定新目標位址 (Target Address)** 給某一個特定裝置。    
- 指定的依據是裝置的 **UDID (Unique Device ID)**。    
- 所有 ARP-capable 裝置都必須同時監聽這個封包，逐一比對 UDID。    
    - 如果 UDID 不符合 → 必須 **NACK 當前或下一個位元組**，表示「我不是目標」。        
    - 如果 UDID 完全符合 → 該裝置會 **接受新的 Target Address**。

### 執行後的狀態解釋
- **目標裝置 (UDID match)**    
    - **AR Flag**：設為 SET → 表示它現在已被指派一個解析完成的位址。        
    - **AV Flag**：設為 SET → 表示它目前有一個有效的目標位址。        
    - 該裝置必須立即採用新的位址，並且若支援 **Persistent Target Address (PTA)**，還要將這個位址寫入其持久設定中。        
    - 注意：新位址的 **LSB (bit0)** 必須忽略（因為 SMBus 位址只使用高 7 bits）。
        
- **非目標裝置 (UDID mismatch)**    
    - 在比對 UDID 過程中，一旦發現不符，裝置必須在「當前 byte 或下一個 byte」對總線送出 **NACK**，以示「我不是目標」。        
    - 這樣可讓 ARP Controller 在傳送過程中即時判斷目標是否存在。

### PEC (Packet Error Code) 機制
- **如果 PEC 正確** → 目標裝置會 **ACK PEC**，並真正採用新位址。    
- **如果 PEC 錯誤** → 目標裝置必須 **NACK PEC**，而且 **忽略這次的指派命令**。 

### 補充重點
- 即使裝置的 **AR Flag 已經是 SET**，它也必須回應此命令（允許重新指派位址）。   

## Reset Device

### Direct
#### 動作與參數
**Action** : if ( AV = 1 ) then ACK/PROCESS; else NACK/REJECT.
**AR Flag** : 清除 (CLEAR) 
**AV Flag** : 依裝置類型而定
	- **Non-PTA** → CLEAR        
    - **DTA** → SET        
    - **PTA** → NO CHANGE

#### 概述說明
這個命令是 **針對特定裝置** 的 ARP（Address Resolution Protocol）重置指令。
- 它只能發送給 **ARP-capable 裝置**。 
- 如果控制器在傳送過程中偵測到 **NACK**，表示沒有 ARP-capable 裝置存在。
- 控制器會直接指定某個目標位址，並要求該裝置清除 ARP 相關狀態。    
- 它不是「一般性的硬體 reset」，而是僅限於 **ARP 功能相關的重置**。
- 如果裝置的 UDID 中包含隨機數，它必須在這個 Reset 之後 **重新產生新的隨機數**。

#### 執行後的狀態解釋
- **Non-PTA (非 Persistent Target Address 裝置)**   
    - AR Flag：清除 (CLEAR)        
    - AV Flag：清除 (CLEAR) → 表示裝置不再有有效位址        
    - 裝置會回到「剛上電、尚未被指派位址」的狀態。
        
- **PTA (Persistent Target Address 裝置)**    
    - AR Flag：清除 (CLEAR)        
    - AV Flag：不變 (NO CHANGE) → 因為 PTA 的位址是持久性的，不能輕易消失        
    - 換句話說，PTA 保留它的有效位址，但會重新進入「尚未完成 AR」的狀態。
        
- **DTA (Default Target Address 裝置)**    
    - AR Flag：清除 (CLEAR)        
    - AV Flag：設為 SET → 因為 DTA 裝置必須回到它的 **預設位址**，這個位址永遠是有效的。

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