## 問題分析

```java
// ⚠️ 這是有問題的設計
public class OrderApplicationService {
    private final OrderRepository orderRepository;
    private final CustomerRepository customerRepository;
    private final ProductRepository productRepository;
    private final OrderPricingService pricingService;
    private final OrderValidationService validationService;
    private final InventoryService inventoryService;
    private final ShippingService shippingService;
    private final PaymentService paymentService;
    private final DiscountService discountService;
    private final TaxService taxService;
    private final NotificationService notificationService;
    private final EmailService emailService;
    // ... 還有更多
}
```

**問題在哪裡?**

1. **職責過重** - 違反單一職責原則
2. **耦合度高** - 依賴太多服務
3. **難以測試** - 需要 mock 一大堆依賴
4. **可讀性差** - 方法內邏輯複雜

## 解決方案

### 方案 1: 拆分 Application Service

按業務用例拆分成更細粒度的服務:

java

```java
// ✅ 拆分成多個專注的 Application Service

// 訂單創建服務
public class CreateOrderService {
    private final OrderRepository orderRepository;
    private final CustomerRepository customerRepository;
    private final OrderValidationService validationService;
    private final OrderPricingService pricingService;
    
    @Transactional
    public OrderDto createOrder(CreateOrderCommand command) {
        // 只處理訂單創建邏輯
    }
}

// 訂單支付服務
public class OrderPaymentService {
    private final OrderRepository orderRepository;
    private final PaymentService paymentService;
    private final EmailService emailService;
    
    @Transactional
    public PaymentResult processPayment(ProcessPaymentCommand command) {
        // 只處理支付邏輯
    }
}

// 訂單配送服務
public class OrderShippingService {
    private final OrderRepository orderRepository;
    private final ShippingService shippingService;
    private final InventoryService inventoryService;
    
    @Transactional
    public void shipOrder(ShipOrderCommand command) {
        // 只處理配送邏輯
    }
}
```

### 方案 2: 使用 Facade Pattern (Domain Service)

創建一個 Domain Service 來組合其他 Domain Service:

java

```java
// ✅ 在領域層創建組合服務
public class OrderFulfillmentService {  // Domain Service
    private final InventoryService inventoryService;
    private final PaymentService paymentService;
    private final ShippingService shippingService;
    
    // 這個服務封裝了複雜的業務流程
    public FulfillmentResult fulfillOrder(Order order) {
        // 協調多個領域服務
    }
}

// Application Service 變得簡潔
public class PlaceOrderService {
    private final OrderRepository orderRepository;
    private final CustomerRepository customerRepository;
    private final OrderFulfillmentService fulfillmentService;  // 只依賴一個
    private final EmailService emailService;
    
    @Transactional
    public OrderDto placeOrder(PlaceOrderCommand command) {
        Customer customer = customerRepository.findById(command.getCustomerId());
        Order order = new Order(customer.getId(), command.getItems());
        
        FulfillmentResult result = fulfillmentService.fulfillOrder(order);
        
        orderRepository.save(order);
        emailService.sendConfirmation(order);
        
        return OrderDto.from(order);
    }
}
```

### 方案 3: 使用 Event-Driven Architecture

減少直接依賴,通過事件解耦:

java

```java
// ✅ 使用領域事件
public class PlaceOrderService {
    private final OrderRepository orderRepository;
    private final OrderValidationService validationService;
    private final DomainEventPublisher eventPublisher;
    
    @Transactional
    public OrderDto placeOrder(PlaceOrderCommand command) {
        // 創建訂單
        Order order = Order.create(command);
        
        // 驗證
        validationService.validate(order);
        
        // 保存
        orderRepository.save(order);
        
        // 發布事件,讓其他服務異步處理
        eventPublisher.publish(new OrderPlacedEvent(order.getId()));
        
        return OrderDto.from(order);
    }
}

// 其他服務監聽事件
@EventHandler
public class OrderPlacedEventHandler {
    private final InventoryService inventoryService;
    private final EmailService emailService;
    
    public void handle(OrderPlacedEvent event) {
        inventoryService.reserveItems(event.getOrderId());
        emailService.sendConfirmation(event.getOrderId());
    }
}
```

## 經驗法則

**Application Service 的依賴數量**:

- **3-5 個依賴**: ✅ 合理
- **6-8 個依賴**: ⚠️ 考慮重構
- **9+ 個依賴**: ❌ 必須重構

**重構信號**:

- 構造函數參數超過 5 個
- 單個方法超過 30 行
- 方法內有超過 3 層的業務邏輯嵌套
- 測試需要 mock 超過 5 個依賴

## 推薦做法

java

```java
// ✅ 好的設計:職責單一,依賴精簡
public class CreateOrderService {
    private final OrderRepository orderRepository;
    private final OrderFactory orderFactory;           // 創建邏輯
    private final OrderValidationService validationService;  // 驗證邏輯
    
    @Transactional
    public OrderDto execute(CreateOrderCommand command) {
        Order order = orderFactory.create(command);
        validationService.validate(order);
        orderRepository.save(order);
        return OrderDto.from(order);
    }
}
```
