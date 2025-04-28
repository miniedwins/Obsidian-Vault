## **1. 為什麼需要中介軟體 ACL？**

### **問題場景**

- **膠水程式碼散落**：業務邏輯中充斥著 Kafka/RabbitMQ 的序列化、Topic 管理、錯誤處理等重複程式碼。

```java
// 反例：業務程式碼直接依賴 KafkaTemplate
@Service
public class TransferService {
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;

    public void transfer(Account source, Account target, Money money) {
        // 業務邏輯
        String message = source.getId() + "," + target.getId() + "," + money.getValue();
        kafkaTemplate.send("audit_topic", message); // 膠水程式碼入侵業務
    }
}
```

- **難以替換中介軟體**：若從 Kafka 切換到 RabbitMQ，需修改所有直接呼叫 Kafka 的程式碼。
    
- **序列化邏輯耦合**：業務物件與 JSON/String 轉換邏輯分散在各處。
    

### **ACL 的解決方案**

1. **統一抽象介面**：定義業務語意的 `AuditMessageProducer`，隱藏 Kafka 細節。
    
2. **集中管理序列化**：在 ACL 層處理 `AuditMessage` ↔ `String` 的轉換。
    
3. **隔離技術細節**：未來更換中介軟體時，只需修改 ACL 實現。

## **2. ACL 核心設計與實作**

### **(1) 定義領域物件（Domain Primitive）**

封裝審計訊息的業務含義，並內建序列化邏輯：

```java
@Value
public class AuditMessage {
    private UserId userId;
    private AccountNumber source;
    private AccountNumber target;
    private Money money;
    private Instant timestamp;

    // 領域層的序列化邏輯（集中管理）
    public String serialize() {
        return String.join(",",
            userId.getValue(),
            source.getValue(),
            target.getValue(),
            money.toString(),
            timestamp.toString()
        );
    }

    public static AuditMessage deserialize(String raw) {
        String[] parts = raw.split(",");
        return new AuditMessage(
            new UserId(parts[0]),
            new AccountNumber(parts[1]),
            new AccountNumber(parts[2]),
            Money.parse(parts[3]),
            Instant.parse(parts[4])
        );
    }
}
```

### **(2) 抽象中介軟體介面**

業務層只依賴抽象的 `AuditMessageProducer`：

```java
public interface AuditMessageProducer {
    SendResult send(AuditMessage message); // 使用領域物件，非 String/Byte[]
}
```

### **(3) 實現 Kafka ACL**

在基礎設施層實現介面，封裝技術細節：

```java
public class KafkaAuditMessageProducer implements AuditMessageProducer {
    private static final String AUDIT_TOPIC = "audit_log";

    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;

    @Override
    public SendResult send(AuditMessage message) {
        try {
            String payload = message.serialize();
            kafkaTemplate.send(AUDIT_TOPIC, payload);
            return SendResult.success();
        } catch (Exception e) {
            throw new AuditMessageSendException("Kafka 發送失敗", e);
        }
    }
}
```

## **3. 業務層的乾淨呼叫**

業務程式碼不再感知 Kafka，只需操作領域物件：

```java
@Service
public class TransferService {
    @Autowired
    private AuditMessageProducer auditMessageProducer; // 依賴抽象

    public void transfer(Account source, Account target, Money money) {
        // 業務邏輯
        AuditMessage message = new AuditMessage(
            currentUserId(),
            source.getNumber(),
            target.getNumber(),
            money,
            Instant.now()
        );
        auditMessageProducer.send(message); // 語意清晰的呼叫
    }
}
```

## **4. ACL 的進階功能擴展**

### **(1) 錯誤處理與重試**

在 ACL 內集中實現：

```java
public SendResult send(AuditMessage message) {
    try {
        String payload = message.serialize();
        kafkaTemplate.send(AUDIT_TOPIC, payload).get(3, TimeUnit.SECONDS); // 同步等待
        return SendResult.success();
    } catch (TimeoutException e) {
        log.warn("Kafka 超時，觸發重試...");
        return retrySend(message); // 封裝重試邏輯
    }
}
```

### **(2) 日誌與監控**

```java
public SendResult send(AuditMessage message) {
    long startTime = System.currentTimeMillis();
    try {
        String payload = message.serialize();
        kafkaTemplate.send(AUDIT_TOPIC, payload);
        metrics.recordSuccess();
        return SendResult.success();
    } catch (Exception e) {
        metrics.recordFailure();
        throw e;
    } finally {
        log.info("審計日誌發送耗時: {}ms", System.currentTimeMillis() - startTime);
    }
}
```

### **(3) 功能開關與 Mock**

```java
@Profile("test")
public class MockAuditMessageProducer implements AuditMessageProducer {
    @Override
    public SendResult send(AuditMessage message) {
        log.info("測試模式：模擬發送審計日誌 -> {}", message);
        return SendResult.success();
    }
}
```

---

## **5. 測試策略**

### **(1) 單元測試：Mock ACL**

```java
@Test
void testTransferWithAudit() {
    // 1. 準備 Mock Producer
    AuditMessageProducer mockProducer = mock(AuditMessageProducer.class);
    TransferService service = new TransferService(mockProducer);

    // 2. 執行業務邏輯
    service.transfer(sourceAccount, targetAccount, Money.of(100));

    // 3. 驗證 ACL 互動
    ArgumentCaptor<AuditMessage> captor = ArgumentCaptor.forClass(AuditMessage.class);
    verify(mockProducer).send(captor.capture());
    assertEquals(100, captor.getValue().getMoney().getValue());
}
```

### **(2) 整合測試：驗證真實 Kafka**

```java
@SpringBootTest
class KafkaAuditMessageProducerTest {
    @Autowired
    private AuditMessageProducer producer;

    @Test
    void testRealKafkaSend() {
        AuditMessage message = new AuditMessage(...);
        SendResult result = producer.send(message);
        assertTrue(result.isSuccess());
    }
}
```

## **6. 總結：中介軟體 ACL 的價值**

|問題|ACL 的解決方案|
|---|---|
|業務程式碼混雜序列化邏輯|集中到 `AuditMessage.serialize()`|
|直接依賴 Kafka/RabbitMQ API|透過介面隱藏實現細節|
|難以替換中介軟體|只需新增一個 ACL 實現（如 `RabbitMQAuditMessageProducer`）|
|分散的錯誤處理與監控|在 ACL 內統一封裝|

**核心思想**：

> **「中介軟體 ACL 是業務與技術基礎設施之間的緩衝層」**  
> 它讓業務程式碼只關心 **「做什麼」**（發送審計日誌），而非 **「怎麼做」**（Kafka 的 Topic 或序列化）。