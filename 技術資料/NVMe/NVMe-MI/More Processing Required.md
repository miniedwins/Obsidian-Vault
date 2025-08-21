MCTP (Management Component Transport Protocol) 為控制訊息定義了最大回應時間。  
當 Management Endpoint 判斷指令處理時間可能超過規範允許的範圍（100ms 或傳輸綁定規範指定的時間），必須回傳 More Processing Required Response，通知控制器處理尚未完成。

當 Endpoint 判斷命令無法在最大回應時間內完成，例如：長時間的指令 **Format NVM** 處理，必須回傳 More Processing Required Response。 此回應表示：處理尚未完成，需要更多時間。