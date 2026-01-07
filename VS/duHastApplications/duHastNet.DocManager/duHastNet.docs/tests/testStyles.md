# Test Style Guide

## Overview
This guide defines the testing standards for the duHastNet.DocManager project. All tests should follow these conventions to maintain consistency, readability, and maintainability.

## General Principles

### Framework and Tooling
- Use **NUnit** as the testing framework
- Use **Moq** for mocking dependencies in ViewModel and service tests
- Use **SQLite-NET-PCL** ORM for all database operations in tests
- Tests should be deterministic and repeatable
- Each test should be independent and not rely on other tests

### Mocking with Moq

#### Critical Rule: Methods with Optional Parameters
**IMPORTANT:** Moq's expression trees cannot handle methods with optional parameters when using literal values. You must specify ALL parameters explicitly using `It.Is<T>()` or `It.IsAny<T>()` matchers.

**âŒ WRONG - Causes CS0854 Error:**
```csharp
// Method signature: SetupDatabaseAsync(string path, List<string>? props = null, bool overwrite = false)
_mockApi.Setup(x => x.SetupDatabaseAsync(
    "path.db",      // Literal value with optional params
    null,           // Optional parameter
    true))          // Optional parameter - ERROR!
```

**âœ… CORRECT:**
```csharp
// Specify ALL parameters using matchers
_mockApi.Setup(x => x.SetupDatabaseAsync(
    It.Is<string>(s => s == "path.db"),  // Use It.Is matcher
    It.IsAny<List<string>>(),            // Use It.IsAny for optional params
    It.Is<bool>(b => b == true)))        // Use It.Is matcher
```

**Common Optional Parameter Patterns:**
```csharp
// IDialogService.ShowSaveFileDialog(string title, string filter, string ext, string? initialDir = null)
_mockDialogService.Setup(x => x.ShowSaveFileDialog(
    It.IsAny<string>(),   // title
    It.IsAny<string>(),   // filter
    It.IsAny<string>(),   // defaultExtension
    It.IsAny<string>()))  // initialDirectory (optional - MUST specify!)

// IDialogService.ShowOpenFileDialog(string title, string filter, string? initialDir = null, bool multiselect = false)
_mockDialogService.Setup(x => x.ShowOpenFileDialog(
    It.IsAny<string>(),   // title
    It.IsAny<string>(),   // filter
    It.IsAny<string>(),   // initialDirectory (optional - MUST specify!)
    It.IsAny<bool>()))    // multiselect (optional - MUST specify!)
```

#### Basic Mocking Patterns
```csharp
// Setup - Configure mock behavior
_mockService.Setup(x => x.GetValue()).Returns("test value");
_mockService.Setup(x => x.GetValueAsync()).ReturnsAsync("async value");

// Setup with parameter matching
_mockService.Setup(x => x.Process(It.IsAny<string>())).Returns(true);
_mockService.Setup(x => x.Process(It.Is<string>(s => s.Length > 5))).Returns(true);

// Verify - Assert mock was called
_mockService.Verify(x => x.GetValue(), Times.Once);
_mockService.Verify(x => x.Process(It.IsAny<string>()), Times.Never);
```

### ViewModel Testing Patterns

#### Critical Rule: Always Mock Interfaces, Never Concrete Classes
**IMPORTANT:** Moq can only mock virtual or abstract members. In MVVM applications following the Dependency Inversion Principle, all injected dependencies must be interfaces.

**âŒ WRONG - Cannot Mock Concrete Classes:**
```csharp
// This will fail at runtime if the class has non-virtual methods
private Mock<DocManagerApi> _mockApi;  // âŒ Concrete class
private Mock<MessageStore> _mockStore; // âŒ Concrete class
private Mock<Manager> _mockManager;    // âŒ Concrete class

// Error: System.NotSupportedException: 
// Non-overridable members (here: DocManagerApi.GetDatabasePath) may not be used in setup
```

**âœ… CORRECT - Mock Interfaces:**
```csharp
// Production code must use interfaces
private Mock<IDocManagerApi> _mockApi;      // âœ… Interface
private Mock<IMessageStore> _mockStore;     // âœ… Interface  
private Mock<IManager> _mockManager;        // âœ… Interface
private Mock<IDialogService> _mockDialog;   // âœ… Interface

// This works because all interface members are implicitly virtual
_mockApi.Setup(x => x.GetDatabasePath()).Returns("test.db");
```

**Production Code Requirements:**
```csharp
// âœ… ViewModel must use interfaces
public class MyViewModel : ObservableObject
{
    private readonly IDocManagerApi _api;        // âœ… Interface
    private readonly IMessageStore _messageStore; // âœ… Interface
    private readonly IManager _manager;           // âœ… Interface
    
    public MyViewModel(
        IDocManagerApi api,           // âœ… Interface parameter
        IMessageStore messageStore,   // âœ… Interface parameter
        IManager manager)             // âœ… Interface parameter
    {
        _api = api;
        _messageStore = messageStore;
        _manager = manager;
    }
}
```

#### Integration Test Pattern: Mixing Mocks and Real Instances

For ViewModel tests, use a **hybrid approach**:
- **Mock external boundaries**: API, DialogService, SettingsService (dependencies that cross application boundaries)
- **Use real instances**: Manager, MessageStore, CurrentFolderManager (internal application state)

**Why this pattern?**
- Real instances test actual behavior without complex mock setups
- Tests verify real integration between internal components
- Only mock what you can't easily control (external dependencies)
- C# allows concrete instances to be passed where interfaces are expected (implicit casting)

```csharp
[TestFixture]
public class MyViewModelTests
{
    // Mock external dependencies
    private Mock<IDocManagerApi> _mockDocManagerApi;
    private Mock<IDialogService> _mockDialogService;
    
    // Use real instances for internal state
    private MessageStore _messageStore;
    private Manager _manager;
    private CurrentFolderManager _currentFolderManager;
    
    [SetUp]
    public void Setup()
    {
        // Mock external boundaries
        _mockDocManagerApi = new Mock<IDocManagerApi>();
        _mockDialogService = new Mock<IDialogService>();
        
        // Create real instances for internal components
        _messageStore = new MessageStore();
        _manager = new Manager(new CloudDocumentManager());
        _currentFolderManager = new CurrentFolderManager(new CurrentFolderManagerSettings());
    }
    
    [TearDown]
    public void TearDown()
    {
        // Dispose real instances
        _messageStore?.Dispose();
    }
    
    private MyViewModel CreateViewModel()
    {
        return new MyViewModel(
            _mockDocManagerApi.Object,  // Mocked interface
            _messageStore,              // Real instance → IMessageStore (implicit cast)
            _manager,                   // Real instance → IManager (implicit cast)
            _currentFolderManager,      // Real instance → ICurrentFolderManager (implicit cast)
            _mockDialogService.Object); // Mocked interface
    }
}
```

#### MVVM Toolkit Property Change Behavior

**Critical Understanding:** The MVVM Community Toolkit only raises `PropertyChanged` events when property values **actually change**. Setting a property to the same value it already has will **not** trigger change notification.

**âŒ Common Test Mistake:**
```csharp
[ObservableProperty]
private string _name = string.Empty;  // Initial value

[Test]
public void Name_WhenSetToEmpty_TriggersLogic()
{
    var viewModel = CreateViewModel();  // _name = string.Empty
    
    // Act - Setting to same value as initial
    viewModel.Name = string.Empty;  // âŒ No change detected, OnNameChanged() NOT called!
    
    // Assert
    Assert.That(viewModel.SomeState, Is.True);  // âŒ Fails - OnNameChanged never ran
}
```

**âœ… Correct Pattern - Test State Transitions:**
```csharp
[Test]
public void Name_WhenSetToEmpty_TriggersLogic()
{
    var viewModel = CreateViewModel();
    
    // Arrange - Set to different value first
    viewModel.Name = "Some Value";  // Now _name != string.Empty
    
    // Act - Now this is an actual change
    viewModel.Name = string.Empty;  // âœ… Change detected, OnNameChanged() called!
    
    // Assert
    Assert.That(viewModel.SomeState, Is.True);  // âœ… Passes
}
```

**When This Matters:**
- Testing property change callbacks (`OnXxxChanged` partial methods)
- Testing logic that clears state based on empty/null values
- Testing validation that triggers on property changes
- Testing UI updates that depend on property notifications

**General Rule:** Always ensure the property has a **different initial value** than the value being tested. Test **state transitions** (A → B), not setting the same value twice (A → A).

#### Testing Commands: Behavior Over Implementation

**Prefer verifying mock interactions over complex event subscriptions.**

**âŒ Complex Approach - Event Subscriptions:**
```csharp
[Test]
public void NavigateCommand_WhenExecuted_NavigatesToView()
{
    // Setup factory mock
    var testViewModel = new TestViewModel();  // Create test double
    _mockFactory.Setup(x => x.Invoke()).Returns(testViewModel);
    
    var viewModel = CreateViewModel();
    var navigated = false;
    
    // Subscribe to property changed event
    _navigationStore.PropertyChanged += (sender, args) =>
    {
        if (args.PropertyName == nameof(_navigationStore.CurrentViewModel))
            navigated = true;
    };
    
    // Act
    viewModel.NavigateCommand.Execute(null);
    
    // Assert
    Assert.That(navigated, Is.True);
    Assert.That(_navigationStore.CurrentViewModel, Is.EqualTo(testViewModel));
}

// Need extra test double class
private class TestViewModel : ObservableObject { }
```

**âœ… Simple Approach - Verify Mock Calls:**
```csharp
[Test]
public void NavigateCommand_WhenExecuted_NavigatesToView()
{
    var viewModel = CreateViewModel();
    
    // Act
    viewModel.NavigateCommand.Execute(null);
    
    // Assert - Just verify the factory was called
    _mockFactory.Verify(x => x.Invoke(), Times.Once,
        "Factory should be invoked when navigating");
}
```

**Why This Is Better:**
- Tests **what** the command does (calls factory), not **how** navigation works internally
- No dependency on NavigationStore implementation details
- No test doubles or type compatibility issues needed
- Simpler, clearer, more maintainable
- Resilient to refactoring of internal navigation mechanism

**When to Use Each Approach:**
- **Verify mock calls**: Testing commands, delegation, method invocation
- **Event subscriptions**: Testing actual property changes when state verification is the goal
- **State assertions**: Testing business logic results, computed properties

#### Event Subscription Patterns

**Two Types of Events in MVVM:**

1. **INotifyPropertyChanged.PropertyChanged** (MVVM Toolkit standard)
   - Raised automatically by `[ObservableProperty]` when values change
   - Generic event for any property change
   - Requires property name filtering

2. **Custom Events** (manually raised)
   - Specific semantic events (e.g., `DocumentAdded`, `ValidationFailed`)
   - Raised explicitly in code
   - More semantically meaningful

**Pattern 1: PropertyChanged Event**
```csharp
[Test]
public void Property_WhenChanged_UpdatesState()
{
    var viewModel = CreateViewModel();
    var propertyChanged = false;
    
    viewModel.PropertyChanged += (sender, args) =>
    {
        if (args.PropertyName == nameof(viewModel.MyProperty))
            propertyChanged = true;
    };
    
    // Act
    viewModel.MyProperty = "new value";
    
    // Assert
    Assert.That(propertyChanged, Is.True);
}
```

**Pattern 2: Custom Events**
```csharp
// If a custom event exists and is documented, use it
[Test]
public void Action_WhenExecuted_RaisesCustomEvent()
{
    var viewModel = CreateViewModel();
    var eventRaised = false;
    
    viewModel.DocumentAdded += (sender, args) =>  // Custom event
    {
        eventRaised = true;
    };
    
    // Act
    viewModel.AddDocument();
    
    // Assert
    Assert.That(eventRaised, Is.True);
}
```

**Decision Guide:**
- Check if a custom event exists and is part of the public API
- If yes, prefer the custom event (more semantic)
- If no custom event, use PropertyChanged with property name filtering
- For command testing, prefer mock verification over event subscription

#### Factory Mock Setup Patterns

**Pattern 1: Factory Returns Null (Navigation Not Under Test)**
```csharp
// When you only care that factory was called, not what it returns
_mockFactory.Setup(x => x.Invoke()).Returns((MyViewModel)null!);
```

**Pattern 2: Factory Returns Mock Object (For Further Interaction)**
```csharp
// When you need to interact with the returned ViewModel
var mockViewModel = new Mock<MyViewModel>();
_mockFactory.Setup(x => x.Invoke()).Returns(mockViewModel.Object);
```

**Pattern 3: Factory With Logic (Callback Pattern)**
```csharp
// When you need to track factory invocation with additional logic
var factoryCalled = false;
_mockFactory.Setup(x => x.Invoke()).Returns(() =>
{
    factoryCalled = true;
    return null!;
});
```

**Type Compatibility:**
- Factory mock type: `Mock<Func<TViewModel>>`
- Setup must return `TViewModel` (not a different type)
- Use `null!` to suppress nullable warnings when returning null

### Test Organization
- One test class per production class being tested
- Test classes should be in the same namespace structure as production code, with `.Tests` appended
  ```csharp
  // Production: duHastNet.DocManager.Core.Services
  // Test:       duHastNet.DocManager.Core.Tests.Services
  ```

### File Naming
- Test files follow pattern: `{ClassName}Tests.cs`
- For large classes with many responsibilities, split tests into multiple files: `{ClassName}Tests_{Category}.cs`
  - Examples: `DatabaseServiceTests_Initialization.cs`, `DocManagerApiTests_SetupOperations.cs`
  - **For ViewModels with partial classes**: Mirror the production class structure
    - Production: `SettingsViewModel.cs` and `SettingsViewModel_Commands.cs`
    - Tests: `SettingsViewModelTests.cs` and `SettingsViewModelTests_Commands.cs`
  - **Category naming**: Use the same category name as the production partial class (e.g., `_Commands`, `_Helpers`, `_Validation`)
  - **Purpose**: Keeps test organization aligned with production code structure, making tests easier to locate and maintain

## Test Class Structure

### Basic Template
```csharp
using NUnit.Framework;
using duHastNet.DocManager.Core.Services;
using System.IO;

namespace duHastNet.DocManager.Core.Tests.Services;

[TestFixture]
public class MyServiceTests
{
    private MyService _service;
    private string _testDirectory;
    
    [SetUp]
    public void Setup()
    {
        // Initialize test dependencies
        _service = new MyService();
        _testDirectory = Path.Combine(Path.GetTempPath(), "MyServiceTests", Guid.NewGuid().ToString());
        Directory.CreateDirectory(_testDirectory);
    }
    
    [TearDown]
    public async Task TearDown()
    {
        // Clean up resources
        if (_service != null)
        {
            await _service.DisposeAsync();
        }
        
        if (Directory.Exists(_testDirectory))
        {
            Directory.Delete(_testDirectory, true);
        }
    }
    
    [Test]
    public async Task MethodName_Scenario_ExpectedBehavior()
    {
        // Arrange
        
        // Act
        
        // Assert
    }
}
```

### Setup and TearDown Rules

#### [SetUp]
- Initialize common test dependencies
- Create test directories with unique GUIDs to avoid conflicts
- Keep setup lightweight and consistent
- Use synchronous `Setup()` unless async initialization is required
- When async is needed, use `public async Task Setup()`

#### [TearDown]
- Always dispose of services/resources properly
- Clean up test directories and files
- Use `async Task TearDown()` when disposing async resources
- Handle disposal gracefully (null checks)
- For database tests, close connections before deleting files

#### Specialized TearDown for Dispose Tests
```csharp
[TearDown]
public void TearDown()
{
    // Don't dispose here - tests will handle disposal themselves
    if (Directory.Exists(_testDirectory))
    {
        Directory.Delete(_testDirectory, true);
    }
    
    _service?.Dispose(); // Final cleanup only
}
```

## Test Naming Conventions

### Test Method Names
Follow the pattern: `MethodName_Scenario_ExpectedBehavior`

**Examples:**
```csharp
[Test]
public async Task InitializeAsync_WithValidPath_InitializesSuccessfully()

[Test]
public async Task SetupDatabaseAsync_WithInvalidPath_ReturnsFailureResult()

[Test]
public void Constructor_WithAllParameters_SetsAllProperties()

[Test]
public async Task CloseAsync_MultipleCalls_DoesNotThrow()
```

### Scenario Descriptions
- Use clear, descriptive scenarios that explain the test condition
- Common patterns:
  - `WithValidPath`, `WithInvalidPath`, `WithNullParameter`
  - `AfterInitialization`, `BeforeInitialization`, `WithoutInitialization`
  - `MultipleCalls`, `ConcurrentOperations`
  - `EmptyList`, `SingleItem`, `MultipleItems`
  - `ExistingFile`, `NonExistentFile`

### Expected Behavior Descriptions
- Focus on the observable outcome
- Common patterns:
  - `ReturnsSuccessfulResult`, `ReturnsFailureResult`
  - `ThrowsException`, `DoesNotThrow`
  - `CreatesFile`, `DeletesFile`, `UpdatesValue`
  - `InitializesSuccessfully`, `ClosesSuccessfully`
  - `SetsAllProperties`, `ClearsState`

## Test Structure (AAA Pattern)

### Arrange-Act-Assert
Every test must follow the AAA pattern with clear comments:

```csharp
[Test]
public async Task SetupDatabaseAsync_WithValidConfig_CreatesSuccessfulResult()
{
    // Arrange
    var databasePath = Path.Combine(_testDirectory, "test.db");
    var config = new DatabaseSetupConfig
    {
        DatabasePath = databasePath,
        CustomPropertyNames = new List<string> { "Property1", "Property2" },
        OverwriteExisting = false
    };
    
    // Act
    var result = await _api.SetupDatabaseAsync(config);
    
    // Assert
    Assert.Multiple(() =>
    {
        Assert.That(result.IsSetupSuccessful, Is.True);
        Assert.That(result.DatabasePath, Is.EqualTo(databasePath));
        Assert.That(result.HasErrors, Is.False);
        Assert.That(File.Exists(databasePath), Is.True);
    });
}
```

### Section Guidelines

#### Arrange
- Set up all test data and preconditions
- Create test objects with meaningful test values
- Use realistic data (e.g., "Ground Floor Plan", "A-101")
- Keep variable names descriptive

#### Act
- Single action being tested
- Should be one line or a small, focused block
- If "Act" is complex, consider if you're testing too much

#### Assert
- Use `Assert.Multiple()` for multiple related assertions
- Order assertions logically (success checks first, then details)
- Include helpful assertion messages for complex checks
- Use constraint-based assertions (`Is.EqualTo`, `Does.Contain`)

## Assertion Styles

### Preferred NUnit Constraint Model
```csharp
// âœ… Correct
Assert.That(result.IsValid, Is.True);
Assert.That(result.Errors.Count, Is.EqualTo(0));
Assert.That(result.Message, Does.Contain("successful"));
Assert.That(entities, Has.Count.EqualTo(3));
Assert.That(_service.IsInitialized, Is.True);

// âŒ Avoid (classic model)
Assert.IsTrue(result.IsValid);
Assert.AreEqual(0, result.Errors.Count);
```

### Common Assertion Patterns

#### Collections
```csharp
Assert.That(list, Has.Count.EqualTo(3));
Assert.That(list, Is.Empty);
Assert.That(list, Is.Not.Null);
Assert.That(result.Errors.Any(e => e.Contains("required")), Is.True);
```

#### Strings
```csharp
Assert.That(result.Message, Does.Contain("successful"));
Assert.That(result.Message, Does.Not.Contain("error"));
Assert.That(path, Is.EqualTo(expectedPath));
```

#### Exceptions
```csharp
// Async methods
Assert.ThrowsAsync<InvalidOperationException>(async () => 
    await _service.OperationAsync());

// Synchronous methods
Assert.Throws<ArgumentNullException>(() => 
    new Document(null, "name", "rev", 1));

// No exception expected
Assert.DoesNotThrow(() => _service.Dispose());
Assert.DoesNotThrowAsync(async () => await _service.CloseAsync());
```

#### Multiple Assertions
```csharp
Assert.Multiple(() =>
{
    Assert.That(document.Number, Is.EqualTo("A-101"));
    Assert.That(document.Name, Is.EqualTo("Floor Plan"));
    Assert.That(document.Revision, Is.EqualTo("3"));
    Assert.That(document.IsActive, Is.True);
});
```

## Test Categories and Organization

### Use Regions for Logical Grouping
```csharp
[TestFixture]
public class DocManagerApiTests_SetupOperations
{
    #region SetupDatabaseAsync(DatabaseSetupConfig) Tests
    
    [Test]
    public async Task SetupDatabaseAsync_WithValidConfig_CreatesSuccessfulResult()
    { }
    
    [Test]
    public async Task SetupDatabaseAsync_WithInvalidPath_ReturnsFailureResult()
    { }
    
    #endregion
    
    #region SetupDatabaseAsync(string, List<string>, bool) Tests
    
    [Test]
    public async Task SetupDatabaseAsync_SimpleOverload_WithValidParameters_CreatesSuccessfulResult()
    { }
    
    #endregion
}
```

### Region Naming Patterns
- `{MethodName} Tests` - for testing a specific method
- `{Operation} Tests` - for testing a category of functionality
- `Integration Tests` - for full workflow tests
- `Edge Cases` - for boundary conditions
- `Error Handling Tests` - for exception scenarios

## Async/Await Guidelines

### Test Method Signatures
```csharp
// For async operations
[Test]
public async Task MethodName_Scenario_ExpectedBehavior()
{
    await _service.DoSomethingAsync();
}

// For synchronous operations
[Test]
public void MethodName_Scenario_ExpectedBehavior()
{
    _service.DoSomething();
}
```

### Mixing Async and Sync in Setup/TearDown
```csharp
[SetUp]
public void Setup()
{
    _service = new MyService();
}

[TearDown]
public async Task TearDown()
{
    if (_service != null)
    {
        await _service.CloseAsync();
        _service.Dispose();
    }
}
```

## Test Data Management

### Test File Paths
```csharp
// âœ… Use unique test directories to avoid conflicts
_testDirectory = Path.Combine(Path.GetTempPath(), "TestClassName", Guid.NewGuid().ToString());
_testDatabasePath = Path.Combine(_testDirectory, "test.db");

// âœ… Use descriptive file names in tests
var databasePath = Path.Combine(_testDirectory, "empty_props.db");
var firstPath = Path.Combine(_testDirectory, "first.db");
```

### Test Data Values
```csharp
// âœ… Use realistic, meaningful test data
var document = new Document("A-101", "Ground Floor Plan", "3", 5);
var config = new DatabaseSetupConfig
{
    DatabasePath = databasePath,
    CustomPropertyNames = new List<string> { "DisciplineCode", "ProjectPhase" }
};

// âœ… Use data that demonstrates the scenario
var invalidName = "Property\"WithQuotes"; // Problematic characters
var tooLongName = new string('A', 150); // Too long
```

## Testing Specific Scenarios

### Testing Success Paths
```csharp
[Test]
public async Task MethodName_WithValidInput_ReturnsSuccessfulResult()
{
    // Arrange
    var validInput = CreateValidInput();
    
    // Act
    var result = await _service.ProcessAsync(validInput);
    
    // Assert
    Assert.Multiple(() =>
    {
        Assert.That(result.IsSuccessful, Is.True);
        Assert.That(result.HasErrors, Is.False);
        Assert.That(result.Data, Is.Not.Null);
    });
}
```

### Testing Failure Paths
```csharp
[Test]
public async Task MethodName_WithInvalidInput_ReturnsFailureResult()
{
    // Arrange
    var invalidInput = ""; // Empty string
    
    // Act
    var result = await _service.ProcessAsync(invalidInput);
    
    // Assert
    Assert.Multiple(() =>
    {
        Assert.That(result.IsSuccessful, Is.False);
        Assert.That(result.HasErrors, Is.True);
        Assert.That(result.Errors[0], Does.Contain("required"));
    });
}
```

### Testing Validation
```csharp
[Test]
public async Task MethodName_WithWarnings_ReturnsSuccessWithWarnings()
{
    // Arrange
    var config = new DatabaseSetupConfig
    {
        DatabasePath = validPath,
        CustomPropertyNames = new List<string>
        {
            "ValidProperty",
            "", // Empty - will generate warning
            "Property;WithSemicolon" // Invalid chars - will generate warning
        }
    };
    
    // Act
    var result = await _api.SetupDatabaseAsync(config);
    
    // Assert
    Assert.Multiple(() =>
    {
        Assert.That(result.IsSetupSuccessful, Is.True);
        Assert.That(result.HasWarnings, Is.True);
        Assert.That(result.Warnings, Has.Count.EqualTo(2));
        Assert.That(result.Warnings.Any(w => w.Contains("[empty/whitespace]")), Is.True);
    });
}
```

### Testing Multiple Calls
```csharp
[Test]
public async Task MethodName_MultipleCalls_DoesNotThrow()
{
    // Arrange
    await _service.InitializeAsync();
    
    // Act & Assert
    await _service.CloseAsync();
    Assert.DoesNotThrowAsync(async () => await _service.CloseAsync());
    Assert.DoesNotThrowAsync(async () => await _service.CloseAsync());
}
```

### Testing State Changes
```csharp
[Test]
public async Task MethodName_ChangesState_UpdatesAllProperties()
{
    // Arrange
    await _service.InitializeAsync();
    Assert.That(_service.IsInitialized, Is.True);
    
    // Act
    await _service.CloseAsync();
    
    // Assert
    Assert.Multiple(() =>
    {
        Assert.That(_service.IsInitialized, Is.False);
        Assert.That(_service.Connection, Is.Null);
        Assert.That(_service.Path, Is.Null);
    });
}
```

### Testing Integration Workflows
```csharp
[Test]
public async Task FullWorkflow_SetupTestClose_WorksCorrectly()
{
    // Arrange
    var databasePath = Path.Combine(_testDirectory, "workflow.db");
    
    // Act & Assert - Setup
    var setupResult = await _api.SetupDatabaseAsync(databasePath);
    Assert.That(setupResult.IsSetupSuccessful, Is.True);
    Assert.That(_api.IsDatabaseReady(), Is.True);
    
    // Act & Assert - Test
    var testResult = await _api.TestDatabaseAsync();
    Assert.That(testResult.IsSetupSuccessful, Is.True);
    
    // Act & Assert - Close
    await _api.CloseAsync();
    Assert.That(_api.IsDatabaseReady(), Is.False);
}
```

## Comments and Documentation

### When to Add Comments
```csharp
[Test]
public async Task MethodName_ComplexScenario_ExpectedBehavior()
{
    // Arrange
    // Create database with specific schema requirements
    var config = CreateComplexConfig();
    
    // Act
    var result = await _service.ProcessAsync(config);
    
    // Assert
    // Verify all schema elements were created correctly
    Assert.Multiple(() =>
    {
        Assert.That(result.TablesCreated, Has.Count.EqualTo(4));
        Assert.That(result.IndexesCreated, Has.Count.EqualTo(7));
    });
}
```

### Documenting Test Intent
```csharp
[Test]
public async Task Dispose_DuringActiveTransaction_HandlesGracefully()
{
    // This test verifies that Dispose properly handles cleanup
    // even when a transaction is still active, preventing
    // database corruption or locked files
    
    // Arrange
    await _service.InitializeAsync(_testDatabasePath);
    // Start transaction but don't commit
    await _service.BeginTransactionAsync();
    
    // Act - Dispose should handle active transaction
    Assert.DoesNotThrow(() => _service.Dispose());
    
    // Assert
    Assert.That(_service.IsInitialized, Is.False);
}
```

## Production Code Requirements for Testability

### Interface-Based Dependencies (CRITICAL)

**All injected dependencies in ViewModels and services must be interfaces, not concrete classes.**

This is a **hard requirement** for testability with Moq and follows the Dependency Inversion Principle (SOLID).

**âœ… Correct Production Code:**
```csharp
public class MyViewModel : ObservableObject
{
    // All dependencies are interfaces
    private readonly IDocManagerApi _api;
    private readonly IMessageStore _messageStore;
    private readonly IManager _manager;
    private readonly IDialogService _dialogService;
    
    public MyViewModel(
        IDocManagerApi api,           // Interface parameter
        IMessageStore messageStore,   // Interface parameter
        IManager manager,             // Interface parameter
        IDialogService dialogService) // Interface parameter
    {
        _api = api;
        _messageStore = messageStore;
        _manager = manager;
        _dialogService = dialogService;
    }
}
```

**âŒ Incorrect Production Code:**
```csharp
public class MyViewModel : ObservableObject
{
    // âŒ Concrete classes - cannot be mocked
    private readonly DocManagerApi _api;
    private readonly MessageStore _messageStore;
    private readonly Manager _manager;
    
    public MyViewModel(
        DocManagerApi api,       // âŒ Concrete class
        MessageStore messageStore, // âŒ Concrete class
        Manager manager)          // âŒ Concrete class
    {
        // This code cannot be properly unit tested with Moq!
    }
}
```

**Why This Matters:**
- Moq can only mock interfaces and virtual members
- Concrete classes with non-virtual methods throw `NotSupportedException` at runtime
- Interface-based design enables dependency injection and test isolation
- Follows SOLID principles (Dependency Inversion)

**Interface Checklist:**
When reviewing production code before writing tests, verify:
- âœ… All constructor parameters are interfaces
- âœ… All private readonly fields store interfaces
- âœ… No concrete service/manager classes are injected
- âœ… Interfaces exist for all mockable dependencies

See `InterfaceBestPractices.md` for comprehensive interface design guidelines.

### Property Initialization Patterns

Be aware of how properties are initialized, as this affects test behavior:

```csharp
// Initial values affect property change detection
[ObservableProperty]
private string _name = string.Empty;  // Starts as empty string

[ObservableProperty]
private bool _isEnabled = false;      // Starts as false

[ObservableProperty]
private int _count = 0;               // Starts as 0
```

**Test Consideration:** Setting a property to its initial value won't trigger `OnPropertyChanged` callbacks. Tests must set properties to **different** values first to test state transitions.

## Anti-Patterns to Avoid

### âŒ Don't Test Multiple Concerns
```csharp
// âŒ Bad - testing too much
[Test]
public async Task TestEverything()
{
    await _api.SetupDatabaseAsync(path);
    await _api.ImportDataAsync(data);
    await _api.ExportDataAsync(outputPath);
    await _api.CloseAsync();
    // Testing 4 different operations!
}

// âœ… Good - focused tests
[Test]
public async Task SetupDatabaseAsync_WithValidPath_CreatesSuccessfully()
{
    var result = await _api.SetupDatabaseAsync(path);
    Assert.That(result.IsSuccessful, Is.True);
}
```

### âŒ Don't Use Magic Values
```csharp
// âŒ Bad
var document = new Document("X", "Y", "Z", 42);

// âœ… Good
var documentNumber = "A-101";
var documentName = "Ground Floor Plan";
var revision = "3";
var revisionId = 5;
var document = new Document(documentNumber, documentName, revision, revisionId);
```

### âŒ Don't Rely on Test Order
```csharp
// âŒ Bad - relies on previous test
[Test]
public async Task Test1_CreateDatabase() 
{
    _sharedDatabase = await CreateDatabase();
}

[Test]
public async Task Test2_UseDatabase() // Depends on Test1!
{
    await UseDatabase(_sharedDatabase);
}

// âœ… Good - each test is independent
[Test]
public async Task CreateDatabase_WithValidPath_CreatesSuccessfully()
{
    var database = await CreateDatabase();
    Assert.That(database, Is.Not.Null);
}
```

### âŒ Don't Ignore Cleanup
```csharp
// âŒ Bad
[TearDown]
public void TearDown()
{
    // Nothing - leaves test files around!
}

// âœ… Good
[TearDown]
public async Task TearDown()
{
    if (_service != null)
    {
        await _service.CloseAsync();
        _service.Dispose();
    }
    
    if (Directory.Exists(_testDirectory))
    {
        Directory.Delete(_testDirectory, true);
    }
}
```

### âŒ Don't Mock Concrete Classes
```csharp
// âŒ Bad - will fail at runtime
private Mock<DocManagerApi> _mockApi;  // Concrete class with non-virtual methods
_mockApi.Setup(x => x.GetDatabasePath()).Returns("test.db");  // Runtime error!

// âœ… Good - mock the interface
private Mock<IDocManagerApi> _mockApi;  // Interface
_mockApi.Setup(x => x.GetDatabasePath()).Returns("test.db");  // Works!
```

### âŒ Don't Test Property Changes Without Actual Changes
```csharp
// âŒ Bad - property initialized to empty, setting to empty again
[Test]
public void Name_WhenSetToEmpty_ClearsState()
{
    var vm = CreateViewModel();  // Name = string.Empty initially
    vm.Name = string.Empty;      // No change detected!
    Assert.That(vm.StateCleared, Is.True);  // Fails
}

// âœ… Good - create an actual state transition
[Test]
public void Name_WhenSetToEmpty_ClearsState()
{
    var vm = CreateViewModel();
    vm.Name = "Some Value";      // Set to different value first
    vm.Name = string.Empty;      // Now this is a change!
    Assert.That(vm.StateCleared, Is.True);  // Passes
}
```

### âŒ Don't Over-Complicate Command Tests
```csharp
// âŒ Bad - complex event subscription to verify navigation
[Test]
public void NavigateCommand_WhenExecuted_Navigates()
{
    var testVm = new TestViewModel();
    _mockFactory.Setup(x => x.Invoke()).Returns(testVm);
    var navigated = false;
    _navStore.PropertyChanged += (s, e) => 
    {
        if (e.PropertyName == nameof(_navStore.CurrentViewModel))
            navigated = true;
    };
    
    vm.NavigateCommand.Execute(null);
    Assert.That(navigated, Is.True);
}

// âœ… Good - just verify factory was called
[Test]
public void NavigateCommand_WhenExecuted_CallsFactory()
{
    vm.NavigateCommand.Execute(null);
    _mockFactory.Verify(x => x.Invoke(), Times.Once);
}
```

## Line Endings

All test files must use **Windows line endings (CRLF)** to maintain consistency with the rest of the project.

## Complete Example

```csharp
using NUnit.Framework;
using duHastNet.DocManager.Core.Services;
using duHastNet.DocManager.Core.Models;
using System.IO;

namespace duHastNet.DocManager.Core.Tests.Services;

[TestFixture]
public class DocumentServiceTests
{
    private DocumentService _documentService;
    private string _testDirectory;
    private string _testDatabasePath;
    
    [SetUp]
    public async Task Setup()
    {
        _documentService = new DocumentService();
        _testDirectory = Path.Combine(Path.GetTempPath(), "DocumentServiceTests", Guid.NewGuid().ToString());
        _testDatabasePath = Path.Combine(_testDirectory, "test.db");
        
        Directory.CreateDirectory(_testDirectory);
        await _documentService.InitializeAsync(_testDatabasePath);
    }
    
    [TearDown]
    public async Task TearDown()
    {
        if (_documentService != null)
        {
            await _documentService.CloseAsync();
            _documentService.Dispose();
        }
        
        if (Directory.Exists(_testDirectory))
        {
            Directory.Delete(_testDirectory, true);
        }
    }
    
    #region CreateDocumentAsync Tests
    
    [Test]
    public async Task CreateDocumentAsync_WithValidData_CreatesSuccessfully()
    {
        // Arrange
        var documentNumber = "A-101";
        var documentName = "Ground Floor Plan";
        var revision = "3";
        var revisionId = 1;
        
        // Act
        var result = await _documentService.CreateDocumentAsync(
            documentNumber, documentName, revision, revisionId);
        
        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsSuccessful, Is.True);
            Assert.That(result.Document, Is.Not.Null);
            Assert.That(result.Document.Number, Is.EqualTo(documentNumber));
            Assert.That(result.Document.Name, Is.EqualTo(documentName));
            Assert.That(result.Document.Revision, Is.EqualTo(revision));
        });
    }
    
    [Test]
    public async Task CreateDocumentAsync_WithNullNumber_ReturnsFailureResult()
    {
        // Arrange
        string documentNumber = null;
        var documentName = "Floor Plan";
        var revision = "1";
        var revisionId = 1;
        
        // Act
        var result = await _documentService.CreateDocumentAsync(
            documentNumber, documentName, revision, revisionId);
        
        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsSuccessful, Is.False);
            Assert.That(result.HasErrors, Is.True);
            Assert.That(result.Errors[0], Does.Contain("Document number is required"));
        });
    }
    
    #endregion
    
    #region GetDocumentAsync Tests
    
    [Test]
    public async Task GetDocumentAsync_ExistingDocument_ReturnsDocument()
    {
        // Arrange
        var document = await CreateTestDocument("S-201", "Structural Plan");
        
        // Act
        var result = await _documentService.GetDocumentAsync(document.Id);
        
        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Is.Not.Null);
            Assert.That(result.Number, Is.EqualTo("S-201"));
            Assert.That(result.Name, Is.EqualTo("Structural Plan"));
        });
    }
    
    [Test]
    public async Task GetDocumentAsync_NonExistentDocument_ReturnsNull()
    {
        // Arrange
        var nonExistentId = 99999;
        
        // Act
        var result = await _documentService.GetDocumentAsync(nonExistentId);
        
        // Assert
        Assert.That(result, Is.Null);
    }
    
    #endregion
    
    #region Helper Methods
    
    private async Task<Document> CreateTestDocument(string number, string name)
    {
        var result = await _documentService.CreateDocumentAsync(number, name, "1", 1);
        return result.Document;
    }
    
    #endregion
}
```

## Summary Checklist

When writing tests, ensure:

- âœ… Test file names follow `{ClassName}Tests.cs` pattern
- âœ… For partial classes, test files mirror production structure (e.g., `_Commands.cs`)
- âœ… Each test follows AAA pattern with clear comments
- âœ… Test names follow `MethodName_Scenario_ExpectedBehavior` pattern
- âœ… Use `Assert.Multiple()` for related assertions
- âœ… Use NUnit constraint model (`Is.EqualTo`, `Does.Contain`)
- âœ… Setup creates unique test directories with GUIDs
- âœ… TearDown properly disposes all resources
- âœ… Tests are independent and can run in any order
- âœ… Use realistic, meaningful test data
- âœ… Group related tests in regions
- âœ… Handle async/await consistently
- âœ… Windows line endings (CRLF)
- âœ… Clean up all test files and directories

**For ViewModel Tests:**
- âœ… Production code uses interfaces for all injected dependencies
- âœ… Mock interfaces (IDocManagerApi), not concrete classes (DocManagerApi)
- âœ… Use hybrid approach: mock external boundaries, use real instances for internal state
- âœ… Test property state transitions (set different value first, then test value)
- âœ… Prefer mock verification over complex event subscriptions for commands
- âœ… Dispose MessageStore and other IDisposable instances in TearDown
