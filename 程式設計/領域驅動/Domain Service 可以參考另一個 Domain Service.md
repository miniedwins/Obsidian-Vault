**可以**,但要避免循環依賴和過度耦合:

```java
// ✅ 可以參考其他 Domain Service
public class OrderPricingService {
    private final DiscountCalculator discountCalculator;
    private final TaxCalculator taxCalculator;
    
    public Money calculateTotalPrice(Order order, Customer customer) {
        Money subtotal = order.getSubtotal();
        Money discount = discountCalculator.calculate(customer, subtotal);
        Money afterDiscount = subtotal.subtract(discount);
        Money tax = taxCalculator.calculate(afterDiscount);
        return afterDiscount.add(tax);
    }
}
```

**注意事項**:

- 避免 A → B → A 的循環依賴
- 如果依賴鏈太長,考慮重新設計職責劃分

## 2. 可以新建 Domain Service 組合多個 Domain Service ✅

**完全可以**,這是常見的模式,稱為 **Composite/Orchestration Service**:

```java
// ✅ 組合多個 Domain Service 的協調服務
public class OrderFulfillmentService {
    private final InventoryService inventoryService;
    private final PaymentService paymentService;
    private final ShippingService shippingService;
    private final NotificationService notificationService;
    
    public FulfillmentResult fulfillOrder(Order order) {
        // 協調多個領域服務完成複雜業務流程
        
        // 1. 檢查庫存
        if (!inventoryService.reserveItems(order.getItems())) {
            return FulfillmentResult.outOfStock();
        }
        
        // 2. 處理付款
        PaymentResult payment = paymentService.processPayment(order);
        if (!payment.isSuccessful()) {
            inventoryService.releaseItems(order.getItems());
            return FulfillmentResult.paymentFailed();
        }
        
        // 3. 安排配送
        ShippingResult shipping = shippingService.arrangeShipping(order);
        
        // 4. 發送通知
        notificationService.notifyOrderConfirmed(order);
        
        return FulfillmentResult.success(shipping);
    }
}
```

**適用場景**:

- 複雜的業務流程需要協調多個領域服務
- 避免 Application Service 變得過於複雜

## 3. Application Service 可以有多個 Domain Service ✅

**可以,而且很常見**。Application Service 負責協調多個 Domain Service 和 Repository:

````java
// ✅ Application Service 協調多個 Domain Service
public class OrderApplicationService {
    private final OrderRepository orderRepository;
    private final CustomerRepository customerRepository;
    private final OrderPricingService pricingService;        // Domain Service
    private final OrderValidationService validationService;  // Domain Service
    private final InventoryService inventoryService;         // Domain Service
    private final EmailService emailService;                 // Infrastructure
    
    @Transactional
    public OrderDto placeOrder(PlaceOrderCommand command) {
        // 1. 載入聚合
        Customer customer = customerRepository.findById(command.getCustomerId());
        
        // 2. 使用 Domain Service 驗證
        ValidationResult validation = validationService.validateOrder(
            command.getItems(), 
            customer
        );
        if (!validation.isValid()) {
            throw new InvalidOrderException(validation.getErrors());
        }
        
        // 3. 創建訂單
        Order order = new Order(customer.getId(), command.getItems());
        
        // 4. 使用 Domain Service 計算價格
        Money totalPrice = pricingService.calculateTotalPrice(order, customer);
        order.setTotalPrice(totalPrice);
        
        // 5. 使用 Domain Service 預留庫存
        inventoryService.reserveItems(order.getItems());
        
        // 6. 保存
        orderRepository.save(order);
        
        // 7. 發送通知 (基礎設施關注點)
        emailService.sendOrderConfirmation(order);
        
        return OrderDto.from(order);
    }
}
```

## 設計原則總結
```
Application Service (應用層)
├── 協調多個 Domain Service
├── 管理事務邊界
├── 處理基礎設施關注點 (Email, 外部 API)
└── 編排業務流程

Domain Service (領域層)
├── 可以調用其他 Domain Service
├── 可以組合成更高層的 Domain Service
├── 封裝跨聚合的業務邏輯
└── 保持領域邏輯純粹 (不處理基礎設施)

Entity/Value Object (領域層)
└── 封裝單一聚合內的業務規則
````

**關鍵區別**:

- **Application Service**: 流程協調、事務管理、與外部系統交互
- **Domain Service**: 純粹的領域邏輯,跨聚合的業務規則
- **Entity**: 聚合內的業務邏輯和一致性維護

這種分層設計讓每一層都有清晰的職責,代碼更容易維護和測試。