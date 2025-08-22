## Device Categorized
- 欄位說明
- 如何知道裝置有沒有支援 ARP

## Prepare to ARP
ARP Controller 發出命令 `Prepare ARP` ，用於通知所有 ARP Capable 設備：
1. ARP 流程即將開始，所有設備需準備進入地址分配狀態。    
2. 強制清除設備的 `AR`（Address Resolved）標誌，表示當前地址可能被重新分配。    
3. 取消所有待處理的 [[Notify ARP Controller]] 請求，避免衝突。

所有支援 ARP 的設備必須要做下列動作：
1. ACK（確認）此命令的所有位元組 
    - 若任何位元組未被 ACK，ARP Controller 會認為總線上無 ARP 設備（可能因雜訊干擾導致 NACK）。        
    - 建議 ARP Controller 重試此命令，以排除雜訊影響。        
2. 立即清除 `AR` 標誌
    - `AR = 0` 表示設備尚未完成地址解析，需等待後續 `Assign Address` 命令。
3. 取消待處理的 [[Notify ARP Controller]] 命令
    - 設備若是有支援 Host Notify，上電後會發送該命令。因此防止設備在 ARP 過程中主動發送請求，干擾 Controller 的主導權。