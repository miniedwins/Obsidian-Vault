## DDD 中的分類層次

在 DDD 中,領域對象主要分為兩大類:

```
領域對象
├── Value Object (值對象)
│   └── Domain Primitive (值對象的特殊形式)
└── Entity (實體)
```

## 為什麼不是從屬關係?

**1. 本質特徵相反**

java

```java
// Domain Primitive - 無身份標識
Email email1 = new Email("user@example.com");
Email email2 = new Email("user@example.com");
// email1.equals(email2) == true (值相同就相等)

// Entity - 有身份標識
User user1 = new User(new UserId("123"), email1);
User user2 = new User(new UserId("456"), email2);
// user1.equals(user2) == false (ID 不同就不相等,即使 email 相同)
```

**2. 可變性相反**

- Domain Primitive: **必須不可變**
- Entity: **可以改變狀態**

java

```java
// Domain Primitive - 不可變
Email email = new Email("old@example.com");
// 無法修改,只能創建新的
Email newEmail = new Email("new@example.com");

// Entity - 可變
User user = new User(userId, email);
user.changeEmail(newEmail);  // 可以修改屬性
```

**3. 在 DDD 理論中的定位**

Eric Evans 在《Domain-Driven Design》中明確區分:

- **Value Objects** (包括 Domain Primitive):用值來定義的對象
- **Entities**:用唯一標識來定義的對象

這是兩個平行的概念,不是繼承關係。

## 它們的關係

Domain Primitive 和 Entity 是**組合關係**,而非繼承關係:

java

```java
public class User {  // Entity
    private UserId id;           // Domain Primitive
    private Email email;         // Domain Primitive
    private PhoneNumber phone;   // Domain Primitive
    private Money balance;       // Domain Primitive
}
```

Domain Primitive 通常作為 Entity 的**組成部分**,用來封裝 Entity 的屬性值和業務規則。