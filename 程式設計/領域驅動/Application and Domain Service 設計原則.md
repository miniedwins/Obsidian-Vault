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