### **(1) 基礎結構：介面抽象與適配**

```java
// 領域層的抽象介面（定義業務需要的契約）
public interface ExchangeRateService {
    ExchangeRate getExchangeRate(Currency source, Currency target);
}

// ACL 實現：封裝第三方服務細節
public class ExchangeRateServiceImpl implements ExchangeRateService {
    @Autowired
    private YahooForexService yahooForexService; // 外部依賴

    @Override
    public ExchangeRate getExchangeRate(Currency source, Currency target) {
        // 1. 參數轉換：將領域物件轉為第三方需要的格式
        String sourceCurrency = source.getValue();
        String targetCurrency = target.getValue();

        // 2. 呼叫外部服務
        BigDecimal forex = yahooForexService.getExchangeRate(sourceCurrency, targetCurrency);

        // 3. 結果轉換：將第三方回應轉為領域物件
        return new ExchangeRate(forex, source, target);
    }
}
```

#### **設計要點**

- **介面設計以業務為導向**：`ExchangeRateService` 使用領域物件（`Currency`），而非第三方特定的參數（如字串 `"USD"`）。
    
- **隱藏技術細節**：ACL 內部處理 Yahoo API 的呼叫與數據轉換，業務層無需感知。

### **(2) 進階功能：擴展 ACL 的能力**

ACL 不僅是簡單的代理，還能整合以下功能：

#### **① 快取（降低外部呼叫頻率）**

```java
public class ExchangeRateServiceImpl implements ExchangeRateService {
    private final Cache<CurrencyPair, ExchangeRate> cache; // Guava Cache 或 Redis

    @Override
    public ExchangeRate getExchangeRate(Currency source, Currency target) {
        CurrencyPair key = new CurrencyPair(source, target);
        return cache.get(key, () -> fetchFromYahoo(source, target)); // 快取邏輯封裝在 ACL
    }

    private ExchangeRate fetchFromYahoo(Currency source, Currency target) {
        // 實際呼叫 Yahoo API
    }
}
```

#### **② 兜底策略（容錯機制）**

```java
public ExchangeRate getExchangeRate(Currency source, Currency target) {
    try {
        return yahooForexService.getRate(source, target);
    } catch (ServiceUnavailableException e) {
        log.warn("Yahoo 服務不可用，使用上次成功快取");
        return cache.getLastSuccessfulRate(source, target); // 返回最近一次成功數據
    }
}
```

#### **③ 功能開關（動態切換實現）**

```java
public ExchangeRate getExchangeRate(Currency source, Currency target) {
    if (featureToggle.isEnabled("use_mock_exchange_rate")) {
        return new ExchangeRate(BigDecimal.ONE, source, target); // 測試用固定值
    }
    return yahooForexService.getRate(source, target);
}
```

#### **④ 監控與日誌**

```java
public ExchangeRate getExchangeRate(Currency source, Currency target) {
    long startTime = System.currentcurrentTimeMillis();
    try {
        ExchangeRate rate = yahooForexService.getRate(source, target);
        metrics.recordSuccess(source, target); // 記錄成功指標
        return rate;
    } catch (Exception e) {
        metrics.recordFailure(source, target); // 記錄失敗指標
        throw e;
    } finally {
        long duration = System.currentTimeMillis() - startTime;
        log.info("匯率查詢完成，耗時: {}ms", duration);
    }
}
```

## **3. ACL 的測試策略**

### **(1) 單元測試：Mock 外部依賴**

```java
@Test
void testGetExchangeRate() {
    // 1. 準備 Mock 行為
    YahooForexService mockService = mock(YahooForexService.class);
    when(mockService.getExchangeRate("USD", "CNY")).thenReturn(BigDecimal.valueOf(6.5));

    // 2. 注入 Mock 到 ACL
    ExchangeRateService service = new ExchangeRateServiceImpl(mockService);

    // 3. 驗證領域邏輯
    ExchangeRate rate = service.getExchangeRate(Currency.USD, Currency.CNY);
    assertEquals(6.5, rate.getRate().doubleValue());
}
```

### **(2) 整合測試：驗證真實第三方連線**

```java
@SpringBootTest
class ExchangeRateServiceIntegrationTest {
    @Autowired
    private ExchangeRateService service;

    @Test
    void testLiveYahooIntegration() {
        ExchangeRate rate = service.getExchangeRate(Currency.USD, Currency.CNY);
        assertNotNull(rate.getRate());
        assertTrue(rate.getRate().compareTo(BigDecimal.ZERO) > 0);
    }
}
```

## **4. ACL 與其他模式的協作**

### **(1) ACL + Domain Primitive**

- **`ExchangeRate` 和 `Currency` 是領域原語**，封裝業務規則（如匯率必須為正數）。
    
- ACL 負責將原始數據（如 Yahoo 返回的浮點數）轉換為這些高階物件。
    

### **(2) ACL + Repository**

- **Repository** 抽象資料庫存取，**ACL** 抽象外部服務，兩者共同保護領域層不受基礎設施影響。
    

### **(3) ACL + Strategy Pattern**

- 可動態切換不同的匯率來源（Yahoo、Fixer.io、Mock）：

```java
public interface ForexClient {
    BigDecimal getRate(String source, String target);
}

public class ExchangeRateServiceImpl implements ExchangeRateService {
    private final ForexClient forexClient; // 透過策略模式注入
}
```

## **5. 總結：ACL 的價值**

|問題|ACL 的解決方案|
|---|---|
|第三方 API 變更頻繁|變更僅限 ACL 內部，業務層不變|
|外部數據格式不符合領域模型|在 ACL 中轉換為領域物件|
|快取/兜底邏輯散落各處|集中到 ACL，便於維護與測試|
|難以模擬外部服務失敗場景|透過 Mock ACL 輕鬆測試異常流程|

**核心思想**：

> **「ACL 是領域層與外部世界的防火牆」**  
> 它讓核心業務邏輯保持純淨，同時靈活應對外部不確定性。