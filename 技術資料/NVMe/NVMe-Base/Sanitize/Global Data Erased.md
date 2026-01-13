

If a namespace sanitize operation has been performed on every namespace that exists in the NVM subsystem and no user data has been written to any of those namespaces since each namespace sanitize operation completed successfully, then the Global Data Erased bit (refer to Figure 302) in the Sanitize Status log page for the sanitization target of the NVM subsystem shall not be set ‘1’ as a result of successfully completing those namespace sanitize operations

### 1. 核心邏輯：範圍（Scope）的差異

NVMe 的 Sanitize 指令分為兩種層級：

- **Subsystem-wide Sanitize (全子系統)：** 針對整顆硬碟，包含所有 Namespace、快取 (Cache)、以及**未分配的空間 (Unallocated space)**。
    
- **Namespace Sanitize (單一命名空間)：** 只針對特定的 Namespace。
    

這段規範的意思是：

> 「就算你把硬碟裡**每一個**現有的 Namespace 都各別跑了一次 Sanitize，這個 **Global Data Erased** 位元依然**不會**變為 `1`。」


### 2. 為什麼「全做完了」卻不能設為 1？

這涉及到資安上的「最高標準」。Global Data Erased (GDE) 位元一旦設為 `1`，代表的是**整顆實體硬碟（Subsystem）**從頭到腳都是乾淨的。

**個別執行 Namespace Sanitize 無法達到「Global」等級的原因：**

1. **快取資料 (Cache)：** 個別 Namespace 清理可能不會強制清空全域的控制器快取。
    
2. **未分配空間 (Unallocated Space)：** 硬碟裡可能存在尚未分配給任何 Namespace 的空間（例如 Over-provisioning 預留空間）。Namespace Sanitize 碰不到這些地方，但這些地方可能殘留舊資料。
    
3. **共享資源：** NVM Subsystem 可能包含多個 Namespace 共享的元數據 (Metadata) 或內部緩衝區。

### 3. 這個規範對你有什麼影響？

如果你是開發者或資安稽核員：

- **檢查狀態時：** 如果你的目的是確認「整顆硬碟都乾淨了」，你必須檢查 Sanitize Status Log 的 **GDE 位元**。但要讓這個位元變成 `1`，你必須發送 **NVM Subsystem 層級** 的 Sanitize 指令。
    
- **個別操作無效：** 你不能透過循環執行 `Sanitize Namespace 1`, `Sanitize Namespace 2`... 來獲得 GDE 認證。