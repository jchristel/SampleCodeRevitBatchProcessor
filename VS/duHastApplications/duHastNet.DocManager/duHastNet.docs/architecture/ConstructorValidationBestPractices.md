# Constructor Parameter Validation Best Practices

## Overview
Constructor parameters should always be validated when they represent required dependencies. This is a fundamental defensive programming practice that prevents runtime errors and provides clear, actionable error messages.

---

## Why Constructor Validation is Important

### 1. **Fail Fast Principle**
Failing at construction time is vastly superior to failing later during execution.

**Without Validation (Bad):**
```csharp
public class DocumentImportService
{
    private readonly IUnitOfWork _unitOfWork;
    
    public DocumentImportService(IUnitOfWork unitOfWork)
    {
        _unitOfWork = unitOfWork; // No validation
    }
    
    public async Task ImportAsync(string filePath)
    {
        // Crashes here with cryptic NullReferenceException
        var documents = await _unitOfWork.Documents.GetAllAsync();
    }
}
```

**Error Message:**
```
System.NullReferenceException: Object reference not set to an instance of an object.
   at DocumentImportService.ImportAsync(String filePath) line 23
```

**With Validation (Good):**
```csharp
public class DocumentImportService
{
    private readonly IUnitOfWork _unitOfWork;
    
    public DocumentImportService(IUnitOfWork unitOfWork)
    {
        ArgumentNullException.ThrowIfNull(unitOfWork);
        _unitOfWork = unitOfWork;
    }
}
```

**Error Message:**
```
System.ArgumentNullException: Value cannot be null. (Parameter 'unitOfWork')
   at DocumentImportService..ctor(IUnitOfWork unitOfWork) line 12
```

**Benefits:**
- ✅ Error occurs immediately at construction
- ✅ Clear parameter name in error message
- ✅ Obvious what went wrong
- ✅ Easier to debug (stack trace points to constructor)
- ✅ Prevents object from entering invalid state

---

### 2. **Clear Error Messages**
Validation provides explicit, actionable error messages.

**Comparison:**

| Without Validation | With Validation |
|-------------------|-----------------|
| `NullReferenceException` | `ArgumentNullException` |
| "Object reference not set..." | "Value cannot be null. (Parameter 'unitOfWork')" |
| Error in method body | Error at construction |
| Unclear what's null | Explicit parameter name |
| Could be many things | Single, clear cause |

---

### 3. **Defensive Programming**
Constructor validation makes the contract explicit and enforces preconditions.

**Contract Documentation:**
```csharp
/// <summary>
/// Creates a new DocumentImportService
/// </summary>
/// <param name="unitOfWork">Unit of work for database operations (required)</param>
/// <exception cref="ArgumentNullException">Thrown when unitOfWork is null</exception>
public DocumentImportService(IUnitOfWork unitOfWork)
{
    ArgumentNullException.ThrowIfNull(unitOfWork);
    _unitOfWork = unitOfWork;
}
```

**Benefits:**
- Makes required dependencies explicit
- Documents preconditions
- Prevents invalid object state
- Enforces invariants from construction

---

### 4. **Consistency Across Codebase**
All services should follow the same validation pattern.

**Example from this Project:**
```csharp
// DatabaseService validates parameters
public async Task InitializeAsync(string databasePath)
{
    ArgumentNullException.ThrowIfNull(databasePath);
    
    if (string.IsNullOrEmpty(databasePath))
    {
        throw new ArgumentException("Database path cannot be null or empty.", nameof(databasePath));
    }
    // ... rest of method
}

// DocumentImportService should validate constructor parameters
public DocumentImportService(IUnitOfWork unitOfWork)
{
    ArgumentNullException.ThrowIfNull(unitOfWork);
    _unitOfWork = unitOfWork;
}
```

---

## Validation Rules

### When to Validate

✅ **Always Validate:**
- Constructor parameters that are dependencies
- Constructor parameters that are required for class operation
- Method parameters that cannot be null
- Method parameters with specific format requirements

❌ **Skip Validation:**
- Optional parameters with default values
- Parameters that are allowed to be null by design
- Internal/private methods where caller is trusted (use Debug.Assert instead)

---

## Validation Patterns

### 1. Required Object Parameters

```csharp
public MyService(IRepository repository, ILogger logger)
{
    ArgumentNullException.ThrowIfNull(repository);
    ArgumentNullException.ThrowIfNull(logger);
    
    _repository = repository;
    _logger = logger;
}
```

### 2. Required String Parameters

```csharp
public async Task ProcessFileAsync(string filePath)
{
    ArgumentNullException.ThrowIfNull(filePath);
    
    if (string.IsNullOrWhiteSpace(filePath))
    {
        throw new ArgumentException("File path cannot be empty or whitespace.", nameof(filePath));
    }
    
    // Process file...
}
```

### 3. Multiple Validations

```csharp
public DocumentImportService(
    IUnitOfWork unitOfWork,
    ILogger logger,
    IFileSystem fileSystem)
{
    ArgumentNullException.ThrowIfNull(unitOfWork);
    ArgumentNullException.ThrowIfNull(logger);
    ArgumentNullException.ThrowIfNull(fileSystem);
    
    _unitOfWork = unitOfWork;
    _logger = logger;
    _fileSystem = fileSystem;
}
```

### 4. Value Validation

```csharp
public void SetTimeout(int timeoutSeconds)
{
    if (timeoutSeconds <= 0)
    {
        throw new ArgumentOutOfRangeException(
            nameof(timeoutSeconds),
            timeoutSeconds,
            "Timeout must be greater than zero.");
    }
    
    _timeoutSeconds = timeoutSeconds;
}
```

---

## Modern C# Syntax

### ArgumentNullException.ThrowIfNull (C# 11+)

**Recommended (Modern):**
```csharp
public MyService(IRepository repository)
{
    ArgumentNullException.ThrowIfNull(repository);
    _repository = repository;
}
```

**Alternative (Older C# versions):**
```csharp
public MyService(IRepository repository)
{
    _repository = repository ?? throw new ArgumentNullException(nameof(repository));
}
```

**Legacy (Pre-C# 7):**
```csharp
public MyService(IRepository repository)
{
    if (repository == null)
    {
        throw new ArgumentNullException(nameof(repository));
    }
    _repository = repository;
}
```

---

## Testing Constructor Validation

### Test Pattern

```csharp
[Test]
public void Constructor_WithNullDependency_ThrowsArgumentNullException()
{
    // Arrange, Act & Assert
    var exception = Assert.Throws<ArgumentNullException>(
        () => new MyService(null));
    
    Assert.That(exception.ParamName, Is.EqualTo("dependency"));
}
```

### Test Coverage

For each constructor with N required parameters, you should have:
- 1 test for successful construction
- N tests for null validation (one per parameter)

**Example:**
```csharp
[TestFixture]
public class DocumentImportServiceTests
{
    [Test]
    public void Constructor_WithValidUnitOfWork_InitializesSuccessfully()
    {
        // Arrange
        var unitOfWork = new UnitOfWork(connection);
        
        // Act
        var service = new DocumentImportService(unitOfWork);
        
        // Assert
        Assert.That(service, Is.Not.Null);
    }
    
    [Test]
    public void Constructor_WithNullUnitOfWork_ThrowsArgumentNullException()
    {
        // Arrange, Act & Assert
        var exception = Assert.Throws<ArgumentNullException>(
            () => new DocumentImportService(null));
        
        Assert.That(exception.ParamName, Is.EqualTo("unitOfWork"));
    }
}
```

---

## Common Mistakes to Avoid

### ❌ Mistake 1: No Validation
```csharp
public MyService(IRepository repository)
{
    _repository = repository; // Missing validation
}
```

### ❌ Mistake 2: Wrong Exception Type
```csharp
public MyService(IRepository repository)
{
    if (repository == null)
    {
        throw new Exception("Repository is null"); // Use ArgumentNullException
    }
}
```

### ❌ Mistake 3: Validating After Assignment
```csharp
public MyService(IRepository repository)
{
    _repository = repository;
    ArgumentNullException.ThrowIfNull(repository); // Too late!
}
```

### ❌ Mistake 4: Missing Parameter Name
```csharp
public MyService(IRepository repository)
{
    if (repository == null)
    {
        throw new ArgumentNullException(); // Missing nameof(repository)
    }
}
```

---

## Exception Types Reference

| Scenario | Exception Type | Example |
|----------|---------------|---------|
| Null parameter | `ArgumentNullException` | `ArgumentNullException.ThrowIfNull(param)` |
| Empty string | `ArgumentException` | `throw new ArgumentException("Cannot be empty", nameof(param))` |
| Out of range value | `ArgumentOutOfRangeException` | `throw new ArgumentOutOfRangeException(nameof(param), value, "Must be > 0")` |
| Invalid format | `ArgumentException` | `throw new ArgumentException("Invalid format", nameof(param))` |
| Invalid state | `InvalidOperationException` | `throw new InvalidOperationException("Service not initialized")` |

---

## Real-World Examples from This Project

### Example 1: Service with Single Dependency
```csharp
public class DocumentExportService
{
    private readonly IUnitOfWork _unitOfWork;
    
    public DocumentExportService(IUnitOfWork unitOfWork)
    {
        ArgumentNullException.ThrowIfNull(unitOfWork);
        _unitOfWork = unitOfWork;
    }
}
```

### Example 2: Service with Multiple Dependencies
```csharp
public class Manager
{
    private readonly IDatabaseService _databaseService;
    private readonly ISettingsService _settingsService;
    
    public Manager(
        IDatabaseService databaseService,
        ISettingsService settingsService)
    {
        ArgumentNullException.ThrowIfNull(databaseService);
        ArgumentNullException.ThrowIfNull(settingsService);
        
        _databaseService = databaseService;
        _settingsService = settingsService;
    }
}
```

### Example 3: Method Parameter Validation
```csharp
public async Task InitializeAsync(string databasePath)
{
    ArgumentNullException.ThrowIfNull(databasePath);
    
    if (string.IsNullOrWhiteSpace(databasePath))
    {
        throw new ArgumentException(
            "Database path cannot be whitespace only.",
            nameof(databasePath));
    }
    
    // Ensure directory exists
    var directory = Path.GetDirectoryName(databasePath);
    if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
    {
        Directory.CreateDirectory(directory);
    }
    
    _connection = new SQLiteAsyncConnection(databasePath);
}
```

---

## Project Standards

### Constructor Validation Checklist

When creating a new class with dependencies:

- [ ] Validate all required constructor parameters
- [ ] Use `ArgumentNullException.ThrowIfNull()` for objects
- [ ] Use `ArgumentException` for strings with additional checks
- [ ] Validate before assignment
- [ ] Include parameter name in exceptions
- [ ] Write tests for each validation
- [ ] Document validation in XML comments
- [ ] Apply consistently across all service classes

---

## Benefits Summary

| Benefit | Impact |
|---------|--------|
| **Earlier Error Detection** | Fail at construction, not later in execution |
| **Clearer Error Messages** | Explicit parameter names, not generic NullReference |
| **Better Debugging** | Stack trace points to exact problem |
| **Code Documentation** | Makes requirements explicit |
| **Invalid State Prevention** | Objects can't exist in invalid state |
| **Testing Confidence** | Validates preconditions are enforced |
| **Professional Code** | Follows industry best practices |

---

## Quick Reference

**One-Line Pattern for Modern C#:**
```csharp
public MyService(IDependency dependency)
{
    ArgumentNullException.ThrowIfNull(dependency);
    _dependency = dependency;
}
```

**Test Pattern:**
```csharp
[Test]
public void Constructor_WithNullDependency_ThrowsArgumentNullException()
{
    Assert.Throws<ArgumentNullException>(() => new MyService(null));
}
```

---

## Conclusion

Constructor parameter validation is a simple, zero-cost practice that:
- Prevents bugs
- Improves error messages
- Documents requirements
- Follows industry standards
- Makes code more maintainable

**Rule of Thumb:** If a constructor parameter is required for the class to function, validate it immediately in the constructor before assignment.

---

## Additional Resources

- [ArgumentNullException Class (Microsoft Docs)](https://learn.microsoft.com/en-us/dotnet/api/system.argumentnullexception)
- [Defensive Programming Best Practices](https://en.wikipedia.org/wiki/Defensive_programming)
- [C# Coding Conventions (Microsoft)](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)
- [Clean Code by Robert C. Martin](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)
