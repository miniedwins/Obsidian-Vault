Entity **可以直接參考**同一個 Aggregate(聚合)內的其他 Entity:

```java
// Order 是 Aggregate Root
public class Order {
    private OrderId id;
    private List<OrderLine> orderLines;  // ✅ 可以直接參考
    private ShippingAddress address;
    
    public void addOrderLine(Product product, int quantity) {
        // 直接操作聚合內的 Entity
        orderLines.add(new OrderLine(product, quantity));
    }
}

// OrderLine 也是 Entity,但屬於 Order 聚合
public class OrderLine {
    private OrderLineId id;
    private Product product;
    private int quantity;
}
```

## 跨 Aggregate 的參考規則

**不應該直接持有對象參考**,而應該只持有 ID:

```java
// ❌ 錯誤:跨聚合直接參考 Entity 對象
public class Order {
    private Customer customer;  // 不應該直接持有
}

// ✅ 正確:只持有 ID
public class Order {
    private CustomerId customerId;  // 只持有身份標識
    
    // 需要時通過 Repository 獲取
    public void process(CustomerRepository customerRepo) {
        Customer customer = customerRepo.findById(customerId);
        // 使用 customer
    }
}
```

## Entity 參考服務(Service)

Entity **不應該直接依賴 Domain Service 或 Application Service**:

```java
// ❌ 錯誤:Entity 依賴服務
public class Order {
    private EmailService emailService;  // 不應該注入服務
    
    public void confirm() {
        this.status = OrderStatus.CONFIRMED;
        emailService.sendConfirmation(this);  // Entity 不該調用服務
    }
}

// ✅ 正確:由外部協調
public class OrderService {
    public void confirmOrder(Order order, EmailService emailService) {
        order.confirm();  // Entity 只改變自己的狀態
        emailService.sendConfirmation(order);  // 服務層處理副作用
    }
}
```

## 總結規則

|情況|是否允許|原因|
|---|---|---|
|參考同聚合內的 Entity|✅ 允許|聚合內保持一致性|
|參考其他 Aggregate 的 Entity 對象|❌ 不允許|破壞聚合邊界,只能持有 ID|
|參考 Domain Service|❌ 不允許|Entity 應保持純粹,服務由外部協調|
|參考 Value Object/Domain Primitive|✅ 允許|這是 Entity 的組成部分|

**核心原則**:Entity 應該專注於**封裝業務邏輯和保持自身一致性**,而不是處理跨聚合協調或基礎設施關注點。