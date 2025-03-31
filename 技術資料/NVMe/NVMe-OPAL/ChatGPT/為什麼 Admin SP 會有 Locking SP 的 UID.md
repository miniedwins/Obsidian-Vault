
在 **Table 24 Admin SP - SP Table Preconfiguration** 中，  
Admin SP (UID: `00 00 02 05 00 00 00 01`) 與 Locking SP (UID: `00 00 02 05 00 00 00 02`) 都出現在這張表中。

在 **Table 25 Locking SP - SPInfo Table Preconfiguration** 中，  
SPID (Security Provider ID) 為 `00 00 02 05 00 00 00 02`，對應的是 **Locking SP**。

### 為什麼 Admin SP 會有 Locking SP 的 UID？

- **Admin SP 是最高管理層級的 SP (Security Provider)**，它負責管理所有其他 SP，包括 Locking SP。
- 在 Admin SP 的表格中，Locking SP 被列出來，代表 **Admin SP 具有對 Locking SP 的管理權限**。
- 這意味著，當我們透過 Admin SP 進行操作時，可以存取 Locking SP 的設定，例如修改 Locking SP 的權限或查詢其狀態。

這種關係可以視為 **階層式管理**：

- **Admin SP** 具有最高權限，能夠管理其他 SP，包括 Locking SP。
- **Locking SP** 主要負責與資料存取鎖定（Locking）相關的功能，例如加密、寫保護、讀取權限等。

如果你要存取 **Locking SP 的相關資訊**，通常可以透過 **Admin SP** 來操作，並使用 `GET` 指令來查詢 Locking SP 的設定。例如：

plaintext

複製編輯

`GET [UID = 00 00 02 05 00 00 00 02]  // 取得 Locking SP 相關設定`

這樣的設計確保 **Admin SP 可以控制 Locking SP 的行為**，但 Locking SP **本身不會影響 Admin SP**。