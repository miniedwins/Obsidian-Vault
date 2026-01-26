當我們要求 SSD 在 Sanitize 後 **保留 L2P 映射 (NDAS=1)**，若是 SSD 的 Identify 設定 **(NDI=1)** 時，就會發生衝突。

為了避免 SSD 不正常的命令造成的錯誤，NVMe 設計了一個參數 **NODRM** 來決定這時候該如何處理。

#### **1. 三個關鍵角色**

- **NDAS (我要求的)**：主機下指令說「Sanitize 後請保留映射」。
    
- **NDI (No-Deallocate Inhibited)**：SSD 舉手投降說「抱歉，我只要 Sanitize 就一定會清除映射」。
    
- **NODRM (No-Deallocate Response Mode)**：預先設定好的處理原則，告訴 SSD 當上述兩者衝突時該聽誰的。
    

#### **2. 衝突時的兩種結局 (當 NDAS=1 且 NDI=1)**

這時候 SSD 會去查看 **NODRM** 的設定值：

- **NODRM = 0 (Error Mode)**
    
    - **指令：** 「既然你做不到保留映射，那就**別做了**。」
        
    - **結果：** SSD 直接拒絕指令，回傳錯誤 (`Invalid Field in Command`)。什麼都沒清。
        
- **NODRM = 1 ( Warning Mode)**
    
    - **指令：** 「雖然你做不到保留映射，但**還是幫我清資料吧**，映射被刪掉就算了。」
        
    - **結果：** SSD 執行 Sanitize 並強制清除映射。
        
    - **紀錄：** 任務成功，但在 Log 中標記「發生意外的 Deallocate (`Sanitized Unexpected Deallocate`)」告知主機。











簡單來說：

- **控制器說 (NDI=1)：** 「我的硬體設計限制，**無法**支援『清除後保留映射』的功能（也就是我一定會 Deallocate）。」


- **主機說 (NDAS=1)：** 「我發送這個 Sanitize 指令，要求你**不要** Deallocate。」
    

這時就發生了衝突。為了不讓控制器當機或不知所措，NVMe 引入了 **NODRM (No-Deallocate Response Mode)** 這個參數（位於 Sanitize Config Command 的 Dword 11），讓主機在下指令時自己決定：「萬一你做不到我的要求，你該怎麼辦？」

以下為您拆解這段「矛盾處理機制」：

---

### **1. 角色介紹**

- **No-Deallocate Inhibited (NDI)**：這是控制器的**能力 (Capability)**。
    
    - `NDI = 1` 代表控制器舉手投降：「抱歉，我做不到 NDAS。只要我執行 Sanitize，我就一定會連帶執行 Deallocate。」
        
- **No-Deallocate After Sanitize (NDAS)**：這是主機下的**指令 (Command)**。
    
    - `NDAS = 1` 代表主機要求：「請幫我保留 LBA 映射，不要 Deallocate。」
        
- **No-Deallocate Response Mode (NODRM)**：這是主機給控制器的**錦囊 (Instruction)**。
    
    - 意思就是：「如果我要求 NDAS 但你做不到 (NDI=1)，請依照這個錦囊的指示行動。」
        

---

### **2. 矛盾處理的兩條路 (NODRM 的設定)**

當 **NDI = 1** (控制器做不到) **且** **NDAS = 1** (主機卻要求做) 時，控制器會檢查 **NODRM** 的值來決定命運：

#### **情況 A：NODRM = 0 (Error Response Mode - 嚴格模式)**

- **主機的意思：** 「如果你做不到 No-Deallocate，那就**別做了**，直接報錯拒絕我。」
    
- **控制器的行為：**
    
    - 直接中止 (Abort) 這條 Sanitize 指令。
        
    - 回傳狀態碼：**Invalid Field in Command**。
        
    - **結果：** 什麼事都沒發生，資料沒清，指令失敗。
        

#### **情況 B：NODRM = 1 (Warning Response Mode - 寬容模式)**

- **主機的意思：** 「如果你做不到 No-Deallocate，沒關係，**還是幫我執行 Sanitize 吧**。雖然你會強制 Deallocate，但我接受這個結果，只要事後通知我一聲就好。」
    
- **控制器的行為：**
    
    - **接受指令**，開始執行 Sanitize。
        
    - 因為硬體限制，Sanitize 完成後**強制執行 Deallocate**（違背了 NDAS=1 的要求）。
        
    - 在 `Sanitize Status Log` 中，將 `SOS` (Sanitize Operation Status) 欄位設定為 **100b (Sanitized Unexpected Deallocate)**。
        
    - **結果：** 資料清除了，LBA 映射也被刪了（Unexpected Deallocate），但任務算是成功完成。
        

---

### **3. 白話比喻**

想像你去餐廳點餐：

- **NDI=1 (控制器限制)：** 廚師說：「我們的炒飯**一定會加蔥**，鍋子都是混在一起的，沒辦法特製不加蔥。」
    
- **NDAS=1 (你的要求)：** 你點單說：「我要一份炒飯，**不要加蔥**。」
    

這時產生了矛盾。**NODRM** 就是你在點單時備註的處理方式：

- **NODRM = 0 (嚴格)：** 「如果你們不能做無蔥炒飯，那我就**不吃了**。」
    
    - **結果：** 退單 (Invalid Field in Command)。
        
- **NODRM = 1 (寬容)：** 「如果你們真的不能去蔥，那算了，**還是炒給我吃吧**，只是上菜時跟我說一聲。」
    
    - **結果：** 廚師端來一盤有蔥的炒飯，並附上一張紙條說「抱歉還是加了蔥」 (Sanitized Unexpected Deallocate)。

| **控制器能力 (NDI)**  | **主機要求 (NDAS)** | **處理模式 (NODRM)** | **結果行為**    | **回傳狀態 / Log**                             |
| ---------------- | --------------- | ---------------- | ----------- | ------------------------------------------ |
| **0** (支援 NDAS)  | **1** (要保留)     | (不重要)            | **成功保留映射**  | Successful Completion                      |
| **1** (不支援 NDAS) | **0** (要刪除)     | (不重要)            | **成功刪除映射**  | Successful Completion                      |
| **1 (矛盾發生!)**    | **1 (矛盾發生!)**   | **0 (嚴格)**       | **拒絕執行**    | **Invalid Field in Command**               |
| **1 (矛盾發生!)**    | **1 (矛盾發生!)**   | **1 (寬容)**       | **執行但強制刪除** | Log 顯示 **Sanitized Unexpected Deallocate** |
|                  |                 |                  |             |                                            |