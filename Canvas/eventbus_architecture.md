## 1. EventBus 核心架構

```mermaid
flowchart TB
    subgraph "EventBus 核心組件"
        EB[("EventBus<br/>事件總線")]
        REG["EventRegistry<br/>事件註冊表<br/>Dict[EventType → Set[Invoker]]"]
        INV["Invoker<br/>調用器<br/>封裝處理器調用邏輯"]
        EXE["Executor<br/>執行器<br/>同步/異步執行"]
    end
    
    subgraph "領域事件基類"
        EVENT["Event<br/>抽象基類<br/>occurred_at: datetime"]
    end
    
    subgraph "領域實體 (發布者)"
        ORDER["Order<br/>訂單聚合"]
        PRODUCT["Product<br/>商品實體"]
    end
    
    subgraph "事件處理器 (訂閱者)"
        OH["OrderEventHandler<br/>訂單處理器"]
        IH["InventoryEventHandler<br/>庫存處理器"]
        NH["NotificationService<br/>通知服務"]
        AH["AnalyticsHandler<br/>分析處理器"]
    end
    
    %% 關係連接
    ORDER -->|"publish(event)"| EB
    PRODUCT -->|"publish(event)"| EB
    
    EB --> REG
    REG --> INV
    INV --> EXE
    
    EXE -->|"dispatch"| OH
    EXE -->|"dispatch"| IH
    EXE -->|"dispatch"| NH
    EXE -->|"dispatch"| AH
    
    OH -.->|"register(self)"| EB
    IH -.->|"register(self)"| EB
    NH -.->|"register(self)"| EB
    AH -.->|"register(self)"| EB
    
    EVENT -.->|"繼承"| ORDER
    EVENT -.->|"繼承"| PRODUCT
    
    style EB fill:#4a90e2,stroke:#2563eb,stroke-width:3px,color:#fff
    style EVENT fill:#9333ea,stroke:#7c3aed,stroke-width:2px,color:#fff
    style ORDER fill:#f97316,stroke:#ea580c,stroke-width:2px,color:#fff
    style PRODUCT fill:#f97316,stroke:#ea580c,stroke-width:2px,color:#fff
    style OH fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    style IH fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    style NH fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    style AH fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
```

---

## 2. 事件繼承層次結構

```mermaid
flowchart TB
    EVENT["Event<br/>(抽象基類)<br/>occurred_at: datetime"]
    
    subgraph "訂單相關事件"
        OPE["OrderPlacedEvent<br/>訂單已下單<br/>order: Order"]
        PCE["PaymentCompletedEvent<br/>支付完成<br/>order: Order"]
        OSE["OrderShippedEvent<br/>訂單已發貨<br/>order: Order"]
        OCE["OrderCancelledEvent<br/>訂單已取消<br/>order: Order<br/>previous_status: OrderStatus"]
    end
    
    subgraph "商品/庫存相關事件"
        PPE["ProductPurchasedEvent<br/>商品已購買<br/>product_id, quantity, order_id"]
        IRE["InventoryReservedEvent<br/>庫存已預留<br/>product_id, quantity, order_id"]
        LSE["LowStockAlertEvent<br/>低庫存警告<br/>product: Product<br/>current_stock, threshold"]
    end
    
    EVENT ==>|"繼承"| OPE
    EVENT ==>|"繼承"| PCE
    EVENT ==>|"繼承"| OSE
    EVENT ==>|"繼承"| OCE
    EVENT ==>|"繼承"| PPE
    EVENT ==>|"繼承"| IRE
    EVENT ==>|"繼承"| LSE
    
    style EVENT fill:#9333ea,stroke:#7c3aed,stroke-width:3px,color:#fff
    style OPE fill:#ef4444,stroke:#dc2626,stroke-width:2px,color:#fff
    style PCE fill:#ef4444,stroke:#dc2626,stroke-width:2px,color:#fff
    style OSE fill:#ef4444,stroke:#dc2626,stroke-width:2px,color:#fff
    style OCE fill:#ef4444,stroke:#dc2626,stroke-width:2px,color:#fff
    style PPE fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff
    style IRE fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff
    style LSE fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff
```

---

## 3. 事件訂閱關係圖

```mermaid
flowchart LR
    subgraph "領域事件"
        OPE["OrderPlacedEvent"]
        PCE["PaymentCompletedEvent"]
        OSE["OrderShippedEvent"]
        OCE["OrderCancelledEvent"]
        PPE["ProductPurchasedEvent"]
        IRE["InventoryReservedEvent"]
        LSE["LowStockAlertEvent"]
    end
    
    subgraph "事件處理器"
        OH["OrderEventHandler"]
        IH["InventoryEventHandler"]
        NH["NotificationService"]
        AH["AnalyticsHandler"]
    end
    
    %% OrderEventHandler 訂閱
    OPE -.->|"訂閱"| OH
    PCE -.->|"訂閱"| OH
    OSE -.->|"訂閱"| OH
    OCE -.->|"訂閱"| OH
    
    %% InventoryEventHandler 訂閱
    PPE -.->|"訂閱"| IH
    IRE -.->|"訂閱"| IH
    LSE -.->|"訂閱"| IH
    
    %% NotificationService 訂閱
    OPE -.->|"訂閱"| NH
    PCE -.->|"訂閱"| NH
    OSE -.->|"訂閱"| NH
    OCE -.->|"訂閱"| NH
    LSE -.->|"訂閱"| NH
    
    %% AnalyticsHandler 訂閱所有事件
    OPE -.->|"訂閱"| AH
    PCE -.->|"訂閱"| AH
    OSE -.->|"訂閱"| AH
    OCE -.->|"訂閱"| AH
    PPE -.->|"訂閱"| AH
    IRE -.->|"訂閱"| AH
    LSE -.->|"訂閱"| AH
    
    style OPE fill:#ef4444,stroke:#dc2626,stroke-width:2px,color:#fff
    style PCE fill:#ef4444,stroke:#dc2626,stroke-width:2px,color:#fff
    style OSE fill:#ef4444,stroke:#dc2626,stroke-width:2px,color:#fff
    style OCE fill:#ef4444,stroke:#dc2626,stroke-width:2px,color:#fff
    style PPE fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff
    style IRE fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff
    style LSE fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff
    
    style OH fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    style IH fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    style NH fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    style AH fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
```

---

## 4. 完整的事件流程 (訂單處理)

```mermaid
flowchart TB
    START(("客戶下單"))
    
    subgraph "步驟 1: 下單"
        ORDER1["Order.place()"]
        OPE1["發布<br/>OrderPlacedEvent"]
        EB1[("EventBus")]
        
        subgraph "並行處理"
            OH1["OrderEventHandler<br/>發送確認郵件"]
            IH1["InventoryEventHandler<br/>預留庫存"]
            NH1["NotificationService<br/>通知客戶"]
            AH1["AnalyticsHandler<br/>記錄數據"]
        end
    end
    
    subgraph "步驟 2: 付款"
        ORDER2["Order.pay()"]
        PCE1["發布<br/>PaymentCompletedEvent"]
        EB2[("EventBus")]
        
        subgraph "並行處理 2"
            OH2["OrderEventHandler<br/>通知倉庫"]
            NH2["NotificationService<br/>付款成功通知"]
            AH2["AnalyticsHandler<br/>記錄付款"]
        end
    end
    
    subgraph "步驟 3: 發貨"
        ORDER3["Order.ship()"]
        OSE1["發布<br/>OrderShippedEvent"]
        EB3[("EventBus")]
        
        subgraph "並行處理 3"
            OH3["OrderEventHandler<br/>更新狀態"]
            NH3["NotificationService<br/>發貨通知"]
            AH3["AnalyticsHandler<br/>記錄發貨"]
        end
    end
    
    END(("訂單完成"))
    
    START --> ORDER1
    ORDER1 --> OPE1
    OPE1 --> EB1
    EB1 ==> OH1 & IH1 & NH1 & AH1
    
    OH1 & IH1 & NH1 & AH1 --> ORDER2
    ORDER2 --> PCE1
    PCE1 --> EB2
    EB2 ==> OH2 & NH2 & AH2
    
    OH2 & NH2 & AH2 --> ORDER3
    ORDER3 --> OSE1
    OSE1 --> EB3
    EB3 ==> OH3 & NH3 & AH3
    
    OH3 & NH3 & AH3 --> END
    
    style START fill:#22c55e,stroke:#16a34a,stroke-width:3px,color:#fff
    style END fill:#22c55e,stroke:#16a34a,stroke-width:3px,color:#fff
    
    style ORDER1 fill:#f97316,stroke:#ea580c,stroke-width:2px,color:#fff
    style ORDER2 fill:#f97316,stroke:#ea580c,stroke-width:2px,color:#fff
    style ORDER3 fill:#f97316,stroke:#ea580c,stroke-width:2px,color:#fff
    
    style OPE1 fill:#ef4444,stroke:#dc2626,stroke-width:2px,color:#fff
    style PCE1 fill:#ef4444,stroke:#dc2626,stroke-width:2px,color:#fff
    style OSE1 fill:#ef4444,stroke:#dc2626,stroke-width:2px,color:#fff
    
    style EB1 fill:#4a90e2,stroke:#2563eb,stroke-width:3px,color:#fff
    style EB2 fill:#4a90e2,stroke:#2563eb,stroke-width:3px,color:#fff
    style EB3 fill:#4a90e2,stroke:#2563eb,stroke-width:3px,color:#fff
    
    style OH1 fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    style OH2 fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    style OH3 fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    style IH1 fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    style NH1 fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    style NH2 fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    style NH3 fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    style AH1 fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    style AH2 fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    style AH3 fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
```

---

## 5. EventBus 內部工作流程

```mermaid
flowchart TB
    START(("應用啟動"))
    
    subgraph "初始化階段"
        INIT1["創建 EventBus"]
        INIT2["創建 EventRegistry"]
        INIT3["創建 Executor<br/>(ThreadPoolExecutor)"]
        INIT4["創建事件處理器<br/>(OrderEventHandler, etc.)"]
    end
    
    subgraph "註冊階段"
        REG1["handler.register(listener)"]
        REG2["掃描 listener 的方法<br/>inspect.getmembers()"]
        REG3{"方法名是否以<br/>handle_ 或 on_ 開頭?"}
        REG4["檢查第一個參數<br/>的類型註解"]
        REG5{"參數類型是否<br/>繼承自 Event?"}
        REG6["創建 Invoker<br/>(listener, method, event_type)"]
        REG7["加入註冊表<br/>registry[event_type].add(invoker)"]
    end
    
    subgraph "發布階段"
        PUB1["entity.method()<br/>(如 order.place())"]
        PUB2["創建事件對象<br/>(如 OrderPlacedEvent)"]
        PUB3["event_bus.publish(event)"]
        PUB4["獲取事件類型<br/>type(event)"]
        PUB5["查找訂閱者<br/>registry[event_type]"]
        PUB6{"有訂閱者?"}
    end
    
    subgraph "分發階段 (同步)"
        SYNC1["遍歷所有 invokers"]
        SYNC2["invoker.invoke(event)"]
        SYNC3["method(event)"]
        SYNC4["處理器執行業務邏輯"]
    end
    
    subgraph "分發階段 (異步)"
        ASYNC1["遍歷所有 invokers"]
        ASYNC2["executor.submit(invoker, event)"]
        ASYNC3["線程池執行"]
        ASYNC4["invoker.invoke(event)"]
        ASYNC5["method(event)"]
    end
    
    END(("完成"))
    
    START --> INIT1
    INIT1 --> INIT2
    INIT2 --> INIT3
    INIT3 --> INIT4
    
    INIT4 --> REG1
    REG1 --> REG2
    REG2 --> REG3
    REG3 -->|"是"| REG4
    REG3 -->|"否"| REG2
    REG4 --> REG5
    REG5 -->|"是"| REG6
    REG5 -->|"否"| REG2
    REG6 --> REG7
    
    REG7 --> PUB1
    PUB1 --> PUB2
    PUB2 --> PUB3
    PUB3 --> PUB4
    PUB4 --> PUB5
    PUB5 --> PUB6
    
    PUB6 -->|"同步模式"| SYNC1
    SYNC1 --> SYNC2
    SYNC2 --> SYNC3
    SYNC3 --> SYNC4
    SYNC4 --> END
    
    PUB6 -->|"異步模式"| ASYNC1
    ASYNC1 --> ASYNC2
    ASYNC2 --> ASYNC3
    ASYNC3 --> ASYNC4
    ASYNC4 --> ASYNC5
    ASYNC5 --> END
    
    PUB6 -->|"無訂閱者"| END
    
    style START fill:#22c55e,stroke:#16a34a,stroke-width:3px,color:#fff
    style END fill:#22c55e,stroke:#16a34a,stroke-width:3px,color:#fff
    
    style INIT1 fill:#6366f1,stroke:#4f46e5,stroke-width:2px,color:#fff
    style INIT2 fill:#6366f1,stroke:#4f46e5,stroke-width:2px,color:#fff
    style INIT3 fill:#6366f1,stroke:#4f46e5,stroke-width:2px,color:#fff
    style INIT4 fill:#6366f1,stroke:#4f46e5,stroke-width:2px,color:#fff
    
    style REG1 fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px,color:#fff
    style REG2 fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px,color:#fff
    style REG3 fill:#ec4899,stroke:#db2777,stroke-width:2px,color:#fff
    style REG4 fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px,color:#fff
    style REG5 fill:#ec4899,stroke:#db2777,stroke-width:2px,color:#fff
    style REG6 fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px,color:#fff
    style REG7 fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px,color:#fff
    
    style PUB1 fill:#f97316,stroke:#ea580c,stroke-width:2px,color:#fff
    style PUB2 fill:#f97316,stroke:#ea580c,stroke-width:2px,color:#fff
    style PUB3 fill:#f97316,stroke:#ea580c,stroke-width:2px,color:#fff
    style PUB4 fill:#f97316,stroke:#ea580c,stroke-width:2px,color:#fff
    style PUB5 fill:#f97316,stroke:#ea580c,stroke-width:2px,color:#fff
    style PUB6 fill:#ec4899,stroke:#db2777,stroke-width:2px,color:#fff
    
    style SYNC1 fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    style SYNC2 fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    style SYNC3 fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    style SYNC4 fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    
    style ASYNC1 fill:#06b6d4,stroke:#0891b2,stroke-width:2px,color:#fff
    style ASYNC2 fill:#06b6d4,stroke:#0891b2,stroke-width:2px,color:#fff
    style ASYNC3 fill:#06b6d4,stroke:#0891b2,stroke-width:2px,color:#fff
    style ASYNC4 fill:#06b6d4,stroke:#0891b2,stroke-width:2px,color:#fff
    style ASYNC5 fill:#06b6d4,stroke:#0891b2,stroke-width:2px,color:#fff
```

---

## 6. 設計模式關係圖

```mermaid
flowchart TB
    subgraph "設計模式"
        OBS["觀察者模式<br/>(Observer Pattern)<br/>一對多的依賴關係"]
        MED["中介者模式<br/>(Mediator Pattern)<br/>EventBus 作為中介"]
        SIN["單例模式<br/>(Singleton Pattern)<br/>全局唯一的 EventBus"]
        STR["策略模式<br/>(Strategy Pattern)<br/>不同的執行策略"]
    end
    
    subgraph "實現技術"
        REF["反射 (Reflection)<br/>inspect.getmembers()"]
        TYPE["類型註解<br/>(Type Hints)<br/>Event 子類匹配"]
        CON["約定優於配置<br/>(Convention)<br/>handle_*, on_*"]
        ASYNC["異步執行<br/>(Async Executor)<br/>ThreadPoolExecutor"]
    end
    
    subgraph "核心優勢"
        DEC["解耦<br/>(Decoupling)<br/>發布者與訂閱者解耦"]
        EXT["可擴展<br/>(Extensibility)<br/>易於添加新的處理器"]
        TEST["可測試<br/>(Testability)<br/>易於單元測試"]
        PERF["性能<br/>(Performance)<br/>異步並行處理"]
    end
    
    OBS --> DEC
    MED --> DEC
    SIN --> PERF
    STR --> EXT
    
    REF --> CON
    TYPE --> CON
    CON --> EXT
    ASYNC --> PERF
    
    DEC --> TEST
    EXT --> TEST
    
    style OBS fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px,color:#fff
    style MED fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px,color:#fff
    style SIN fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px,color:#fff
    style STR fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px,color:#fff
    
    style REF fill:#06b6d4,stroke:#0891b2,stroke-width:2px,color:#fff
    style TYPE fill:#06b6d4,stroke:#0891b2,stroke-width:2px,color:#fff
    style CON fill:#06b6d4,stroke:#0891b2,stroke-width:2px,color:#fff
    style ASYNC fill:#06b6d4,stroke:#0891b2,stroke-width:2px,color:#fff
    
    style DEC fill:#22c55e,stroke:#16a34a,stroke-width:2px,color:#fff
    style EXT fill:#22c55e,stroke:#16a34a,stroke-width:2px,color:#fff
    style TEST fill:#22c55e,stroke:#16a34a,stroke-width:2px,color:#fff
    style PERF fill:#22c55e,stroke:#16a34a,stroke-width:2px,color:#fff
```

---

## 說明

### 顏色編碼
- 🔵 **藍色**: EventBus 核心組件
- 🟣 **紫色**: 事件基類和註冊相關
- 🟠 **橙色**: 領域實體 (發布者)
- 🔴 **紅色**: 訂單相關事件
- 🟡 **黃色**: 商品/庫存相關事件
- 🟢 **綠色**: 事件處理器 (訂閱者) / 成功狀態
- 🔷 **青色**: 異步處理
- 🟥 **粉紅色**: 決策節點

### 關係類型
- **實線箭頭 (→)**: 直接調用或數據流
- **虛線箭頭 (-.->)**: 訂閱關係或繼承關係
- **粗箭頭 (==>)**: 強調的關係 (如繼承、並行分發)

### 圖表說明
1. **核心架構圖**: 展示 EventBus 的整體架構和組件關係
2. **繼承層次圖**: 展示所有事件的繼承結構
3. **訂閱關係圖**: 清楚顯示哪個處理器訂閱哪些事件
4. **完整流程圖**: 展示訂單處理的完整事件流程
5. **內部工作流程**: 詳細展示 EventBus 內部的工作機制
6. **設計模式圖**: 展示使用的設計模式和實現技術
