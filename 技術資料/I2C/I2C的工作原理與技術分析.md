**(一) I2C簡介**

![圖1.png](https://imageproxy.pixnet.cc/imgproxy?url=https://pic.pimg.tw/rexpighj123/1623635732-534151213-g.png "圖1.png")

圖1. I2C logo

I²C（Inter-Integrated Circuit）是內部整合電路的稱呼，正確唸法是I-squared-C，為了方便打字，本篇文章使用I2C取代I²C 。

I2C是一種串列通訊匯流排(Serial Bus)，由Philips公司在1980年代為了讓主機板、手機及嵌入式系統用以連接低速周邊裝置而發展，主要應用在晶片間的溝通(board-to-board)，它的設計並不能應用到長距離裝置及需要快速溝通的通訊。

不過，I2C bus 可以很便利地被應用在各種控制架構上，如系統管理匯流排(System Management Bus, SMBus)、電源管理匯流排(Power Management Bus, PMBus)、智慧平台管理介面(Intelligent Platform Management Interface, IPMI)、顯示數據通道(Display Data Channel, DDC)、先進電信運算架構(Advanced Telecom Computing Architecture, ATCA)等，而且只有使用到兩根實體線，有效地節省了PCB的排線空間。

I2C的參考設計使用一個7位元長度的位址空間但保留了16個位址，所以在一組匯流排最多可和112個節點通訊。常見的I2C匯流排依傳輸速率的不同而有不同的模式：標準模式（100 Kbit/s）、低速模式（10 Kbit/s），但時脈頻率可被允許下降至零，這代表可以暫停通訊。而新一代的I2C匯流排可以和更多的節點（支援10位元長度的位址空間）以更快的速率通訊：快速模式（400 Kbit/s）、高速模式（3.4 Mbit/s）。

**(二) I2C的實體層**

![圖2.png](https://imageproxy.pixnet.cc/imgproxy?url=https://pic.pimg.tw/rexpighj123/1623635732-3578173057-g_n.png "圖2.png")

圖2. I2C裝置連接示意圖

I2C 的實體界面只有兩根訊號，分別稱之爲 SCL（serial clock）與 SDA（serial data），而由於 I2C 是一個 bus，在這個 bus 上所有的裝置都得透過這兩個訊號線相連，也就是說 I2C 只需要兩根訊號線，就可以讓很多（多達上百個）裝置彼此之間互相通訊，如何讓多個裝置溝通而不打架呢?後續會再詳細說明。

上圖2是一個典型的 I2C bus 電路，bus 上的所有裝置都透過 SCL/SDA 這兩根線相連。I2C 允許 bus 上可以有多個 master、多個 slave 存在，只要彼此的 address 不衝突、裝置數量沒有超過 bus 的電氣特性上限就沒有問題。

在上圖2這個電路中，有兩個電阻，分別將 SCL 和 SDA 拉到 VCC。這兩顆電阻稱之爲 I2C bus 的「上拉電阻」（pull-up resistors, Rp），看起來好像沒什麼複雜的地方，但它們卻是 I2C bus 能正常運作的關鍵，而Rp的電阻值也需要工程師的精心設計。

![圖3.png](https://imageproxy.pixnet.cc/imgproxy?url=https://pic.pimg.tw/rexpighj123/1623635732-669129438-g_n.png "圖3.png")

圖3. I2C實體層

I2C bus 上所有的裝置都是透過 open-drain 或 open-collector 的方式來驅動 SCL 或 SDA。一般 push-pull 的數位邏輯輸出電路會有 high/low 兩顆電晶體，各自負責把輸出拉到 high 或 low 的工作，但 open-drain 或 open-collector 的輸出則只有 low-side 一顆電晶體。

![圖4.png](https://imageproxy.pixnet.cc/imgproxy?url=https://pic.pimg.tw/rexpighj123/1623635732-2682119317-g_n.png "圖4.png")

圖4. Push-pull與Open-drain的驅動方式比較

從圖4的電路可以看出，因爲 open-drain 輸出電路只有 low-side 一顆電晶體，它只能把輸出拉到 low，無法把輸出變成 high，因此當 open-drain 輸出的 low-side 電晶體不導通時，它就會呈現 high-Z 的高阻抗狀態，就好像它沒有接到任何東西一樣。

這個電路的特性是：

(1) 當所有的裝置都輸出 high 時，bus 上的狀態才會是 high

(2) 只要有任何一個裝置輸出 low，bus 上的狀態就會是 low

這樣的電路稱之爲「Wired-AND」，只要了解「Wired-AND」的邏輯，就可以掌握I2C的控制時序了。

![圖5-1.png](https://imageproxy.pixnet.cc/imgproxy?url=https://pic.pimg.tw/rexpighj123/1623635732-4235349171-g.png "圖5-1.png")

![圖5-2.png](https://imageproxy.pixnet.cc/imgproxy?url=https://pic.pimg.tw/rexpighj123/1623635731-3872190483-g.png "圖5-2.png")

圖5. 緩衝器或同相器(Buffer Gate)示意圖及其真值表

圖3除了輸出的電晶體外，還有一個三角形圖案，它是I2C訊號的輸入緩衝器(Buffer Gate, 也稱同相器)，它的用途是要監聽接腳上的狀態，爲什麼要監聽呢？正是因爲這個 bus 的 Wired-AND 特性。

以一個I2C上的裝置device1為例，當device1輸出 low 時，bus 上一定是 low，但是當device1輸出 high 時，bus 上卻不一定是 high，只有當其它所有的device都輸出 high，而且device1也輸出 high 時，bus 才會是 high，如果有任何一個其它裝置輸出 low，即使device1輸出 high，bus 的狀態也會是 low。

因此當device1在輸出 high 時，藉由監聽 bus 的狀態，可以得知是不是有其它的裝置在輸出 low，這個特性對 I2C bus 的 仲裁(Arbitration)非常有用，後面會再說明。

**(三) I2C的操作原理**

1. I2C的訊號邏輯規則

![圖6.png](https://imageproxy.pixnet.cc/imgproxy?url=https://pic.pimg.tw/rexpighj123/1623635731-3917842145-g_n.png "圖6.png")

圖6. 資料的有效性(Data Validity)

I2C bus上的訊號邏輯有以下規則：

1. I2C bus 為 idle high，也就是當 bus 上沒有任何活動時，SCL 和 SDA 都維持在 high。
2. SCL 為 high 時，表示 SDA 上的資料為有效(Data Validity)，此時 SDA 的狀態不能改變，以確保接收方可以取樣到正確的 SDA 狀態。
3. SCL 為 low 時，SDA 的狀態可以改變。
4. 當 SCL 為 high 時，如果 SDA 變動，有兩種特殊狀況：SCL high、SDA 下降代表START；SCL high、SDA 上升代表STOP時序狀態。

![圖7.png](https://imageproxy.pixnet.cc/imgproxy?url=https://pic.pimg.tw/rexpighj123/1623635731-3563251958-g_n.png "圖7.png")

圖7. Start & Stop狀態

1. Ack & Nack

![圖8.png](https://imageproxy.pixnet.cc/imgproxy?url=https://pic.pimg.tw/rexpighj123/1623635731-934798963-g_n.png "圖8.png")

圖8. Ack & Nack狀態

每一個 8-bit(I2C是以1-byte為單位傳送data) 的資料傳輸結束後，會跟著一個 acknowledge bit(第9個bit)。這個 acknowledge bit 固定由接收方產生，有兩種用法：

1. 當 master 是傳送方(Transmitter)、slave 是接收方(Receiver)，也就是說這個傳輸是 master 寫入資料到 slave 時，這個 acknowledge bit 是用來讓 slave 告訴 master「收到！了解！正確！」
2. 當 master 是接收方、slave 是傳送方，也就是說這個傳輸是 master 從 slave 讀取資料時，這個 acknowledge bit 是用來讓 master 告訴 slave「我還要接著讀，請繼續準備下一筆資料」或者是「夠了，我讀完了」。

傳送方會在ACK的SCL時脈釋放SDA線(SDA為high)，如果接收方正常收到data的話，會在第9個bit將SDA拉low，也就是回應ACK。

如果接收方有任何狀況，或是 bus 上面根本就沒有那個 address 的 slave 裝置，到了第 9 個 SCL 週期時，當傳送方釋放SDA後，就沒有人去驅動 SDA，這時 SDA 就會因為上拉電阻(Rp)的關係維持在 high，如此一來，傳送方就知道出問題了，不會繼續接下來的傳輸，而要進行錯誤處理，這種情況稱之為「non-acknowledge」，或簡稱為「NACK」。

產生NACK的五大原因:

1. 在multiple data read傳輸中，當Master要告知Slave停止傳輸，則會在最後一個data byte收下後，改發NACK以告訴Slave裝置data讀取已結束。
2. 沒有裝置去回應ACK  (根本沒有接任何裝置或是發出的address不屬於bus上任一個裝置所有)。
3. 接收的裝置因為某種原因無暇進行指令的接收。
4. 傳輸過程中，接收裝置收到了他無法理解的資料。
5. 傳輸過程中，接收裝置的資料Buffer滿了，未處理前，再也收不下來。

(四) I2C的傳輸流程

1. Slave Address

![圖9.png](https://imageproxy.pixnet.cc/imgproxy?url=https://pic.pimg.tw/rexpighj123/1623635731-1207868773-g_n.png "圖9.png")

圖9. Slave Address示意圖

I2C 是一個多裝置的 bus，因此每當 master 發起傳輸時，它得先點名，就像老師叫特定座號的同學回答問題一樣，而這個座號就是Slave的 address。在最早的 I2C 規格中，I2C address 是 7-bit，同一個 bus 上不可以有兩個 address 一樣的 slave 裝置，因此 I2C bus 上最多可以有 128 個 slave 裝置，實務上有一些 address 是保留的不能使用，因此可用的數量會比 128 略少一點；至於 master，它沒有、也不需要address，因為沒有人會點名老師起來回答問題。因此所有的 I2C 傳輸週期，第一個 byte 都是用來點名的，它的內容就是被點到裝置的 address。

伴隨著 7 個 bit 的 slave address 而來的第 8 個 bit，則是一個表示讀或寫的 bit，0 是寫入、1 是讀取；其中點名的 byte 永遠是寫入，因此在slave address後的 R/W bit 的值一定是 0。

1. 寫入(Write)實例

I2C master 用 START 狀態發起傳輸後，接著是 slave address 以及 R/W bit，因爲這時是寫入 slave，因此 R/W bit 是 0，到了第 9 個 bit 時，傳輸方向會換過來，變成由 slave 向 master 傳送 acknowledge bit。

Master 收到 acknowledge 後，就會繼續切換 SCL，並在每一個 SCL 爲 high 的脈波週期中，依序送出資料的每一個 bit，總共 8 個 bit。

一樣到了第 9 個 bit 時，傳輸方向會換過來。Master 會在 SCL 變成 high 的第 9 個時脈週期中，放掉 SDA 不去驅動它(SDA為high)，並監聽來自 slave 的狀態；如果 slave 在此時有把 SDA 驅動到 low，就代表slave有正確地收到了這個 byte 的資料傳輸。

最後，master 送出 STOP 狀態結束這一回合的傳輸，成功寫入 1 個 byte 的資料到 slave。

![圖10.png](https://imageproxy.pixnet.cc/imgproxy?url=https://pic.pimg.tw/rexpighj123/1623635731-1905603317-g_n.png "圖10.png")

圖10. I2C master 對 slave 寫入一個 byte 資料的格式

在寫入週期中，只要 master 沒有送出 STOP 狀態，而是持續不斷地切換 SCL 並將資料送出，就會變成一個連續寫入data的傳輸。

至於可以連續寫入多少筆資料，則要看 slave 這邊晶片的設計，當寫入太多筆資料，超過 slave 可以允許的範圍，它就會發NACK喊停，告訴 master 不要再寫了。

![圖11.png](https://imageproxy.pixnet.cc/imgproxy?url=https://pic.pimg.tw/rexpighj123/1623635731-3339377239-g_n.png "圖11.png")

圖11. I2C master 對 slave連續寫入多筆資料的格式

1. 讀取(Read)實例

讀取和寫入流程類似，I2C master 用 START 狀態發起傳輸後，接著是填寫 slave address 以及 R/W bit，因爲這時是讀取 slave，所以 R/W bit 是 1，到了第 9 個 bit 時，傳輸方向會換過來，變成由 slave 向 master 傳送 acknowledge bit，之後就是slave向master傳送data，當master讀完後，會發ACK=0告訴slave收到data了。

![圖12.png](https://imageproxy.pixnet.cc/imgproxy?url=https://pic.pimg.tw/rexpighj123/1623635731-2683036054-g_n.png "圖12.png")

圖12. I2C master 對 slave 讀取一個 byte 資料的格式

在連續讀取時，只要後面還會繼續讀，master 就要送出 ACK=1 的 acknowledge bit 告訴 slave 要準備提供接下來的資料，只有當後面不再讀取而接著 STOP 狀態時，ACK 才會是 0。

![圖13.png](https://imageproxy.pixnet.cc/imgproxy?url=https://pic.pimg.tw/rexpighj123/1623635731-3917491802-g_n.png "圖13.png")

圖13. I2C master 對 slave 連續讀取多筆資料的格式

**(四) 時脈擴展(Clock Stretching)與仲裁協定(Arbitration)**

時脈擴展（clock stretching）這個功能，是設計用來讓動作比較慢的 slave 裝置在忙不過來時，通知 master「慢點、慢點」的方法。如果 slave 在接收資料的過程中，覺得它忙不過來，需要延長一點時間來喘口氣時，它就會驅動 SCL，把 SCL 拉到 low 的狀態。

master 在送出每一個 clock 時，都會同時監聽 SCL 的狀態，看看有沒有人拉住 SCL 將它保持在 low。此時 master 裝置的 SCL input buffer就扮演了很重要的角色(還記得那個三角形的同相器嗎?)。Master 在送出 SCL 上的 clock 時，並非自顧自地一直送，而是在每一個放開 SCL 的瞬間去聽聽看 SCL 是否有隨著 master 的放開而變成 high，還是有人拉住它請求 clock stretching。

在I2C spec中沒有規定clock stretching的時間上限，換句話說，你想拉住SCL多久就拉多久，這是因為I2C的clock速度在不同版本的spec中只有規定不同的上限(100 KHz、400 KHz、1 MHz、3.4 MHz 等)，並沒有最低速度的限制，所以SCL的速度可以無限制的慢。

由於長時間拉住SCL會造成I2C bus癱瘓(因為wired-AND特性)，所以後面有加入了time out機制，限制了最低的clock速度，以 PC 上常用的 SMBus 來說，它的基礎協定仍是 I2C，但限制了最低 clock 爲 10 KHz，而且整個 bus 上不能超過 3.5 ms 沒有任何動作。

![圖14.png](https://imageproxy.pixnet.cc/imgproxy?url=https://pic.pimg.tw/rexpighj123/1623635732-1917926108-g_n.png "圖14.png")

圖14. 典型的 clock stretching 時脈圖

時脈擴展（clock stretching）是slave透過控制SCL達成爭取時間的目的。而I2C的仲裁機制(Arbitration)是透過master控制SDA決定哪位master勝出。

由於I2C bus允許多個master裝置，所以當每個 master 在傳送資料時要如何才能不打架呢?

每個master除了照著 SCL 的節奏去驅動 SDA 外，同時也會逐個 bit 監聽 SDA 上的狀態。如果 SDA 上的狀態與它驅動 SDA 的狀態不符，抱歉，這個master就被判出局了。

Wired-AND 電路在這裡再度發威：「你的 low 一定是 low，但你的 high 卻不一定是 high」。當一個 master 把 SDA 拉 low 時，SDA 一定是 low；但當一個 master 把 SDA 放開變成 high 時，SDA 卻不一定是 high。如果有其它人將 SDA 驅動爲 low，那 SDA 就會是 low。

因此，「仲裁的輸贏總發生在一個 master 將 SDA 放掉的時候」。每當master放開 SDA時，它都會很緊張地監聽 SDA狀態，如果 SDA 仍然爲 high，那麼它就安然渡過這個 bit，可以繼續傳輸，參與仲裁；如果 SDA 被別人驅動成 low，那它就輸掉了這一回合的仲裁，接下來的時間它就必需關閉 SDA 的驅動電路，不能繼續參與仲裁。

![圖15.png](https://imageproxy.pixnet.cc/imgproxy?url=https://pic.pimg.tw/rexpighj123/1623635732-2618994491-g_n.png "圖15.png")

圖15. 仲裁的輸贏總發生在一個 master 將 SDA 放掉的時候

決定仲裁輸贏的情況有以下幾種：

1. 因爲 I2C 傳輸的第一個 byte 是接收裝置的 slave address，這種仲裁機制的結果就會由這個 slave address 決定。目標 slave address 越小的 master，在仲裁中就會有越高的優先權，其中送往 slave address 0x00 的 master 會有最高的優先權，因爲它把 7 個 bit 的 slave address 都拉到 low。
2. 如果真的這麼剛好，有兩個 master 同時要對同一個 slave 執行同樣的動作，那麼在第一個 byte 這個回合中就分不出勝負，仲裁會繼續進行到下一個 byte。
3. 如果這個動作是寫入，那麼就會由寫入資料比較小的那個 master 勝出。比方說兩個 master 都要對同一個 slave 寫資料，一個寫 0x80，一個寫 0x00，那麼實際上在 SDA 上出現的資料會是 0x00，而且寫 0x80 的那個 master 在寫第一個 bit 時就會知道自己搶輸了。
4. 如果這個動作是讀取，那麼接下來的 byte 就會是由 slave 送出來，於是就沒有仲裁的問題，兩個 master 也會收到一模一樣的資料。

**(五) 小結**

1. I2C的優缺點

2. 優點：電路簡單，方便當IC間溝通的橋樑
3. 缺點：速度慢，不適合長距離的傳輸、不同工作電壓的晶片連接問題等

4. I2C的應用

以顯示器的應用來說，常會在以下幾個地方看到I2C的應用：

1. EEPROM
2. DDC溝通(EDID、HDCP等)
3. DDCCI
4. 利用GPIO實現software I2C

5. I2C使用上的注意事項

6. 在電路設計上要考慮bus上的上拉電阻(Rp)和總寄生電容，決定最大可連接的裝置數。
7. 若發生I2C溝通異常，需使用I2C monitor或拉波形出來分析，首先要先檢查ACK bit是ACK還是NACK，並查閱晶片說明書，比對結果是否如預期。
8. 可以嘗試分析以下I2C波形圖當練習囉!