
1. **傳輸單元大小一致性**
    - 除了訊息的最後一個封包外， 一個 Message 內的所有封包，其 **MCTP Transmission Unit (MTU)** 大小必須相同，且需符合雙方事先協商好的 **MTU Size**。
        
2. **最後一個封包 (EOM=1) 的大小**
    - 當封包是 Request/Response Message 的最後一個封包 (EOM bit = 1) 時，  
        其大小應為剛好能容納剩餘的 Payload。        
    - **不可額外填充 (padding)**，除非是物理層需要的對齊或尾碼 (trailer)。
        
3. **完整 Message 的驗證** 
    - 當所有封包組合成完整的NVMe-MI Message後：        
        - 驗證 Message Integrity Check (MIC)。 
        - MIC 通過 → Message 交由 NVMe-MI 處理。            
        - MIC 失敗 → Message 被丟棄 (不處理)。