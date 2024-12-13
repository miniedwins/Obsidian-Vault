## 概要說明

主機用於對 NVM 媒體進行低階格式化操作，主要用來更改以下屬性：

- **LBA ( 邏輯區塊地址 ) 資料大小**
- **Metadata ( 元數據 ) 大小**
- **Protection Information ( 端對端資料保護 )**
## 功能說明

1. 執行低階格式化可選擇銷毀所有的 User Data ( 使用者資料 ) 以及 Metadata ( 元數據 )。
2. 格式化完成後，受影響的命名空間將**不返回任何之前儲存的用戶資料**。
3. 可以指定格式化所有命名空間或僅特定命名空間。
4. 開啟端對端資料保護功能。
## 安全擦除 (Secure Erase)

格式化時可以選擇進行安全擦除 **( Secure Erase Settings ) SES**，清除 NVM 內的內容。
SES 設定分為三個類型，其中有兩種類型可以將所有資料清除，如下 : 

1. **沒有安全擦除 ( No secure erase )** : 
	- 協議規範未要求清除所有資料。
	- 僅格式化命名空間相關屬性。
2. **用戶數據擦除 (User Data Erase)**：
	- 清除所有使用者資料 ( 例如 : 所有使用者的資料填成 "1" 或是 "0" )。
	- 若是用戶資料已經是被加密過，控制器會使用 `Cryptographic Erase` 方式來執行。
3.  **加密擦除 (Cryptographic Erase)**：
	- 刪除加密用的密鑰，從而清除所有用戶資料。
	- 速度快並且不需要更動當前所有內容，密鑰已經被刪除因此無法回復原始數據。

![[Pasted image 20241213141643.png]]
## 操作範圍 (Operation Scope)

低階格式化會**影響所有命名空間或是特定命名空間**，控制器會根據 `Namespace  Identify Ctrl` 欄位中的 **Format NVM Attributes ( FNA )** 欄位決定操作範圍。

![[Pasted image 20241213142445.png]]

FNA 範圍設定說明 : 
- 主要區分是否支援所有的命名空間或是特定命名空間，取決於此欄位的配置和命令參數。
- 控制器有沒有支援加密刪除 **( Cryptographic Erase )** 功能。
- 若是位元 Bit 3 設為 `1`，位元 Bit 0 需設為 `0`。

![[Pasted image 20241213142801.png]]

最後格式化會根據 `Format NVM Operation Scope` 表格以及 `FNA` 欄位決定影響命名空間的範圍。

![[Pasted image 20241213143554.png]]