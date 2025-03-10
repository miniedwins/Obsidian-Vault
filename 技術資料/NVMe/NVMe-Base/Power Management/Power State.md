# 電源階段描述 (Power State)

描述各個電源階段表格，說明每個階段有不同的最大電源消耗 (MP)，進入 (Enter) 或是離開 (Exit) 該電源階段的延遲時間，以及不同階段的 `I/O` 效能 (Performance) 與延遲 (Latency) 時間的處理能力。數字越小代表者效能越好，相對的功耗也會越大。

下圖表格是描述各個電源階段的功耗與效能 (參考表格並非真實數據)

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/power_state_descriptor_table.png)

一個控制器最大可以支援 32 個電源狀態，可以發送命令 identify controller 取得 **Number of Power States Supported (NPSS)** 控制器支援數量。目前現階段的應用並不會使用這麼多，根據目前大廠所支援的狀態大多都是 `PS0 ~ PS4`。 `PS0`模式代表最大電源消耗，意思就是說處在這個電源模式下可以發揮工作最大效率，`PS3 & PS4` 模式表示低電源消耗，又稱為 **Non-Operational Power States (NOPS)** ，若是處在 `PS4` 電源狀態下，則該電源消耗是最低的。

*備註 : 每個控制器最少都要支援一個電源狀態，那就是 PS0。*

> 補充 : 有些廠商的控制器韌體只有支援 PS0，可能的原因那就是客戶不考慮耗電量的問題，希望在工作效率上能夠全速運行，並且能夠維持在相對的效能。



若是要了解控制器提供表格的內容，可以發送命令 identify controller 取得電源資訊內容，以下是部份電源表格結構 : 

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/identify_controller/Identify_Controller_Power_State_Descriptor.png)

然後再去尋找每個電源狀態的資料結構的說明，如下圖是部份表格 :

![](https://github.com/miniedwins/learning/blob/main/nvme/pic/identify_controller/Identify_Controller_Power_State_Descriptor_Data_Structure.png)

