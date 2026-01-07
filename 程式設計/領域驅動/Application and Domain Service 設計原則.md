## 這個例子是什麼?

```java
// 這是 Application Service!
public class CreateOrderService {  // 建議改名: OrderApplicationService
    private final OrderRepository orderRepository;
    private final OrderFactory orderFactory;
    private final OrderValidationService validationService;  // 這才是 Domain Service
    
    @Transactional
    public OrderDto execute(CreateOrderCommand command) {
        Order order = orderFactory.create(command);
        validationService.validate(order);  // 調用 Domain Service
        orderRepository.save(order);
        return OrderDto.from(order);  // 返回 DTO 給外層
    }
}
```

## 如何區分 Domain Service vs Application Service?

### 關鍵判斷標準

|判斷維度|Domain Service|Application Service|
|---|---|---|
|**所在層次**|領域層 (Domain Layer)|應用層 (Application Layer)|
|**職責**|**業務邏輯**,跨聚合的領域規則|**流程編排**,協調領域對象|
|**依賴**|不依賴外部技術(Repository, DTO)|依賴 Repository, 返回 DTO|
|**事務**|不管事務|管理事務邊界 (@Transactional)|
|**返回值**|領域對象|DTO (數據傳輸對象)|
|**可復用性**|可被多個 Application Service 調用|直接被外層(Controller)調用|
|**測試**|純單元測試|需要集成測試|

### 具體特徵對比

```java
// ===== Domain Service =====
// 特徵:純粹的領域邏輯,不依賴基礎設施

public class OrderValidationService {  // Domain Service
    // ✅ 沒有 @Transactional
    // ✅ 不依賴 Repository
    // ✅ 不返回 DTO
    // ✅ 純粹的業務規則
    
    public void validate(Order order, Customer customer) {
        // 業務規則:VIP 客戶可以下大額訂單
        if (!customer.isVIP() && order.getTotalAmount().isGreaterThan(Money.of(10000))) {
            throw new OrderAmountExceedsLimitException();
        }
        
        // 業務規則:週末不能配送生鮮商品
        if (isWeekend() && order.containsFreshProducts()) {
            throw new FreshProductsNotAvailableOnWeekendException();
        }
        
        // 業務規則:新用戶首單限制
        if (customer.isNewCustomer() && order.getOrderLines().size() > 5) {
            throw new FirstOrderItemLimitException();
        }
    }
}

public class OrderPricingService {  // Domain Service
    private final TaxCalculator taxCalculator;  // 可以依賴其他 Domain Service
    private final DiscountCalculator discountCalculator;
    
    // ✅ 純粹的計算邏輯
    // ✅ 返回領域對象(Money)
    
    public Money calculateFinalPrice(Order order, Customer customer, List<Promotion> promotions) {
        Money subtotal = order.getSubtotal();
        
        // 會員折扣計算
        Money memberDiscount = discountCalculator.calculateMemberDiscount(customer, subtotal);
        
        // 促銷折扣計算
        Money promotionDiscount = discountCalculator.calculatePromotionDiscount(order, promotions);
        
        // 稅金計算
        Money tax = taxCalculator.calculate(subtotal.subtract(memberDiscount).subtract(promotionDiscount));
        
        return subtotal.subtract(memberDiscount).subtract(promotionDiscount).add(tax);
    }
}

// ===== Application Service =====
// 特徵:協調者,管理事務和流程

public class OrderApplicationService {  // Application Service
    // ✅ 有 @Transactional
    // ✅ 依賴 Repository
    // ✅ 返回 DTO
    // ✅ 調用 Domain Service
    
    private final OrderRepository orderRepository;
    private final CustomerRepository customerRepository;
    private final OrderValidationService validationService;  // Domain Service
    private final OrderPricingService pricingService;        // Domain Service
    
    @Transactional  // 管理事務邊界
    public OrderDto createOrder(CreateOrderCommand command) {
        // 1. 載入聚合
        Customer customer = customerRepository.findById(command.getCustomerId());
        
        // 2. 創建領域對象
        Order order = Order.create(command.getCustomerId(), command.getItems());
        
        // 3. 調用 Domain Service 執行業務邏輯
        validationService.validate(order, customer);
        
        // 4. 保存
        orderRepository.save(order);
        
        // 5. 返回 DTO
        return OrderDto.from(order);
    }
    
    @Transactional
    public OrderDto confirmOrder(ConfirmOrderCommand command) {
        // 1. 載入
        Order order = orderRepository.findById(command.getOrderId());
        Customer customer = customerRepository.findById(order.getCustomerId());
        List<Promotion> promotions = promotionRepository.findActive();
        
        // 2. 調用 Domain Service 計算價格
        Money finalPrice = pricingService.calculateFinalPrice(order, customer, promotions);
        order.setFinalPrice(finalPrice);
        
        // 3. 確認訂單
        order.confirm();
        
        // 4. 保存
        orderRepository.save(order);
        
        // 5. 返回 DTO
        return OrderDto.from(order);
    }
}
```

## 設計指南

### Domain Service 設計原則

```java
// ✅ Domain Service 的正確設計

public class TransferService {  // Domain Service
    
    // 1. 純粹的領域邏輯,沒有基礎設施依賴
    public TransferResult transfer(Account fromAccount, Account toAccount, Money amount) {
        // 業務規則驗證
        if (fromAccount.getCurrency() != toAccount.getCurrency()) {
            throw new CurrencyMismatchException();
        }
        
        if (amount.isGreaterThan(fromAccount.getDailyTransferLimit())) {
            throw new DailyLimitExceededException();
        }
        
        // 執行業務邏輯
        fromAccount.debit(amount);
        toAccount.credit(amount);
        
        // 返回領域對象
        return new TransferResult(fromAccount, toAccount, amount);
    }
    
    // 2. 可以依賴其他 Domain Service
    public boolean canTransfer(Account fromAccount, Account toAccount, Money amount) {
        // 檢查邏輯
        return fromAccount.getBalance().isGreaterThanOrEqual(amount)
            && fromAccount.getCurrency() == toAccount.getCurrency()
            && amount.isLessThanOrEqual(fromAccount.getDailyTransferLimit());
    }
}

// 命名建議:
// - XxxService: 動作型,如 TransferService, PricingService
// - XxxCalculator: 計算型,如 TaxCalculator, DiscountCalculator
// - XxxValidator: 驗證型,如 OrderValidator, PaymentValidator
// - XxxPolicy: 策略型,如 RefundPolicy, ShippingPolicy
```

### Application Service 設計原則

```java
// ✅ Application Service 的正確設計

@Service
public class OrderApplicationService {
    private final OrderRepository orderRepository;
    private final CustomerRepository customerRepository;
    private final InventoryRepository inventoryRepository;
    
    // Domain Services
    private final OrderValidationService orderValidationService;
    private final OrderPricingService orderPricingService;
    
    // Infrastructure Services
    private final EmailService emailService;
    private final PaymentGateway paymentGateway;
    
    // 1. 管理事務邊界
    @Transactional
    public OrderDto placeOrder(PlaceOrderCommand command) {
        // 2. 載入聚合根
        Customer customer = customerRepository.findById(command.getCustomerId());
        
        // 3. 創建新聚合
        Order order = Order.create(command.getCustomerId(), command.getItems());
        
        // 4. 調用 Domain Service 執行業務邏輯
        orderValidationService.validate(order, customer);
        Money finalPrice = orderPricingService.calculateFinalPrice(order, customer);
        order.setFinalPrice(finalPrice);
        
        // 5. 持久化
        orderRepository.save(order);
        
        // 6. 調用基礎設施服務(副作用)
        emailService.sendOrderConfirmation(order.getId());
        
        // 7. 返回 DTO(不返回領域對象)
        return OrderDto.from(order);
    }
    
    @Transactional
    public void cancelOrder(CancelOrderCommand command) {
        Order order = orderRepository.findById(command.getOrderId());
        
        // 業務邏輯委託給聚合根
        order.cancel(command.getReason());
        
        orderRepository.save(order);
        
        // Repository 自動發布領域事件
    }
}

// 命名建議:
// - XxxApplicationService
// - 或簡化為 XxxService(如果項目中不會混淆)
```

## 層次結構完整示例

```java
// ===== 展現層 (Presentation Layer) =====

@RestController
@RequestMapping("/orders")
public class OrderController {
    private final OrderApplicationService orderApplicationService;
    
    @PostMapping
    public ResponseEntity<OrderDto> createOrder(@RequestBody CreateOrderRequest request) {
        CreateOrderCommand command = CreateOrderCommand.from(request);
        OrderDto order = orderApplicationService.createOrder(command);
        return ResponseEntity.ok(order);
    }
}

// ===== 應用層 (Application Layer) =====

@Service
public class OrderApplicationService {  // Application Service
    private final OrderRepository orderRepository;
    private final CustomerRepository customerRepository;
    private final OrderValidationService validationService;  // Domain Service
    
    @Transactional  // 事務管理
    public OrderDto createOrder(CreateOrderCommand command) {
        // 編排流程
        Customer customer = customerRepository.findById(command.getCustomerId());
        Order order = Order.create(command.getCustomerId(), command.getItems());
        
        validationService.validate(order, customer);  // 調用 Domain Service
        
        orderRepository.save(order);
        
        return OrderDto.from(order);  // 轉換為 DTO
    }
}

// ===== 領域層 (Domain Layer) =====

// Domain Service: 跨聚合的業務邏輯
public class OrderValidationService {
    // 純粹的業務規則
    public void validate(Order order, Customer customer) {
        if (!customer.isVIP() && order.getTotalAmount().isGreaterThan(Money.of(10000))) {
            throw new OrderAmountExceedsLimitException();
        }
    }
}

// 聚合根: 聚合內的業務邏輯
public class Order {
    public void confirm() {
        validateCanConfirm();
        this.status = OrderStatus.CONFIRMED;
        registerEvent(new OrderConfirmedEvent(this.id));
    }
}

// ===== 基礎設施層 (Infrastructure Layer) =====

@Repository
public class OrderRepositoryImpl implements OrderRepository {
    // 持久化實現
}
```

## 實際案例對比

### 案例:訂單折扣計算

````java
// ❌ 錯誤:把業務邏輯放在 Application Service

@Service
public class OrderApplicationService {
    @Transactional
    public OrderDto applyDiscount(ApplyDiscountCommand command) {
        Order order = orderRepository.findById(command.getOrderId());
        Customer customer = customerRepository.findById(order.getCustomerId());
        
        // ❌ 業務邏輯不該在這裡!
        Money discount = Money.ZERO;
        if (customer.isVIP()) {
            discount = order.getSubtotal().multiply(0.1);
        }
        if (customer.getBirthMonth() == LocalDate.now().getMonthValue()) {
            discount = discount.add(order.getSubtotal().multiply(0.05));
        }
        
        order.applyDiscount(discount);
        orderRepository.save(order);
        return OrderDto.from(order);
    }
}

// ✅ 正確:業務邏輯抽取到 Domain Service

public class DiscountCalculator {  // Domain Service
    public Money calculateDiscount(Order order, Customer customer) {
        Money discount = Money.ZERO;
        
        // VIP 折扣
        if (customer.isVIP()) {
            discount = discount.add(order.getSubtotal().multiply(0.1));
        }
        
        // 生日折扣
        if (customer.isBirthdayMonth()) {
            discount = discount.add(order.getSubtotal().multiply(0.05));
        }
        
        return discount;
    }
}

@Service
public class OrderApplicationService {  // Application Service
    private final DiscountCalculator discountCalculator;
    
    @Transactional
    public OrderDto applyDiscount(ApplyDiscountCommand command) {
        Order order = orderRepository.findById(command.getOrderId());
        Customer customer = customerRepository.findById(order.getCustomerId());
        
        // 調用 Domain Service 計算
        Money discount = discountCalculator.calculateDiscount(order, customer);
        
        order.applyDiscount(discount);
        orderRepository.save(order);
        return OrderDto.from(order);
    }
}
```

## 決策樹:該放在哪一層?
```
這段邏輯是什麼?
│
├─ 是編排流程(載入、保存、協調)? 
│  └─ YES → Application Service
│
├─ 是跨聚合的業務規則?
│  └─ YES → Domain Service
│
├─ 是單一聚合內的業務規則?
│  └─ YES → Entity/Aggregate Root
│
└─ 是技術細節(發郵件、調 API)?
   └─ YES → Infrastructure Service
````

## 總結

**Domain Service**:

- 位於**領域層**
- 處理**跨聚合的業務邏輯**
- **不依賴**基礎設施(Repository, 外部 API)
- **不管理**事務
- 返回**領域對象**
- 可被**多個** Application Service 復用

**Application Service**:

- 位於**應用層**
- **編排流程**,協調領域對象
- **依賴** Repository
- **管理**事務邊界 (@Transactional)
- 返回 **DTO**
- 直接被**外層**調用

**命名建議**:

```java
// Domain Service
OrderValidationService
OrderPricingService
DiscountCalculator
TaxCalculator
TransferService

// Application Service
OrderApplicationService
CustomerApplicationService
// 或簡化為
OrderService (如果不會混淆)
```

你原來的例子應該這樣命名:

```java
// ✅ 清晰的命名
public class OrderApplicationService {  // 改這個名字
    private final OrderValidationService validationService;  // 這是 Domain Service
    // ...
}
```

===========================================================================

Application Service 萬一我有很多個折價券 , 或是會員折扣, 這些算是業務邏輯嗎 ? ( 它們是有季節性的 ) 我要放在 Application service 還是 Domain Service

這是一個非常典型且重要的架構決策點。

直接回答你的問題： **這絕對是「業務邏輯」，而且絕對「不能」放在 Application Service。**

這些邏輯應該放在 **Domain Layer**，但由於它們具有「多樣性」和「季節性（易變性）」，單純寫死在 `OrderPricingService` 裡也會很難維護。

這時候你需要引入 **策略模式 (Strategy Pattern)** 或 **規格模式 (Specification Pattern)**。

---

### 1. 為什麼不能放在 Application Service？

Application Service 的職責是 **「流程編排」**。它的代碼應該相對穩定，不應該因為行銷部門決定「下週二舉辦萬聖節活動」而需要修改代碼。

如果你把折扣邏輯寫在 AS：

- **違反開閉原則 (OCP)**：每次規則改變都要改 AS，AS 會變得非常脆弱。
    
- **邏輯洩漏**：折扣計算是核心商業價值，不是流程控制。
    
- **難以測試**：要在 AS 層級測試各種複雜的折扣組合非常痛苦。
    

### 2. 架構師的建議方案：Domain Service + 策略模式

針對這種「會隨時間改變」、「有多種規則疊加」的業務邏輯，我們通常會這樣設計：

#### 第一步：定義折扣策略介面 (Interface)

在 Domain Layer 定義一個標準的介面，所有的折扣規則（無論是會員、季節性、折價券）都必須遵守這個契約。

```Java
// Domain Layer
public interface DiscountStrategy {
    // 判斷該策略是否適用於此訂單
    boolean isApplicable(Order order, Customer customer);
    
    // 計算折扣金額
    Money calculateDiscount(Order order, Customer customer);
    
    // 優先級 (決定先算哪個折扣，例如先扣會員再扣折價券)
    int priority();
}
```

#### 第二步：實作具體的業務規則

這些類別也是 Domain Layer 的一部分。你可以隨意新增、刪除，而不會影響到主要的 Service。

```Java
// 實作 1: VIP 會員折扣 (長期規則)
public class VipMemberDiscountStrategy implements DiscountStrategy {
    public boolean isApplicable(Order order, Customer customer) {
        return customer.isVIP();
    }
    public Money calculateDiscount(Order order, Customer customer) {
        return order.getSubtotal().multiply(0.1); // 9折
    }
    public int priority() { return 10; }
}

// 實作 2: 聖誕節大促銷 (季節性規則)
// 可以透過設定檔或資料庫開關來控制是否生效
public class ChristmasDiscountStrategy implements DiscountStrategy {
    private final Clock clock; // 注入時間避免依賴
    
    public boolean isApplicable(Order order, Customer customer) {
        LocalDate today = LocalDate.now(clock);
        return today.getMonth() == Month.DECEMBER && order.getTotalAmount().isGreaterThan(Money.of(2000));
    }
    public Money calculateDiscount(Order order, Customer customer) {
        return Money.of(200); // 滿2000折200
    }
    public int priority() { return 20; }
}
```

#### 第三步：進化後的 Domain Service

你的 `OrderPricingService` 不再寫死 `if-else`，而是變成一個 **「策略執行器」**。


```Java
public class OrderPricingService {
    // 這裡注入所有的策略實作 (Spring 可以自動注入 List<DiscountStrategy>)
    private final List<DiscountStrategy> discountStrategies; 

    public OrderPricingService(List<DiscountStrategy> discountStrategies) {
        this.discountStrategies = discountStrategies;
    }

    public Money calculateFinalPrice(Order order, Customer customer) {
        Money currentPrice = order.getSubtotal();
        
        // 1. 根據優先級排序策略
        List<DiscountStrategy> sortedStrategies = discountStrategies.stream()
            .sorted(Comparator.comparingInt(DiscountStrategy::priority))
            .collect(Collectors.toList());

        // 2. 逐一應用策略
        for (DiscountStrategy strategy : sortedStrategies) {
            if (strategy.isApplicable(order, customer)) {
                Money discount = strategy.calculateDiscount(order, customer);
                currentPrice = currentPrice.subtract(discount);
                
                // 可以在這裡加入邏輯紀錄使用了哪個優惠，方便後續顯示給使用者
                order.addAppliedDiscount(strategy.getName(), discount);
            }
        }
        
        // 防止負數
        return currentPrice.isNegative() ? Money.ZERO : currentPrice;
    }
}
```

---

### 3. Application Service 該做什麼？

在這種架構下，Application Service 的工作依然是 **「協調」**：

1. 從 Repository 撈出訂單。
    
2. 從 Repository 撈出 **「當下有效的」** 折價券列表 (如果這不是寫在 Code 裡，而是存在 DB 的話)。
    
3. 呼叫 `pricingService.calculateFinalPrice(...)`。
    
4. 保存。
    
```Java
// Application Service
@Transactional
public void calculateOrderPrice(String orderId) {
    Order order = orderRepo.findById(orderId);
    Customer customer = customerRepo.findById(order.getCustomerId());
    
    // 如果策略是動態的（存在 DB 裡的規則），這裡可能需要撈出規則
    // 但如果策略是寫成 Java Class 的 (如上面的例子)，則不需要這步
    
    // 純粹計算，完全不關心現在是聖誕節還是春節，細節都在策略裡
    Money finalPrice = pricingService.calculateFinalPrice(order, customer);
    
    order.confirm(finalPrice);
    orderRepo.save(order);
}
```

### 總結

面對複雜且易變的折扣邏輯：

1. **Application Service**：**只負責流程**。絕對不要放 `if (isChristmas)` 這種邏輯。
    
2. **Domain Service**：**負責計算的骨架**。它遍歷所有規則，但不包含具體規則的細節。
    
3. **Strategy Classes (Domain Objects)**：**負責具體邏輯**。每一個折扣規則（會員、折價券、季節活動）都是一個獨立的小類別。
    

**這樣做的好處：** 明年你要加一個「端午節折扣」，你只需要 **新增一個 Class (`DragonBoatFestivalStrategy`)**，完全不用去改 Application Service 或 Domain Service 的程式碼，系統非常穩健且易於擴充。
