**問題核心**：  
Domain Service 需要資料來執行業務邏輯，但直接依賴 DAO 會污染領域層，違反 DDD 的分層原則。

#### ✅ **正確做法：透過 Repository 介面取得資料**

- **領域層**（Domain Layer）不應直接依賴 DAO（屬於基礎設施層），而是依賴 **Repository 介面**。
    
- **Repository 實作** 在基礎設施層注入 DAO，負責資料存取與轉換。
    

**程式碼範例**：

```java
// 領域層定義 Repository 介面（純領域概念）
public interface OrderRepository {
    Order findById(OrderId id);
    void save(Order order);
}

// 基礎設施層實作 Repository（依賴 DAO）
public class OrderRepositoryImpl implements OrderRepository {
    private final OrderDAO orderDAO; // 依賴 DAO

    @Override
    public Order findById(OrderId id) {
        OrderDO orderDO = orderDAO.findById(id.getValue());
        return OrderConverter.toDomain(orderDO); // 轉換為領域物件
    }
}

// Domain Service 只依賴 Repository 介面
public class OrderService {
    private final OrderRepository orderRepository;

    public OrderService(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }

    public void processOrder(OrderId id) {
        Order order = orderRepository.findById(id); // 透過 Repository 取資料
        order.doSomething(); // 業務邏輯
        orderRepository.save(order);
    }
}
```

**優點**：

- **領域層純淨**：Domain Service 只看到 `OrderRepository` 介面，不知 DAO 存在。
    
- **易於測試**：可 Mock `OrderRepository` 進行單元測試。
    
- **靈活替換**：未來可替換 DAO 實作（如從 MySQL 換成 MongoDB）。

### 2. **回傳給使用者的資料格式轉換**

**問題核心**：  
從資料庫到前端的資料流需要多次轉換（`DO → Domain Model → DTO`），且轉換過程可能需要額外查詢。

#### ✅ **正確做法：分層轉換 + Application Service 協調**

1. **Domain Layer**：
    
    - 使用 **Repository** 取得 `Domain Model`（如 `Order`）。
        
2. **Application Layer**：
    
    - 透過 **DTO Assembler** 將 `Domain Model` 轉為 `DTO`。
        
    - 若需補充資料，由 **Application Service** 呼叫多個 Repository 或外部服務。
        

**程式碼範例**：

```java
// Application Service 協調轉換與流程
public class OrderApplicationService {
    private final OrderRepository orderRepository;
    private final UserRepository userRepository;
    private final OrderDTOAssembler assembler;

    public OrderDTO getOrderDetails(OrderId id) {
        // 1. 取得領域物件
        Order order = orderRepository.findById(id);
        User user = userRepository.findById(order.getUserId());

        // 2. 補充資料並轉換為 DTO
        return assembler.toDTO(order, user);
    }
}

// DTO Assembler 處理複雜轉換
public class OrderDTOAssembler {
    public OrderDTO toDTO(Order order, User user) {
        OrderDTO dto = new OrderDTO();
        dto.setOrderId(order.getId().getValue());
        dto.setUserName(user.getName()); // 補充額外資料
        dto.setItems(order.getItems().stream().map(this::toItemDTO).toList());
        return dto;
    }
}
```

**優點**：

- **職責分離**：
    
    - Repository 負責 `DO ↔ Domain Model`。
        
    - Assembler 負責 `Domain Model ↔ DTO`。
        
- **彈性擴充**：
    
    - 可輕鬆在 Application Service 中整合快取、外部 API 等。

### 總結：依賴關係圖

[Domain Layer]
    ↑
[OrderRepository] (介面)
    ↑
[Infrastructure Layer]
    ├── OrderRepositoryImpl (依賴 OrderDAO)
    └── OrderQueryDAO (直接回傳 DTO)

[Application Layer]
    ├── OrderApplicationService (協調 Repository + Assembler)
    └── OrderQueryService (高效查詢 DTO)

### 關鍵原則：

1. **領域層不依賴 DAO**：透過 Repository 介面隔離。
    
2. **轉換邏輯分散處理**：
    
    - Repository 處理 `DO ↔ Domain Model`。
        
    - Assembler 處理 `Domain Model ↔ DTO`。
        
3. **複雜查詢優化**：必要時使用 CQRS 或專用查詢服務。
    

這樣既能保持領域層的純淨，又能靈活應對商業需求！











