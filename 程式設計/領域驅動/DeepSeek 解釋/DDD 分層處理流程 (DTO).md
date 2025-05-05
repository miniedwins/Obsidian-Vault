
![[Pasted image 20250506064601.png]]

### 關鍵角色職責：

1. **Controller**
    
    - 只做三件事：
        
        - 接收 HTTP 請求，解析為 DTO。
            
        - 呼叫 **Application Service**（傳入 DTO）。
            
        - 將 Application Service 返回的 DTO 轉為 HTTP 回應。

```java
@RestController
public class AccountController {
    private final TransferService transferService; // Application Service

    @PostMapping("/transfer")
    public ResponseEntity<TransferResponseDTO> transfer(@RequestBody TransferRequestDTO dto) {
        TransferResponseDTO result = transferService.executeTransfer(dto);
        return ResponseEntity.ok(result);
    }
}
```

**Application Service**

- 協調流程的核心層：
    
    - 透過 **DTO Assembler** 將 DTO 轉為 Domain Model。
        
    - 呼叫 **Domain Service** 執行業務邏輯。
        
    - 處理事務、日誌等橫切關注點。

```java
@Service
public class TransferServiceImpl implements TransferService {
    private final TransferDTOAssembler assembler;
    private final AccountTransferService domainService; // Domain Service

    @Override
    public TransferResponseDTO executeTransfer(TransferRequestDTO dto) {
        // DTO → Domain Model
        TransferCommand command = assembler.toCommand(dto);
        
        // 呼叫領域服務
        domainService.transfer(command);
        
        // 返回 DTO
        return assembler.toResponseDTO(command);
    }
}
```

**DTO Assembler**

- 專職對象轉換：
    
    - 不包含業務邏輯，僅做欄位對應。
        
    - 可處理 1 個 DTO ↔ N 個 Domain Model 的複雜轉換。

```java
public class TransferDTOAssembler {
    public TransferCommand toCommand(TransferRequestDTO dto) {
        return new TransferCommand(
            new AccountId(dto.getSourceAccountId()),
            new AccountNumber(dto.getTargetAccountNumber()),
            new Money(dto.getAmount(), dto.getCurrency())
        );
    }
}
```

**Domain Service**

- 純業務邏輯：
    
    - 只接受 Domain Model（如 `Account`, `Money`）。
        
    - 完全不知道 DTO 或外部技術細節。

```java
public class AccountTransferService {
    public void transfer(TransferCommand command) {
        // 純領域邏輯，例如檢查餘額、計算手續費
    }
}
```

### 為什麼 Controller 不能直接轉換和呼叫 Domain Service？

1. **破壞單一職責原則**
    
    - Controller 應專注於 HTTP 協定處理，混入轉換邏輯會導致代碼膨脹。
        
2. **領域層污染風險**
    
    - 若 Domain Service 直接接受 DTO，會強制領域層感知外部數據結構，違反 DDD 的「領域層獨立性」。
        
3. **難以維護**
    
    - DTO 結構變更時，若轉換邏輯散落在多個 Controller，修改成本高。

### 常見錯誤案例與修正：

#### ❌ 錯誤做法（Controller 直接轉換 + 呼叫 Domain Service）：

```java
@Controller
public class BadAccountController {
    private final AccountTransferService domainService;

    @PostMapping("/transfer")
    public void transfer(@RequestBody TransferRequestDTO dto) {
        // Controller 自行轉換 DTO → Domain Model
        TransferCommand command = new TransferCommand(
            new AccountId(dto.getSourceAccountId()),
            new AccountNumber(dto.getTargetAccountNumber()),
            new Money(dto.getAmount(), dto.getCurrency())
        );
        
        // 直接呼叫 Domain Service
        domainService.transfer(command);
    }
}
```

**問題**：

- Controller 承擔了 Application Service 的職責。
    
- 無法統一處理事務、日誌等橫切邏輯。


#### ✅ 正確做法（透過 Application Service 協調）：

```java
@Controller
public class GoodAccountController {
    private final TransferService applicationService; // 依賴 Application Service

    @PostMapping("/transfer")
    public ResponseEntity<TransferResponseDTO> transfer(@RequestBody TransferRequestDTO dto) {
        TransferResponseDTO response = applicationService.executeTransfer(dto);
        return ResponseEntity.ok(response);
    }
}
```

### 總結：

- **Controller**：HTTP 介面適配，不碰 Domain Model。
    
- **Application Service**：協調轉換與流程，是唯一能同時看到 DTO 和 Domain Model 的層。
    
- **Domain Service**：只處理純業務邏輯，完全隔離技術細節。
    

嚴格遵守此分層，才能保持領域層的純淨與系統的可維護性！