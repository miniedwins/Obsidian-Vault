# Python 資深開發核心規範 (Core Standards)

本規範旨在約束開發者的設計決策，確保程式碼具備高度的「解耦性」與「商業邏輯透明度」。

## 1. 型別設計原則 (Advanced Type Architecture)

- **介面解耦**：禁止濫用類別繼承。針對組件間的介面，優先使用 `typing.Protocol` 進行結構化標註 (Structural Typing)。
- **領域安全性**：關鍵 ID 或狀態應使用 `NewType` 或 `Literal` 封裝，防止基礎型別混淆。
- **不可變性優先**：資料容器 (DTO) 應優先使用 `@dataclass(frozen=True)`，確保資料流的可預測性。
- **嚴格性門檻**：不接受 `Any` 作為型別宣告。若遇複雜泛型，應定義 `TypeVar` 確保型別鏈結完整。

## 2. 彈性化錯誤處理 (Error & Resilience)

- **領域異常定義**：禁止在核心邏輯拋出通用型異常（如 `ValueError`, `Exception`）。必須定義具備商業語義的自定義錯誤類別。
- **異常鏈結規範**：轉換異常時，必須使用 `raise NewError(...) from e` 保留原始追蹤堆疊。
- **快錯原則 (Fail Fast)**：函式開頭應先進行「防禦性驗證」，確保後續邏輯在正確狀態下執行。

## 3. 資源與狀態管理 (State Management)

- **顯性生命週期**：涉及併發鎖、臨時檔案或狀態變更的操作，必須實作 Context Manager 以確保資源確定性釋放。
- **非同步安全**：在 Async 代碼中，應標記並謹慎處理阻塞型 IO，避免阻塞事件循環。

## 4. 文件化決策 (Decision Documentation)

- **意圖導向 (Google Style)**：Docstrings 必須描述「為什麼這樣設計」以及「呼叫者的責任限制」，禁止重複函式名稱的無意義描述。
- **複雜邏輯註解**：針對非直觀的演算法或優化（如位元運算、生成器管道），應標註其效能考量。

## 5. 日誌與可觀測性 (Logging & Observability)

- **輸出流管制**：在任何業務邏輯、API 或排程任務中，**嚴禁使用 `print()`** 語句。所有的狀態輸出必須透過標準的 `logging` 模組（如 `logger = logging.getLogger(__name__)`）執行。
- **禁止吞噬異常 (No Swallowing)**：在 `except` 區塊中紀錄錯誤後，若模組無力修復該狀態，**必須將異常重新拋出 (re-raise)**，嚴禁紀錄日誌後靜默返回 `None` 或預設值。
- **強制攜帶堆疊 (Stack Trace)**：在捕捉異常並記錄 Error 層級的日誌時，必須強制加上 `exc_info=True`（例如 `logger.error("Failed", exc_info=True)`），以確保錯誤追蹤鏈不中斷。
