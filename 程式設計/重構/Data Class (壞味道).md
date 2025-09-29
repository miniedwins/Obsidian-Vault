### 核心概念：為什麼「只有資料的類別」通常是個問題？

在物件導向設計（Object-Oriented Programming, OOP）中，一個核心思想是 **「將資料與操作該資料的行為封裝在一起」**。這就像在現實世界中，一顆「籃球」不僅有重量、尺寸、顏色等**資料**，它本身也具備「彈跳」這個**行為**。你不會需要一個「籃球管理器」來幫籃球執行彈跳的動作。

「Data Class」的壞味道就出現在這裡：它打破了這個核心思想。它就像一顆只有重量和尺寸資料，但自己不會彈跳的籃球。

**問題點分析：**

1. **行為與資料分離 (Increased Coupling)：** 當你把操作資料的邏輯（行為）放在另一個完全不相關的類別時（例如，一個 `Manager` 或 `Service` 類別），這兩個類別就產生了緊密的**耦合**。如果未來 `Data Class` 的內部資料結構改變了（例如，欄位名稱變了、型別換了），那個遠在天邊的 `Manager` 類別也必須跟著修改。這會讓程式碼變得脆弱且難以維護。
    
2. **貧血的領域模型 (Anemic Domain Model)：** 這些只有 `getter` 和 `setter` 的 `Data Class`，我們稱之為「貧血物件」。它們本身沒有任何商業邏輯，只是一個資料的容器。真正的商業邏輯四散在各種「服務」或「工具」類別中，導致物件導向的優勢（如封裝、內聚）蕩然無存，寫起來更像是在寫傳統的程序式程式碼。
    
3. **職責不清：** 物件本身應該最清楚如何處理自己的資料。把行為外移，等於是讓物件將自己的責任推給別人，這違反了物件導向中「高內聚、低耦合」的設計原則。
    

---

### 範例解說

讓我們用一個簡單的「訂單」例子來看看好與壞的設計。

#### 👎 不好的範例 (Bad Example - Data Class)

在這個範例中，`Order` 類別就只是一個資料容器，完全沒有自己的行為。所有的商業邏輯，例如計算總金額，都被放在一個叫做 `OrderService` 的外部類別中。

Java

```java
// 這是一個 Data Class，只有欄位和 get/set 方法
// 它就像一個不會思考的資料袋
public class Order {
    private String customerName;
    private double price;
    private int quantity;
    private double discountRate;

    // A series of getters and setters...
    public double getPrice() {
        return price;
    }

    public void setPrice(double price) {
        this.price = price;
    }

    public int getQuantity() {
        return quantity;
    }

    public void setQuantity(int quantity) {
        this.quantity = quantity;
    }

    public double getDiscountRate() {
        return discountRate;
    }

    public void setDiscountRate(double discountRate) {
        this.discountRate = discountRate;
    }
    // ... other getters and setters
}

// 商業邏輯被放在一個外部的 "Service" 類別
// 它從 Order 物件中取出資料，進行計算，然後再回傳結果
public class OrderService {
    public double calculateTotalPrice(Order order) {
        // 從 Order 物件 "拉" 出所有需要的資料
        double basePrice = order.getPrice() * order.getQuantity();
        double discount = basePrice * order.getDiscountRate();
        
        // 在外部進行所有的商業邏輯計算
        return basePrice - discount;
    }
}

// 在主程式中如何使用：
public class Main {
    public static void main(String[] args) {
        Order myOrder = new Order();
        myOrder.setPrice(100.0);
        myOrder.setQuantity(5);
        myOrder.setDiscountRate(0.1); // 10% 折扣

        OrderService service = new OrderService();
        double totalPrice = service.calculateTotalPrice(myOrder); // 需要一個外部服務來幫忙計算

        System.out.println("Total price: " + totalPrice); // 輸出 450.0
    }
}
```

**這個範例的問題點：**

- `OrderService` 嚴重依賴 `Order` 的內部實作。如果 `Order` 類別未來決定把 `discountRate` 改成 `discountPercentage`，`OrderService` 就必須跟著修改。
    
- `Order` 類別本身是「貧血」的，它對自己的資料一無所知，無法執行任何有意義的行為。
    

---

#### 👍 好的範例 (Good Example - Refactored)

現在，我們使用 **Move Method** 的重構技巧，將計算總金額的行為 (`calculateTotalPrice`) 從 `OrderService` **搬移**到 `Order` 類別內部。讓 `Order` 自己負責自己的事情。

Java

```java
// 這是一個擁有資料和行為的 "豐富" 物件
public class Order {
    private String customerName;
    private double price;
    private int quantity;
    private double discountRate;

    public Order(double price, int quantity, double discountRate) {
        this.price = price;
        this.quantity = quantity;
        this.discountRate = discountRate;
    }
    
    // 行為與資料封裝在一起！
    // 讓 Order 物件自己告訴我們它的總價是多少
    public double getTotalPrice() {
        double basePrice = this.price * this.quantity;
        double discount = basePrice * this.discountRate;
        return basePrice - discount;
    }

    // 我們甚至可以隱藏 set 方法，讓物件狀態更穩定
    // ... 其他必要的 public 方法
}

// 在主程式中如何使用：
public class Main {
    public static void main(String[] args) {
        // 物件在建立時就確保了資料的完整性
        Order myOrder = new Order(100.0, 5, 0.1);

        // 我們直接 "詢問" 訂單物件它的總價是多少，而不是去請別人幫忙算
        double totalPrice = myOrder.getTotalPrice(); 

        System.out.println("Total price: " + totalPrice); // 輸出 450.0
    }
}
```

**這個範例的優點：**

- **高內聚 (High Cohesion):** `Order` 類別同時包含了訂單資料和與訂單相關的計算邏輯，職責單一且清晰。
    
- **低耦合 (Low Coupling):** 不再需要 `OrderService` 這個類別了。其他程式碼想知道訂單總價，只需要跟 `Order` 物件互動即可，不用關心內部是如何計算的。
    
- **封裝 (Encapsulation):** 我們可以把 `price`, `quantity` 等欄位的 `setter` 拿掉，讓外部程式無法隨意竄改訂單的內部狀態，使得物件更加健壯。
    

---

### 何時「只有資料的類別」是可接受的？

正如原文所提，不是所有只有資料的類別都是壞味道。關鍵在於它 **「是否搭配了一個放在其他地方的相關行為」**。

以下是常見且合理的使用情境：

1. **DTO (Data Transfer Object - 資料傳輸物件):**
    
    - **用途：** 它的唯一目的就是在不同層級或系統之間傳遞資料。例如，後端從資料庫讀取了複雜的資料後，組裝成一個簡單的 DTO 物件，然後序列化成 JSON 格式回傳給前端。
        
    - **為什麼合理：** 因為它的生命週期很短，且職責就是「傳輸」。前端拿到這個資料後，會在前端的邏輯中進行處理，後端傳完就沒它的事了。它本身不需要包含後端的商業邏輯。硬塞一個行為給它反而奇怪。
        
    
    Java
    
    ```java
    // 一個用來回傳給前端的 DTO
    public class UserProfileDTO {
        private String username;
        private String email;
        private String lastLoginTime; // 格式化好的字串
        // 只有 getters
    }
    ```
    
2. **CQRS (命令查詢職責分離) 中的查詢模型：**
    
    - **用途：** 在 CQRS 架構中，「查詢 (Query)」的職責就是專門為了某個特定的顯示需求（例如，一個複雜的報表頁面），從多個資料來源抓取資料並組合成一個「唯讀」的物件。
        
    - **為什麼合理：** 這個查詢模型是高度客製化的，它存在的唯一目的就是滿足那個頁面的顯示需求。它不需要有任何改變自己狀態的「命令 (Command)」行為，因為它只是資料的呈現，而不是核心的業務實體 (Entity)。
        

總結來說，判斷一個「只有資料的類別」是否為壞味道的關鍵問題是：

> **「有沒有一些本應屬於這個類別的商業邏輯，卻被寫在其他地方了？」**

如果答案是 **Yes**，那麼它很可能就是一個 Data Class 壞味道，你應該考慮將那些外部的邏輯搬移回來。 如果答案是 **No**，它只是一個單純的資料載體（如 DTO），那麼它就是一個合理且正常的設計模式。