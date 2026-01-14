


![](assets/Sanitize%20State%20Machine/file-20260114103744498.png)


## IDLE State

**Exit Failure Mode 是一個「安全」的指令**：

- 如果你已經在 Idle 狀態，你手癢又發了一次「退出失敗模式」，控制器也不會報錯 (Invalid Field)，它會當作沒事發生。

這解釋了為什麼我們一直強調 AUSE=1：

- **如果 AUSE=1**：滿足 (c) 的條件，狀態機能透過「Exit Failure Mode」回到 Idle。
    
- **如果 AUSE=0**：不滿足 (c) 的條件，就算你發送了退出指令，狀態機依然會根據 **Restricted Failure** 的規則把你擋下來，不讓你回到 Idle。