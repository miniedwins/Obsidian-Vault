## 旗標定義
1. AV Flag ( Address Valid )  
    - 說明 → 表示裝置是否擁有一個「有效的 Target Address」。        
    - SET → 有有效的地址。        
    - CLEARED → 沒有有效的地址。
        
2. AR Flag ( Address Resolved )    
    - 說明 → 表示裝置是否已經經過 ARP Controller 的「位址解析」流程。        
    - SET → 這個地址已經被 ARP Controller 確認並綁定。 
    - CLEARED → 還沒有被解析/確認。

![[Pasted image 20250825105643.png]]

## 四種組合狀態

### 1. AR = Cleared, AV = Cleared
- 裝置沒有有效 Target Address，必須參加 ARP 流程。        
- 這是 Power-On Reset 的初始狀態，特別是對 Non-PTA 裝置 或者 PTA 尚未被分配地址時。        
- 重點 : 剛開機 / 等待分配

### 2. AR = Set, AV = Cleared
- 非法狀態 (Illegal state)

### 3. AR = Cleared, AV = Set
- 裝置有一個有效的地址，但仍必須參加 ARP 流程。        
- 表示裝置雖然知道一個地址，但尚未經過 ARP Controller 的確認。 
- 重點 : 有地址但未解析

### 4. AR = Set, AV = Set
- 裝置已經有一個有效地址，且該地址已經被 ARP Controller 確認。
- 裝置不會再回應 General Get UDID 指令。
- 但 ARP Controller 仍可用 Assign Address 指令修改它的地址。        
- 重點 : 地址已確認
