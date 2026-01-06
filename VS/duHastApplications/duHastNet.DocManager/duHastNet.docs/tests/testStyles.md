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

**❌ WRONG - Causes CS0854 Error:**
```csharp
// Method signature: SetupDatabaseAsync(string path, List<string>? props = null, bool overwrite = false)
_mockApi.Setup(x => x.SetupDatabaseAsync(
    "path.db",      // Literal value with optional params
    null,           // Optional parameter
    true))          // Optional parameter - ERROR!
```

**✅ CORRECT:**
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
// ✅ Correct
Assert.That(result.IsValid, Is.True);
Assert.That(result.Errors.Count, Is.EqualTo(0));
Assert.That(result.Message, Does.Contain("successful"));
Assert.That(entities, Has.Count.EqualTo(3));
Assert.That(_service.IsInitialized, Is.True);

// ❌ Avoid (classic model)
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
// ✅ Use unique test directories to avoid conflicts
_testDirectory = Path.Combine(Path.GetTempPath(), "TestClassName", Guid.NewGuid().ToString());
_testDatabasePath = Path.Combine(_testDirectory, "test.db");

// ✅ Use descriptive file names in tests
var databasePath = Path.Combine(_testDirectory, "empty_props.db");
var firstPath = Path.Combine(_testDirectory, "first.db");
```

### Test Data Values
```csharp
// ✅ Use realistic, meaningful test data
var document = new Document("A-101", "Ground Floor Plan", "3", 5);
var config = new DatabaseSetupConfig
{
    DatabasePath = databasePath,
    CustomPropertyNames = new List<string> { "DisciplineCode", "ProjectPhase" }
};

// ✅ Use data that demonstrates the scenario
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

## Anti-Patterns to Avoid

### ❌ Don't Test Multiple Concerns
```csharp
// ❌ Bad - testing too much
[Test]
public async Task TestEverything()
{
    await _api.SetupDatabaseAsync(path);
    await _api.ImportDataAsync(data);
    await _api.ExportDataAsync(outputPath);
    await _api.CloseAsync();
    // Testing 4 different operations!
}

// ✅ Good - focused tests
[Test]
public async Task SetupDatabaseAsync_WithValidPath_CreatesSuccessfully()
{
    var result = await _api.SetupDatabaseAsync(path);
    Assert.That(result.IsSuccessful, Is.True);
}
```

### ❌ Don't Use Magic Values
```csharp
// ❌ Bad
var document = new Document("X", "Y", "Z", 42);

// ✅ Good
var documentNumber = "A-101";
var documentName = "Ground Floor Plan";
var revision = "3";
var revisionId = 5;
var document = new Document(documentNumber, documentName, revision, revisionId);
```

### ❌ Don't Rely on Test Order
```csharp
// ❌ Bad - relies on previous test
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

// ✅ Good - each test is independent
[Test]
public async Task CreateDatabase_WithValidPath_CreatesSuccessfully()
{
    var database = await CreateDatabase();
    Assert.That(database, Is.Not.Null);
}
```

### ❌ Don't Ignore Cleanup
```csharp
// ❌ Bad
[TearDown]
public void TearDown()
{
    // Nothing - leaves test files around!
}

// ✅ Good
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

- ✅ Test file names follow `{ClassName}Tests.cs` pattern
- ✅ Each test follows AAA pattern with clear comments
- ✅ Test names follow `MethodName_Scenario_ExpectedBehavior` pattern
- ✅ Use `Assert.Multiple()` for related assertions
- ✅ Use NUnit constraint model (`Is.EqualTo`, `Does.Contain`)
- ✅ Setup creates unique test directories with GUIDs
- ✅ TearDown properly disposes all resources
- ✅ Tests are independent and can run in any order
- ✅ Use realistic, meaningful test data
- ✅ Group related tests in regions
- ✅ Handle async/await consistently
- ✅ Windows line endings (CRLF)
- ✅ Clean up all test files and directories
