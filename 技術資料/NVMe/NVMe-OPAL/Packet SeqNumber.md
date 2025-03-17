在 **TCG Opal** 通訊協議中，**SeqNumber**（序列號）用於識別 Host（主機）與 TPer（Trusted Peripheral，即自加密儲存裝置）之間的請求和回應，以確保通訊的同步性。

### **1. Host 發送請求**

當 **Host** 向 **TPer** 發送第一個請求時，會使用：

plaintext

複製編輯

`SeqNumber = 0x0000_0001`

這代表 **該請求的序列號是 1**。

---

### **2. TPer 回應 Host**

當 **TPer** 回應這個請求時，它會使用 **相同的 SeqNumber**：

plaintext

複製編輯

`SeqNumber = 0x0000_0001`

這確保了回應是針對該請求的。

---

### **3. Host 發送下一個請求**

當 **Host** 發送第二個請求時，SeqNumber 會遞增：

plaintext

複製編輯

`SeqNumber = 0x0000_0002`

這樣可以確保每次請求都有唯一的序列號。

---

### **4. TPer 對應的回應**

當 **TPer** 回應這個請求時，仍然會使用相同的 SeqNumber：

plaintext

複製編輯

`SeqNumber = 0x0000_0002`

---

### **5. 總結**

|**方向**|**SeqNumber 值**|
|---|---|
|Host → TPer（請求 1）|`0x0000_0001`|
|TPer → Host（回應 1）|`0x0000_0001`|
|Host → TPer（請求 2）|`0x0000_0002`|
|TPer → Host（回應 2）|`0x0000_0002`|
|Host → TPer（請求 3）|`0x0000_0003`|
|TPer → Host（回應 3）|`0x0000_0003`|

這種機制確保每個請求與回應都有匹配的序列號，防止訊息錯亂或重複處理。✅