在 NVMe 規格中，若控制器支援 **SSFS（Save and Select Feature Support，儲存與選擇功能支援）**，主機（Host）可以透過 `Get Features` 指令，將其中的 **Select（SEL）** 欄位設定為 **011b**（即 **Supported Capabilities**）來查詢某個 Feature ID（FID）的支援屬性。

這個查詢能讓主機知道該功能是否可被修改、是否具備命名空間專屬性、以及其設定值是否能在斷電或重設後保存。

---

2. 當 Select 設定為 11b (Supported Capabilities) 時，Completion Queue Entry (CQE) Dword 0 的定義為何？

當主機下達 `Get Features` 且 `SEL = 011b` 時，控制器回傳之 **CQE Dword 0** 內含該功能的支援屬性，其位元（Bits）定義如下：

- **Bits 31:03**：保留（Reserved）。
- **Bit 02 - Changeable (CHANG，可變性)**：
    - **1b**：代表該 Feature 的值是**可被修改的**（主機可透過 `Set Features` 變更其目前值）。
    - **0b**：代表該 Feature 的值是**不可修改的**。
- **Bit 01 - NS Specific (NSSPEC，命名空間專屬性)**：
    - **1b**：代表該 Feature 具有 **Namespace Scope（命名空間範圍）**，必須針對特定命名空間單獨設定。
    - **0b**：代表該 Feature 的 Scope 屬於**非命名空間專屬**（如 Controller Scope、Domain Scope、或 NVM Subsystem Scope 等，定義於規格書的 Figure 403 中）。
- **Bit 00 - Saveable (SVBL，可保存性)**：
    - **1b**：代表該 Feature 的值是**可保存的**（主機在 `Set Features` 中設定 `Save (SV) = 1` 後，其值可在 Power Cycle 或 Reset 後維持）。
    - **0b**：代表該 Feature **不可保存**。


為什麼讀取 Enhanced Controller Metadata (7Dh) 的 Supported Capabilities 時，NS Specific (NSSPEC) 必須為 0？

規範指出：若對 **Enhanced Controller Metadata（FID = 7Dh）** 提交 `Get Features` 且 `SEL = 011b`，其回傳之 CQE Dword 0 中的 **NS Specific 位元必須被清除為** **0**。

**原因如下：**

1. **Scope 範圍屬性不同**：依據 NVMe 規格書的 Feature Scope 定義，FID `7Dh`（Enhanced Controller Metadata）以及 `7Eh`（Controller Metadata）的 Scope 皆屬於 **Controller Scope（控制器範圍）**。
2. **NSSPEC 欄位的本質**：如前所述，NSSPEC 位元為 `1` 代表該功能是「Namespace 專屬」。
3. **對照組 7Fh**：相較之下，**Namespace Metadata（FID = 7Fh）** 的 Scope 是 **Namespace Scope**，因此當讀取 `7Fh` 的 Supported Capabilities 時，NS Specific 位元就必須被**設定為** **1**。

因此，因為 `7Dh` 屬於控制器層級的詮釋資料，與單一 Namespace 無關，所以其 `NSSPEC` 位元必須為 `0`。