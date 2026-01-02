---
name: net-app-testing
description: 本技能專門用於 .NET 8.0 LTS 專案的全方位測試。涵蓋 Service 、Entity (Domain Object)、Dao (Data Access Object) 以及 Adapter (外部系統連結)。本規範強調真實互動與高品質的程式碼風格，確保測試既能驗證邏輯，又符合架構一致性。
---

# NET 8.0 應用層測試專家

## 簡介
本技能專門用於 .NET 8.0 LTS 專案的全方位測試。涵蓋 Service 、Entity (Domain Object)、Dao (Data Access Object) 以及 Adapter (外部系統連結)。本規範強調真實互動與高品質的程式碼風格，確保測試既能驗證邏輯，又符合架構一致性。

## 啟動時機 (Activation)
當使用者要求針對以下類型的類別撰寫單元測試或整合測試時：
- 「針對 [待測類別] 撰寫單元測試」
- 涉及目標為：`*Service`, `*Entity`, `*Dao`, `*Repository`, `*Adapter`, `*Client`。

## 分層測試準則 (Layer Guidelines)
針對不同層級，請遵循以下原則：
1. **Entity (Domain Object)**：測試狀態變更、驗證邏輯及領域行為。
2. **Service (Application Logic)**：測試業務流程串接與邏輯分支，確保正確調用內部組件。
3. **Dao (Data Access Object)**：**禁止使用 Mock**。必須連結實體資料庫，測試真實的 SQL 執行與資料取得。
4. **Adapter (Integration)**：測試與外部系統 (如第三方 API、外部 SDK) 的介接邏輯。

## 程式碼規範 (Coding Standards)
產出的測試程式碼必須嚴格遵守以下風格：

1. **命名規範**：
   - 測試類別：`[待測類別]Test`。
   - 測試方法：`Test[動名詞]` (例如：`TestDBConnIsOK`, `TestCalculateOrderTotal`, `TestAdapterCallSuccess`)。
2. **註解風格**：
   - 單行註解：使用 `//`。
   - 多行註解：必須使用 Java 註解風格 `/** ... */`。
3. **測試結構**：
   - 必須遵循 **3A Pattern** (Arrange, Act, Assert)。
4. **技術禁令**：
   - **不對 private 方法進行測試**。
   - **禁止使用 Reflection (反射)** 進行測試。
   - 在 Dao 測試中 **禁止使用 Mock** (其餘層級視需求由使用者指示)。

## 操作指令 (Instructions)
身為資深開發專家，請按以下步驟操作：
1. **環境確認**：確保專案使用 .NET 8.0 LTS 與 MSTest 框架。
2. **結構建立**：
   - 建立 `[待測類別]Test.cs` 檔案。
   - 在類別上方使用 `/** ... */` 標註測試目的。
3. **撰寫 3A 邏輯**：
   - **Arrange**: 準備環境、輸入參數或資料庫實體資料。
   - **Act**: 調用待測方法。
   - **Assert**: 使用 `Assert` 類別驗證結果。

## 範例 (Examples)
**使用者問：** 「幫我為 MemberService 寫測試，要包含資料庫 Dao 的調用。」
**Agent 應對：** - 建立 `MemberServiceTest` 類別。
- 寫入 Java 風格多行註解描述測試情境。
- 建立方法 `TestRegisterMemberSuccess`。
- 內部不使用 Mock，直接準備 Dao 所需的資料庫環境。
- 使用 `// Arrange`, `// Act`, `// Assert` 分隔代碼。

---
> 備註：此規範已整合使用者之核心提示詞與 ASP.NET Core 架構實務。
> 請將此檔案放置於：.github/skills/dotnet-full-stack-testing/SKILL.md