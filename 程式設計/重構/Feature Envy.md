### 更深入的解釋 (A Deeper Explanation)

Feature Envy 的核心問題，違反了物件導向設計中一個非常重要的原則：**「資料和操作資料的行為應該被封裝在一起。」**

我們可以從幾個角度來思考，為什麼這是一個「壞味道」：

1. **責任錯置 (Misplaced Responsibility):** 一個類別 (Class) 的主要職責，應該是管理好自己的狀態 (Data) 並提供與該狀態相關的行為 (Methods)。如果 A 類的方法花大量的時間去操作 B 類的資料，那這個方法實際上是在「越俎代庖」，承擔了本應屬於 B 類的責任。這會讓程式碼的職責劃分變得模糊不清。
    
2. **破壞封裝 (Broken Encapsulation):** B 類之所以將資料設為私有 (private) 或提供 getter/setter，是希望保護其內部結構，並保留未來修改的彈性。但如果 A 類的方法不斷地透過 getter 去取得 B 類的多個資料欄位來進行複雜計算，那 A 類就等於是「看穿」了 B 類的內部實作。一旦 B 類想改變這些資料的儲存方式或結構，所有窺探它的 A 類方法都必須跟著修改，這就是你提到的「緊密耦合」。
    
3. **高耦合，低內聚 (High Coupling, Low Cohesion):**
    
    - **高耦合 (High Coupling):** A 類和 B 類因為這個「羨慕」的函式而緊緊地綁在一起。A 依賴 B 的內部細節，B 的改動會影響 A。系統變得脆弱、難以維護。
        
    - **低內聚 (Low Cohesion):** 內聚指的是一個模組（例如一個 Class）內部各個元素之間關聯的緊密程度。當 A 類的方法處理的邏輯其實跟 A 沒什麼關係，而是跟 B 比較相關時，A 類的「純度」和「專一性」就降低了，這就是低內聚的表現。
        

### 一個經典的範例 (A Classic Example)

想像一個電商系統，我們有 `Order` (訂單) 和 `Customer` (顧客) 兩個類別。

`Customer` 類別可能長這樣：

Python

```python
class Customer:
    def __init__(self, name: str, is_vip: bool, loyalty_points: int):
        self._name = name
        self._is_vip = is_vip
        self._loyalty_points = loyalty_points

    def is_vip(self) -> bool:
        return self._is_vip

    def get_loyalty_points(self) -> int:
        return self._loyalty_points
```

`Order` 類別負責計算訂單總價：

Python

```python
class Order:
    def __init__(self, customer: Customer, base_price: float):
        self._customer = customer
        self._base_price = base_price

    # ... 其他訂單相關方法 ...
```

---

#### 重構前：有 Feature Envy 的壞味道 🤢

現在，我們要在 `Order` 類中增加一個計算折扣後價格的方法 `get_final_price`。這個折扣規則跟顧客的身份有密切關係。

Python

```python
class Order:
    def __init__(self, customer: Customer, base_price: float):
        self._customer = customer
        self._base_price = base_price

    def get_final_price(self) -> float:
        """
        這個方法對 Customer 的特徵（Feature）充滿了羨慕（Envy）。
        它不斷地向 customer 物件索取資料來進行運算。
        """
        discount = 0.0
        # 羨慕1：對 is_vip() 的興趣
        if self._customer.is_vip():
            discount += 0.1 # VIP 享有 10% 折扣

        # 羨慕2：對 get_loyalty_points() 的興趣
        if self._customer.get_loyalty_points() > 100:
            discount += 0.05 # 忠誠點數超過 100 再折 5%

        # ... 未來可能還有更多基於顧客屬性的複雜折扣規則 ...

        final_price = self._base_price * (1 - discount)
        return final_price

# --- 使用範例 ---
vip_customer = Customer(name="John Doe", is_vip=True, loyalty_points=150)
order = Order(customer=vip_customer, base_price=1000.0)

print(f"Final price: {order.get_final_price()}") # 輸出: Final price: 850.0
```

**問題分析：** `Order.get_final_price()` 這個方法，它關心 `_base_price` 這個「自家事」嗎？只關心一點點。它大部分的邏輯都在圍繞著 `customer` 物件打轉，不斷地問：「你是 VIP 嗎？」、「你點數多少？」。

這就是標準的 Feature Envy。如果未來公司的折扣策略改變（例如增加不同等級的 VIP、或是根據顧客的註冊時長打折），我們修改的竟然是 `Order` 這個類別！這完全不合邏輯，因為折扣策略是跟「顧客」有關的，而不是「訂單」。

---

#### 重構後：移除 Feature Envy 的好味道 😊

解決方案就是 Martin Fowler 說的：**Move Method**。將這個方法移動到它真正依戀的那個類別身上。

**第 1 步：** 將計算折扣的邏輯搬到 `Customer` 類別。

Python

```python
class Customer:
    def __init__(self, name: str, is_vip: bool, loyalty_points: int):
        self._name = name
        self._is_vip = is_vip
        self._loyalty_points = loyalty_points

    def is_vip(self) -> bool:
        return self._is_vip

    def get_loyalty_points(self) -> int:
        return self._loyalty_points

    # 新增的方法：將計算邏輯移入
    def calculate_discount_rate(self) -> float:
        """
        這個方法現在名正言順地使用自己的資料。
        這就是高內聚！
        """
        discount = 0.0
        if self.is_vip():
            discount += 0.1

        if self.get_loyalty_points() > 100:
            discount += 0.05

        return discount
```

**第 2 步：** 讓 `Order` 類別去「請求」`Customer` 計算折扣，而不是自己動手。這符合 **"Tell, Don't Ask"** 原則：不要去問物件的內部狀態來自己做決定，而是告訴物件去做某件事。

Python

```python
class Order:
    def __init__(self, customer: Customer, base_price: float):
        self._customer = customer
        self._base_price = base_price

    def get_final_price(self) -> float:
        """
        現在這個方法職責非常清晰：
        1. 取得顧客的折扣率
        2. 計算最終價格
        它不再窺探 Customer 的內部細節。
        """
        discount_rate = self._customer.calculate_discount_rate() # 告訴 customer 計算折扣
        final_price = self._base_price * (1 - discount_rate)
        return final_price

# --- 使用範例 ---
vip_customer = Customer(name="John Doe", is_vip=True, loyalty_points=150)
order = Order(customer=vip_customer, base_price=1000.0)

print(f"Final price: {order.get_final_price()}") # 輸出: Final price: 850.0
```

**重構後的好處：**

1. **職責清晰：** `Customer` 負責所有跟顧客自身屬性相關的商業邏輯（例如折扣計算）。`Order` 則專注於訂單本身的計算。
    
2. **低耦合：** `Order` 不再依賴 `Customer` 的內部實現。未來 `Customer` 的折扣規則怎麼改，哪怕是增加 10 種新的會員等級，`Order` 的 `get_final_price` 方法都不需要修改任何一行程式碼。
    
3. **高內聚：** `Customer` 類別的功能變得更完整、更專一了。
    
4. **易於維護和擴充：** 當PM說要修改折扣規則時，工程師能立刻定位到 `Customer.calculate_discount_rate()` 這個方法，而不需要在整個系統裡到處尋找哪裡有用到顧客資料。
    

---

### 問題一：處理 VIP 過期問題

VIP 身份不是永久的，它有時效性。這表示 `is_vip` 不應該只是一個簡單的布林值 (`True`/`False`)，它應該是根據「當下時間」動態計算出來的結果。

**設計思路：**

1. **增加屬性：** `Customer` 類別需要一個 `vip_expiry_date` (VIP 到期日) 屬性。
    
2. **修改行為：** 原本的 `is_vip()` 方法要變得更聰明。它不應該存在，取而代之的是一個 `is_active_vip(check_date)` 方法，用來判斷在 `check_date` 那天，VIP 身份是否有效。
    
3. **上下文的重要性：** 判斷 VIP 是否有效，需要一個「時間點」作為參考。這個時間點通常就是訂單成立的日期。所以 `Order` 類別也應該記錄自己的 `order_date`。
    

**修改後的程式碼：**

我們需要 `datetime` 模組來處理日期。

Python

```python
from datetime import date, timedelta
from typing import Optional

class Customer:
    def __init__(self, name: str, loyalty_points: int, vip_expiry_date: Optional[date] = None):
        self._name = name
        self._loyalty_points = loyalty_points
        self._vip_expiry_date = vip_expiry_date # 新增 VIP 到期日屬性

    def get_loyalty_points(self) -> int:
        return self._loyalty_points

    def is_active_vip(self, check_date: date) -> bool:
        """
        在指定的日期 (check_date) 判斷 VIP 是否有效。
        """
        if self._vip_expiry_date is None:
            return False
        return self._vip_expiry_date >= check_date

    def calculate_discount_rate(self, check_date: date) -> float:
        """
        計算折扣率時，也需要傳入日期來判斷 VIP 資格。
        """
        discount = 0.0
        # 根據傳入的日期來判斷 VIP 資格
        if self.is_active_vip(check_date):
            discount += 0.1

        if self.get_loyalty_points() > 100:
            discount += 0.05

        return discount

# Order 類別也要跟著調整
class Order:
    def __init__(self, customer: Customer, base_price: float, order_date: date):
        self._customer = customer
        self._base_price = base_price
        self._order_date = order_date # 訂單建立時就記錄日期

    def get_final_price(self) -> float:
        # 將訂單日期傳遞給 customer，讓他自己判斷當時的折扣
        discount_rate = self._customer.calculate_discount_rate(self._order_date)
        final_price = self._base_price * (1 - discount_rate)
        return final_price

# --- 使用範例 ---
today = date.today()
yesterday = today - timedelta(days=1)
tomorrow = today + timedelta(days=1)

# a_customer 的 VIP 明天才到期
a_customer = Customer(name="Alice", loyalty_points=150, vip_expiry_date=tomorrow)
# b_customer 的 VIP 昨天就過期了
b_customer = Customer(name="Bob", loyalty_points=150, vip_expiry_date=yesterday)

# 兩筆訂單都是今天成立
order_a = Order(customer=a_customer, base_price=1000.0, order_date=today)
order_b = Order(customer=b_customer, base_price=1000.0, order_date=today)

# Alice 的訂單有 VIP 折扣 + 忠誠點數折扣 (0.1 + 0.05)
print(f"Alice's final price: {order_a.get_final_price()}") # 預期 850.0

# Bob 的訂單 VIP 已過期，只剩下忠誠點數折扣 (0.05)
print(f"Bob's final price: {order_b.get_final_price()}") # 預期 950.0
```

**重點分析：**

- 我們把「如何判斷 VIP 是否有效」這個複雜的邏輯，完美地**封裝**在 `Customer` 類別內部。
    
- `Order` 類別完全不需要知道 VIP 是怎麼判斷的，它只需要提供「訂單日期」這個上下文資訊，然後信任地告訴 `Customer`：「請根據這天，算出你該有的折扣」。
    
- 這種設計**耦合度極低**，未來就算 VIP 規則變得更複雜（例如：VIP 還有分金卡、白金卡等級），`Order` 類別依然不需要任何改動。
    

---

### 問題二：處理季節性折扣問題

季節性折扣（例如：雙十一、聖誕節特價）是一個**全域性**或**外部**的規則，它不專屬於某個顧客，也不專屬於某張訂單。它跟「時間」這個外部因素有關。

**設計思路：**

1. **職責分離 (Separation of Concerns):** 顧客折扣歸顧客管，季節性折扣則應該由一個獨立的「折扣規則引擎」或「服務」來管理。我們不應該把季節性折扣的邏輯寫死在 `Customer` 或 `Order` 類別裡。
    
2. **Order 的角色：** `Order` 在計算最終價格時，是總指揮。它應該去詢問所有可能的折扣來源（顧客自身的折扣、季節性折扣...等），然後把它們組合起來。
    

**修改後的程式碼：**

首先，我們建立一個獨立的函式（在大型專案中，這可能是一個類別 `PricingService`）來處理季節性折扣。

Python

```python
# 這是一個獨立的服務或規則引擎，與 Customer 和 Order 無關
def get_seasonal_discount_rate(check_date: date) -> float:
    """
    根據日期回傳季節性折扣。
    這部分的邏輯可以非常複雜，但都跟核心物件無關。
    """
    # 假設 12 月是聖誕節特價月，額外 8% 折扣
    if check_date.month == 12:
        return 0.08
    # 假設 11 月 11 日是雙十一，當天額外 15% 折扣
    if check_date.month == 11 and check_date.day == 11:
        return 0.15
    return 0.0
```

然後，我們讓 `Order` 在計算總價時，也把這個因素考慮進去。

Python

```python
class Order:
    def __init__(self, customer: Customer, base_price: float, order_date: date):
        self._customer = customer
        self._base_price = base_price
        self._order_date = order_date

    def get_final_price(self) -> float:
        # 1. 取得顧客自身的折扣率
        customer_discount = self._customer.calculate_discount_rate(self._order_date)

        # 2. 取得當天的季節性折扣率
        seasonal_discount = get_seasonal_discount_rate(self._order_date)

        # 3. 組合所有折扣 (這裡用簡單的相加，真實世界可能更複雜)
        total_discount = min(customer_discount + seasonal_discount, 0.9) # 假設最高 9 折

        final_price = self._base_price * (1 - total_discount)
        return final_price

# --- 使用範例 ---
christmas_day = date(2025, 12, 24)
normal_day = date(2025, 10, 10)

# Alice 是 VIP，忠誠點數也夠
alice = Customer(name="Alice", loyalty_points=150, vip_expiry_date=date(2026, 1, 1))

# 在聖誕節下單
order_christmas = Order(customer=alice, base_price=1000.0, order_date=christmas_day)
# 在平常日子下單
order_normal = Order(customer=alice, base_price=1000.0, order_date=normal_day)

# 聖誕節訂單 = (VIP 10% + 點數 5%) + 季節性 8% = 23% 折扣
print(f"Alice's Christmas order price: {order_christmas.get_final_price()}") # 預期 770.0

# 平常訂單 = VIP 10% + 點數 5% = 15% 折扣
print(f"Alice's normal day order price: {order_normal.get_final_price()}") # 預期 850.0
```

**重點分析：**

- 我們完全沒有修改 `Customer` 類別，就成功加入了季節性折扣的功能。這證明了我們的設計是**有彈性**、**可擴充**的。
    
- 季節性折扣的複雜邏輯被**封裝**在 `get_seasonal_discount_rate` 函式中，與核心業務物件 (`Customer`, `Order`) 完全解耦。
    
- `Order` 類別扮演了**協調者 (Coordinator)** 的角色，它負責整合不同來源的折扣，計算出最終價格。這非常符合它作為「訂單」的職責。
    

### 總結

透過解決這兩個更進階的問題，我們再次印證了良好物件導向設計的威力：

1. **單一職責原則 (Single Responsibility Principle):** `Customer` 管好顧客的事，`Order` 管好訂單的事，季節性折扣規則由獨立的模組管理。各司其職，程式碼就不會混亂。
    
2. **封裝 (Encapsulation):** 每個類別都隱藏了自己內部的複雜邏輯。`Order` 不用管 VIP 怎麼判斷，`Customer` 也不用管聖誕節是什麼時候。
    
3. **低耦合 (Low Coupling):** 因為職責分明且封裝良好，修改一部分功能（例如增加新的季節性活動）不會影響到其他不相關的部分，讓系統維護起來輕鬆很多。