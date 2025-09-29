### 1. Primitive Obsession (基本型別執著)

#### 說明

**基本型別執著** 指的是過度使用程式語言內建的基本型別 (如 `int`, `String`, `double`, `boolean` 等) 來表示具有特定業務意義或領域概念的資料。

您提供的說明非常貼切：「它們沒有物理意義、不具商業邏輯、沒有行為」。一個 `String` 就只是一個字串，它本身並不知道自己代表的是一個「電子郵件地址」、「電話號碼」還是一本書的「ISBN 編號」。當我們用基本型別來表示這些概念時，會產生以下問題：

1. **喪失業務意義 (Loss of Domain Knowledge)**：程式碼的意圖變得模糊。一個 `String email` 變數，只有命名可以提示它是個 Email，但編譯器本身無法保證它的格式正確。
    
2. **缺乏驗證機制 (Lack of Validation)**：任何字串都可以被賦值給 `email` 變數，例如 `"這不是一個email"`。驗證邏輯必須在使用它的地方手動添加，而且很容易在多處重複。
    
3. **缺少專屬行為 (No Encapsulated Behavior)**：如果我想從一個 Email 字串中獲取它的「域名」(Domain)，我必須另外寫一個外部的輔助函式 (utility function) 來處理，而不是讓 `email` 物件自己提供這個行為。
    

#### 範例：表示「金額」

我們用一個簡單的「金額」概念來說明。

##### 👎 不好的範例 (Primitive Obsession)

在這裡，我們用 `double` 來表示錢。

Java

```java
public class BadTransaction {

    // 使用基本型別 double 來表示金額
    public void processPayment(double amount, String currency) {
        if (amount < 0) {
            System.out.println("錯誤：金額不能是負數！");
            return;
        }

        // 假設 currency 總是 "TWD"
        System.out.println("處理支付：" + amount + " " + currency);
        // ... 其他商業邏輯
    }

    public static void main(String[] args) {
        BadTransaction transaction = new BadTransaction();
        
        // 這裡可以傳入任何 double 值，即使它沒有意義
        transaction.processPayment(-150.5, "TWD"); // 驗證邏輯分散在 processPayment 方法裡
        transaction.processPayment(100.0, "USD"); // 可能會忘記處理匯率轉換
    }
}
```

**問題點：**

- `double` 無法阻止傳入負數，驗證邏輯 (`if (amount < 0)`) 必須寫在 `processPayment` 方法內部。如果還有另一個方法 `refundPayment` 也需要處理金額，就可能要重複寫一次驗證。
    
- `double` 有浮點數精度問題，不適合用來做精確的貨幣計算。
    
- 「金額」和「貨幣單位」是兩個獨立的參數，它們之間的關係沒有被強制綁定。
    

##### 👍 好的範例 (使用 Value Object)

我們創建一個 `Money` 類別來封裝這個概念，解決 Primitive Obsession 的問題。

Java

```java
// 一個「值物件」(Value Object) 來代表金額
public class Money {
    private final double value;
    private final String currency;

    public Money(double value, String currency) {
        if (value < 0) {
            throw new IllegalArgumentException("金額不能是負數");
        }
        if (currency == null || currency.trim().isEmpty()) {
            throw new IllegalArgumentException("必須提供貨幣單位");
        }
        this.value = value;
        this.currency = currency;
    }

    public double getValue() {
        return value;
    }

    public String getCurrency() {
        return currency;
    }

    // 專屬行為：例如增加金額
    public Money add(Money other) {
        if (!this.currency.equals(other.currency)) {
            // 為了範例簡化，先不處理匯率轉換
            throw new IllegalArgumentException("不同貨幣無法直接相加");
        }
        return new Money(this.value + other.value, this.currency);
    }

    @Override
    public String toString() {
        return value + " " + currency;
    }
}

// 使用 Money 物件的交易類別
public class GoodTransaction {

    public void processPayment(Money amount) {
        // 不需要再做負數檢查，因為在 Money 物件創建時就保證了
        System.out.println("處理支付：" + amount);
        // ... 其他商業邏輯
    }

    public static void main(String[] args) {
        GoodTransaction transaction = new GoodTransaction();
        
        try {
            Money payment = new Money(500.0, "TWD");
            transaction.processPayment(payment);

            // 下面這行在創建時就會直接拋出異常，防止無效資料進入系統核心
            Money invalidPayment = new Money(-150.5, "TWD"); 
            // transaction.processPayment(invalidPayment); // 這行根本不會執行到

        } catch (IllegalArgumentException e) {
            System.out.println("創建物件失敗：" + e.getMessage());
        }
    }
}
```

**優點：**

1. **意義明確**：`Money` 這個型別清楚地表達了它的商業意涵。
    
2. **驗證集中**：所有關於 `Money` 的驗證規則 (如不能是負數) 都封裝在 `Money` 的建構子裡，確保任何一個 `Money` 物件都是有效的。
    
3. **行為封裝**：我們可以為 `Money` 加上專屬的行為，例如 `add()`。
    

---

### 2. Data Clump (資料泥團)

#### 說明

**資料泥團** 指的是一組經常「形影不離」的變數。它們可能出現在多個類別的成員變數中，或是多個方法的參數列表裡。

就像您引用的：「...就像小孩子，喜歡成群結隊地待在一塊兒」。看到 `startX`, `startY`, `endX`, `endY` 一起出現，或是 `name`, `address`, `phoneNumber` 一起出現，就應該警覺到可能存在一個被遺漏的「概念」。這個被遺漏的概念，正是將這些資料泥團重構成一個物件的好機會。

**壞處：**

1. **參數列表過長**：如 Uncle Bob 所言，過長的參數列表增加了方法的複雜度，也容易發生傳錯參數順序的錯誤 (例如把 `y` 傳到 `x` 的位置)。
    
2. **重複程式碼**：如果你需要新增一個 `z` 座標，你就必須去修改所有用到 `x` 和 `y` 的地方，在每個方法的參數列表都加上 `z`。
    
3. **隱藏了應有的抽象**：這群資料之所以總是在一起，正是因為它們共同構成了一個更高層次的抽象概念 (例如 `x` 和 `y` 組成了「座標點」)。
    

#### 範例：繪製幾何圖形

##### 👎 不好的範例 (Data Clump)

`x` 和 `y` 這對資料泥團在參數中不斷出現。

Java

```java
public class BadGeometryDrawer {

    // 參數裡有一組 (x, y) 代表圓心
    public void drawCircle(double centerX, double centerY, double radius) {
        System.out.println(
            "繪製圓形：圓心 (" + centerX + ", " + centerY + ")，半徑 " + radius
        );
    }

    // 參數裡有兩組 (x, y)，代表起點和終點
    public void drawLine(double startX, double startY, double endX, double endY) {
        System.out.println(
            "繪製線段：從 (" + startX + ", " + startY + ") 到 (" + endX + ", " + endY + ")"
        );
    }

    public static void main(String[] args) {
        BadGeometryDrawer drawer = new BadGeometryDrawer();
        drawer.drawCircle(10.0, 20.0, 5.0);
        drawer.drawLine(10.0, 20.0, 50.0, 60.0);
    }
}
```

**問題點：**

- `drawCircle` 和 `drawLine` 的參數列表都很長。
    
- `centerX` 和 `centerY` 這組資料泥團，以及 `startX` 和 `startY` 這另一組，其實都代表同一個概念：「二維座標點」。
    

##### 👍 好的範例 (提煉成類別)

我們將 `(x, y)` 這組資料泥團提煉成一個 `Point` 類別。

Java

```java
// 將資料泥團 (x, y) 提煉成一個類別
public class Point {
    private final double x;
    private final double y;

    public Point(double x, double y) {
        this.x = x;
        this.y = y;
    }

    public double getX() { return x; }
    public double getY() { return y; }
    
    @Override
    public String toString() {
        return "(" + x + ", " + y + ")";
    }
}

public class GoodGeometryDrawer {
    
    // 參數變得簡潔且富有意義
    public void drawCircle(Point center, double radius) {
        System.out.println("繪製圓形：圓心 " + center + "，半徑 " + radius);
    }

    // 參數從 4 個變成了 2 個
    public void drawLine(Point start, Point end) {
        System.out.println("繪製線段：從 " + start + " 到 " + end);
    }

    public static void main(String[] args) {
        GoodGeometryDrawer drawer = new GoodGeometryDrawer();
        
        Point center = new Point(10.0, 20.0);
        drawer.drawCircle(center, 5.0);
        
        Point start = new Point(10.0, 20.0);
        Point end = new Point(50.0, 60.0);
        drawer.drawLine(start, end);
    }
}
```

**優點：**

1. **可讀性提升**：`drawCircle(Point center, ...)` 比 `drawCircle(double centerX, double centerY, ...)` 更能表達意圖。
    
2. **參數減少**：方法簽名變得更簡潔，降低了呼叫時出錯的機率。
    
3. **程式碼更穩固**：如果未來需要增加 `z` 座標變成 3D，我們只需要修改 `Point` 類別，而 `drawCircle` 和 `drawLine` 的方法簽名可能完全不需要改變。
    

---

### 難兄難弟：互為因果的關係

您說的「互為因果」非常精準。這兩個壞味道的關係如下：

1. **Primitive Obsession 導致 Data Clump**： 當你使用基本型別來表示一個更複雜的概念時 (Primitive Obsession)，例如用 `double lat`, `double lon` 來表示「地理座標」，你就**被迫**在所有需要「地理座標」的地方，都必須同時傳遞 `lat` 和 `lon` 這兩個參數。這就自然而然地形成了 Data Clump。
    
2. **解決 Data Clump 的方法常常是解決 Primitive Obsession**： 當你發現 `lat` 和 `lon` 總是一起出現 (Data Clump)，最好的解決方案就是問自己：「這群資料共同代表了什麼概念？」答案是「地理座標」(Geolocation)。於是你創建一個 `Geolocation` 類別來封裝 `lat` 和 `lon`。這個動作不僅解決了 Data Clump，同時也消除了用基本型別 `double` 來表示複雜概念的 Primitive Obsession。
    

**總結來說，辨識出 Data Clump 是發現 Primitive Obsession 的一個重要線索。而解決 Primitive Obsession 的主要手段——也就是創建一個新的類別來封裝概念——也正是消除 Data Clump 的標準方法。**

透過將這些基本型別和資料泥團重構成有意義的物件，我們的程式碼會變得更加物件導向、更具表達力、也更容易維護。