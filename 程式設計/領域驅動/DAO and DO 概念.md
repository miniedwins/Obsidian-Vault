### **1. DO (Data Object) → 就是「純資料」的容器**

- **本質**：DO 是一個單純的「資料結構」，用來「承載資料」，**沒有任何行為**（方法）。
    
- **用途**：在程式內部傳遞資料，例如從資料庫讀取的「一筆記錄」或 API 收到的「請求參數」。
    
- **別名**：有些框架或團隊也會稱它為：
    
    - **POJO (Plain Old Java Object)**
        
    - **Entity (實體)**
        
    - **Model (模型)**
        

#### **🌰 舉例：一個「用戶」的 DO**

```java
// UserDO.java (DO 只包含資料，沒有邏輯)
public class UserDO {
    private Long id;
    private String name;
    private String email;
    
    // 只有 getter/setter，沒有其他方法！
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    // ... (其他 getter/setter)
}
```

### **2. DAO (Data Access Object) → 就是「操作資料庫」的介面**

- **本質**：DAO 是一個「抽象層」，**封裝所有對資料庫的操作**（如 CRUD）。
    
- **用途**：讓業務邏輯層「不需要知道資料庫細節」，只需呼叫 DAO 的方法。
    
- **關鍵特性**：
    
    - **依賴 DO**：所有方法的輸入/輸出都是 DO 或 DO 的集合（例如 `List<UserDO>`）。
        
    - **可替換實現**：DAO 是介面，底層可以用 MySQL、PostgreSQL 甚至 Mock 資料實現。
        

#### **🌰 舉例：一個「用戶」的 DAO**

```java
// UserDAO.java (DAO 只定義操作，不關心具體實現)
public interface UserDAO {
    // 插入一筆用戶資料（參數和返回值都是 UserDO）
    void insert(UserDO user);
    
    // 根據 ID 查詢用戶
    UserDO findById(Long id);
    
    // 更新用戶資料
    void update(UserDO user);
    
    // 刪除用戶
    void delete(Long id);
}
```

#### **DAO 的具體實現（MySQL 版）**

```java
// UserDAOMySQLImpl.java (實際操作 MySQL)
public class UserDAOMySQLImpl implements UserDAO {
    @Override
    public void insert(UserDO user) {
        String sql = "INSERT INTO users (name, email) VALUES (?, ?)";
        // 執行 SQL，並將 user.getName() 和 user.getEmail() 綁定到參數
    }
    
    @Override
    public UserDO findById(Long id) {
        String sql = "SELECT * FROM users WHERE id = ?";
        // 執行 SQL，將結果轉換成 UserDO 物件返回
    }
    // ... (其他方法實現)
}
```

### **3. 為什麼要分 DAO 和 DO？**

#### **✅ 分層清晰，職責分離**

- **DO** 只負責「攜帶資料」，不關心怎麼存儲或查詢。
    
- **DAO** 只負責「操作資料庫」，不關心資料怎麼被使用。
    

#### **✅ 更換資料庫時，只需改 DAO 實現**

例如：

- 今天用 **MySQL** → 寫 `UserDAOMySQLImpl`。
    
- 明天換 **MongoDB** → 寫 `UserDAOMongoDBImpl`，但業務邏輯層**不用改**（因為它依賴的是 `UserDAO` 介面）。
    

#### **✅ 方便單元測試**

- 測試業務邏輯時，可以用 **Mock DAO** 代替真實資料庫，避免依賴外部系統。

### **4. 實際程式碼流程範例**

```java
// 業務邏輯層（例如 Service）
public class UserService {
    private UserDAO userDAO;  // 依賴 DAO 介面
    
    // 新增用戶
    public void addUser(String name, String email) {
        UserDO user = new UserDO();
        user.setName(name);
        user.setEmail(email);
        userDAO.insert(user);  // 呼叫 DAO 存儲資料
    }
    
    // 查詢用戶
    public UserDO getUser(Long id) {
        return userDAO.findById(id);  // 透過 DAO 取得資料
    }
}
```

### **5. 常見混淆點**

#### **🚫 DAO vs. Repository**

- **DAO**：偏底層，直接對應資料庫操作（如 SQL）。
    
- **Repository**：偏業務，可能合併多個 DAO 的操作（例如「訂單 + 用戶」聯合查詢）。
    

#### **🚫 DO vs. DTO (Data Transfer Object)**

- **DO**：對應資料庫的結構（如 `users` 表的欄位）。
    
- **DTO**：對應 API 傳輸的結構（可能組合多個 DO 的資料，或省略敏感欄位）。


### **總結**

|概念|角色|特點|範例|
|---|---|---|---|
|**DO**|資料容器|只有欄位和 getter/setter|`UserDO`、`ProductDO`|
|**DAO**|資料庫操作介面|封裝 CRUD 方法，輸入輸出都是 DO|`UserDAO.insert(user)`|

這樣的分層設計讓程式更容易維護、擴充和測試！