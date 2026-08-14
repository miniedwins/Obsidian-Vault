**GDHM** 是主機在對 Host Metadata 功能（7Dh, 7Eh, 7Fh）發送 **Get Features** 時，填寫於 **Command Dword 11 中的 Bit 00** 的一個控制位元。

- **當** **GDHM = 1**：主機命令控制器**「生成預設的主機詮釋資料（Generate Default Host Metadata）」**。控制器會根據其內部韌體實作，自動生成一組 **Vendor-Specific（廠商專屬）的預設詮釋字串**（例如：預設的控制器名稱、驅動版本、處理器型號等描述），並將其填入該 Host Metadata 的 **Default（預設值，SEL = 001b）** 結構中供主機讀取。這組生成的預設值在執行 Controller Level Reset 後會恢復為 0。
- **當** **GDHM = 0**：控制器**不可**主動生成任何廠商專屬的預設字串，此時若主機讀取 Default 值，控制器僅會回傳既有的修改後預設值（如有）或空值。

B. 澄清迷思：Host 一定要先 Get Feature 讓 Controller 建立空間，才能 Add 或 Replace 嗎？

**答案是：完全不需要！**

主機**不需要（也沒必要）**在寫入資料前先下達 `Get Features (GDHM = 1)` 來逼控制器「建立」或「初始化」詮釋資料空間。主機可以直接下達 **Set Features** 指令，利用 **Element Action (EA)** 欄位直接進行詮釋資料的建立或修改：

1. **直接新增（EA = 00b / 10b）**：
    - 主機發送 `Set Features`，將 **Element Action（EA）** 設為 **00b****（Add or Replace Entry）**。
    - 如果控制器發現該指定的 `Element Type`（例如 OS Name）目前在資料結構中**不存在（does not exist）**，控制器會**自動在 Host Metadata 結構中建立（Create）**該 Descriptor，並將主機傳入的值寫入。
    - 在增強型（7Dh）中，如果 `EA = 10b`（Add Entry Multiple）且元素不存在，控制器同樣會直接建立它。
2. **直接替換**：
    - 如果該 `Element Type` 在結構中**已存在（exists）**，控制器在收到 `EA = 00b` 時，會自動用主機傳入的新值進行**替換（Replace）**。

**總結來說：** 主機可以直接發送 `Set Features` 進行新增、替換或刪除。**GDHM 僅用於主機想要讀取控制器內部「廠商預設生成的描述字串」之用****，與主機自身寫入/修改當前诠释資料的空間配置毫無因果關係。**