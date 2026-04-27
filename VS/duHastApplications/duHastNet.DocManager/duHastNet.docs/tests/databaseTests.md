# Database Testing Guidelines

## Core Principle: ORM-First

Tests should be ORM-first and demonstrate sqlite-net-pcl's ORM capabilities. All database interaction in tests uses sqlite-net-pcl directly — never bypass the ORM for operations it can handle.

### When to Use Raw SQL in Tests

Raw SQL should only appear in tests when the behaviour under test itself uses raw SQL. Do not introduce raw SQL in test setup or assertions where ORM methods would suffice.

Legitimate cases for raw SQL in tests:

- Testing PRAGMA-based methods (e.g. `GetDataVersionAsync`, `CheckDatabaseIntegrityAsync`) where the implementation itself executes raw SQL
- Verifying schema operations (indexes, table structure) that have no ORM equivalent
- Corrupting a database deliberately to test error handling

### Architecture Hierarchy

- **Primary**: sqlite-net-pcl ORM methods (`InsertAsync`, `Table<T>().Where()`, `FindAsync`, etc.)
- **Secondary**: Raw SQL via `ExecuteAsync` / `ExecuteScalarAsync` only when the scenario requires it
- **Never**: Bypassing sqlite-net-pcl entirely

---

## Database Test Setup Pattern

Every database test class must follow this setup pattern:

```csharp
[SetUp]
public async Task Setup()
{
    _databasePath = Path.Combine(
        Path.GetTempPath(),
        "MyClassTests",
        Guid.NewGuid().ToString(),
        "test.db");

    Directory.CreateDirectory(Path.GetDirectoryName(_databasePath)!);

    var connectionString = new SQLiteConnectionString(
        _databasePath,
        storeDateTimeAsTicks: false,
        openFlags: SQLiteOpenFlags.ReadWrite | SQLiteOpenFlags.Create,
        key: null);

    _connection = new SQLiteAsyncConnection(connectionString);
    await _connection.CreateTableAsync<MyEntity>();
}

[TearDown]
public async Task TearDown()
{
    if (_connection != null)
        await _connection.CloseAsync();

    var dir = Path.GetDirectoryName(_databasePath);
    if (Directory.Exists(dir))
        Directory.Delete(dir, true);
}
```

For sync tests, use `SQLiteConnection` instead of `SQLiteAsyncConnection` and remove `async`/`await`.

**Key rules:**
- Use a GUID-based directory so each test run gets its own isolated database file
- Always close the connection before deleting the file
- Delete the entire test directory in `TearDown`, not just the file

---

## Required Test Coverage for Hardening Features

The following hardening features are part of the production implementation and must be covered by tests. Each is described with the expected test pattern.

---

### Busy Timeout

Both `Initialize` (sync) and `InitializeAsync` (async) configure a 5-second busy timeout on their respective connections. This must be verified by tests.

**Why test this:** The busy timeout is the primary concurrency hardening measure. If it is accidentally removed during a refactor, a test should catch it before it reaches production.

**Test pattern — async connection:**

```csharp
[Test]
public async Task InitializeAsync_ConfiguresBusyTimeout()
{
    // Arrange & Act
    await _databaseService.InitializeAsync(_testDatabasePath);

    // Assert - PRAGMA busy_timeout returns the configured value in milliseconds
    var busyTimeout = await _databaseService.Connection
        .ExecuteScalarAsync<int>("PRAGMA busy_timeout");

    Assert.That(busyTimeout, Is.EqualTo(5000));
}
```

**Test pattern — sync connection:**

```csharp
[Test]
public void Initialize_ConfiguresBusyTimeout()
{
    // Arrange & Act
    _databaseService.Initialize(_testDatabasePath);

    // Assert - BusyTimeout property is directly readable on SQLiteConnection
    Assert.That(_databaseService.SyncConnection.BusyTimeout,
        Is.EqualTo(TimeSpan.FromSeconds(5)));
}
```

---

### `GetDataVersionAsync` and `GetDataVersion`

These methods expose SQLite's `PRAGMA data_version`, which increments whenever any connection writes to the database. Both the async and sync variants must be tested.

**Required tests:**

1. Returns a non-negative integer after initialisation
2. Value increments after a write operation
3. Value does not change when only reads occur

**Test pattern:**

```csharp
[Test]
public async Task GetDataVersionAsync_AfterWrite_ReturnsIncrementedValue()
{
    // Arrange
    await _databaseService.InitializeAsync(_testDatabasePath);
    var versionBefore = await _databaseService.GetDataVersionAsync();

    // Act
    var revision = new Revision(DateTime.Today, "Test");
    await _databaseService.Connection.InsertAsync(revision);

    var versionAfter = await _databaseService.GetDataVersionAsync();

    // Assert
    Assert.That(versionAfter, Is.GreaterThan(versionBefore));
}

[Test]
public async Task GetDataVersionAsync_AfterReadOnly_ReturnsSameValue()
{
    // Arrange
    await _databaseService.InitializeAsync(_testDatabasePath);
    var revision = new Revision(DateTime.Today, "Test");
    await _databaseService.Connection.InsertAsync(revision);

    var versionBefore = await _databaseService.GetDataVersionAsync();

    // Act - read only
    await _databaseService.Connection.Table<Revision>().ToListAsync();

    var versionAfter = await _databaseService.GetDataVersionAsync();

    // Assert
    Assert.That(versionAfter, Is.EqualTo(versionBefore));
}
```

Mirror these tests for the sync path using `Initialize` and `GetDataVersion`.

---

### Transaction Atomicity (`RunInTransactionAsync` / `RunInTransaction`)

Any class that exposes or uses `RunInTransactionAsync` (async) or `RunInTransaction` (sync) must have tests verifying:

1. **Commit path**: all writes inside the transaction are visible after it completes
2. **Rollback path**: no writes persist if the action throws an exception

These tests must exist for both `UnitOfWork.RunInTransactionAsync` and `UnitOfWorkSync.RunInTransaction`.

**Test pattern — commit:**

```csharp
[Test]
public async Task RunInTransactionAsync_OnSuccess_CommitsAllWrites()
{
    // Arrange
    var revision = new Revision(DateTime.Today, "Test");
    await _unitOfWork.Revisions.InsertAsync(revision);

    // Act
    await _unitOfWork.RunInTransactionAsync(conn =>
    {
        var doc1 = new Document("A-101", "Floor Plan", "1", revision.Id);
        var doc2 = new Document("A-102", "Ceiling Plan", "1", revision.Id);
        conn.Insert(doc1);
        conn.Insert(doc2);
    });

    // Assert
    var allDocs = await _unitOfWork.Documents.GetAllAsync();
    Assert.That(allDocs, Has.Count.EqualTo(2));
}
```

**Test pattern — rollback:**

```csharp
[Test]
public async Task RunInTransactionAsync_OnException_RollsBackAllWrites()
{
    // Arrange
    var revision = new Revision(DateTime.Today, "Test");
    await _unitOfWork.Revisions.InsertAsync(revision);

    // Act
    Assert.ThrowsAsync<InvalidOperationException>(async () =>
    {
        await _unitOfWork.RunInTransactionAsync(conn =>
        {
            conn.Insert(new Document("A-101", "Floor Plan", "1", revision.Id));
            throw new InvalidOperationException("Simulated failure");
        });
    });

    // Assert - nothing was committed
    var allDocs = await _unitOfWork.Documents.GetAllAsync();
    Assert.That(allDocs, Has.Count.EqualTo(0));
}
```

---

### `DatabaseService` Sync Path

The sync methods on `DatabaseService` (`Initialize`, `CreateTables`, `Close`, `CheckDatabaseIntegrity`, `GetDataVersion`) must have the same depth of test coverage as their async counterparts. This coverage belongs in a dedicated `DatabaseServiceTests_Sync.cs` partial test class.

Minimum required tests:

- `Initialize_WithValidPath_InitializesSuccessfully`
- `Initialize_WithNullPath_ThrowsArgumentNullException`
- `Initialize_WithEmptyPath_ThrowsArgumentException`
- `Initialize_WithWhitespacePath_ThrowsArgumentException`
- `Initialize_ConfiguresBusyTimeout`
- `Initialize_WithNonExistentDirectory_CreatesDirectory`
- `CreateTables_CreatesAllRequiredTables`
- `Close_AfterInitialization_ClosesConnection`
- `Close_WithoutInitialization_DoesNotThrow`
- `CheckDatabaseIntegrity_AfterInitialization_ReturnsTrue`
- `GetDataVersion_AfterInitialization_ReturnsNonNegativeValue`
- `GetDataVersion_AfterWrite_ReturnsIncrementedValue`

---

## `DatabaseService` Sync Test Setup Pattern

Sync tests for `DatabaseService` do not use `async`/`await` and must close the sync connection through `Close()` before cleanup:

```csharp
[TestFixture]
public class DatabaseServiceTests_Sync
{
    private DatabaseService _databaseService;
    private string _testDatabasePath;
    private string _testDirectory;

    [SetUp]
    public void Setup()
    {
        _databaseService = new DatabaseService();
        _testDirectory = Path.Combine(
            Path.GetTempPath(),
            "DatabaseServiceTests_Sync",
            Guid.NewGuid().ToString());
        _testDatabasePath = Path.Combine(_testDirectory, "test.db");
    }

    [TearDown]
    public void TearDown()
    {
        _databaseService?.Close();
        _databaseService?.Dispose();

        if (Directory.Exists(_testDirectory))
            Directory.Delete(_testDirectory, true);
    }
}
```

---

## SQLiteAsyncConnection Connection Pooling

sqlite-net-pcl pools `SQLiteAsyncConnection` instances by database path. Opening a second `SQLiteAsyncConnection` to the same path returns the same underlying connection object — it does **not** create a new OS-level connection.

### Why this matters in tests

Any test that needs to simulate an **external writer** (a second, genuinely independent connection) must use `SQLiteConnection` (sync), not `SQLiteAsyncConnection`. If `SQLiteAsyncConnection` is used, SQLite sees only one connection and behaviours that depend on cross-connection state — such as `PRAGMA data_version` — will not work as expected.

**Affected scenarios:**
- Testing `GetDataVersionAsync` / `GetDataVersion` increment after an external write
- Testing busy timeout / locking behaviour under concurrent access
- Any test that asserts state visible only to a different connection

**Correct pattern — second writer in an async test:**

```csharp
// SQLiteAsyncConnection pools by path — use SQLiteConnection for the second
// writer so SQLite sees a genuinely separate connection.
var secondConnection = new SQLiteConnection(_testDatabasePath);
try
{
    secondConnection.CreateTable<Revision>(); // schema required on fresh connection
    secondConnection.Insert(new Revision(DateTime.Today, "External write"));
}
finally
{
    secondConnection.Close();
}
```

**Wrong pattern — does not create a separate connection:**

```csharp
// This reuses the pooled connection — SQLite sees no second writer.
var secondConnection = new SQLiteAsyncConnection(_testDatabasePath);
await secondConnection.InsertAsync(revision); // data_version will NOT increment
```

### Production impact

This pooling behaviour has no impact on production code. `DatabaseService` creates exactly one connection per instance (either async or sync, never both), and no two `SQLiteAsyncConnection` instances ever target the same path simultaneously. The pool is effectively transparent in the production use case.

---

## General Reminders

- Use `Assert.Multiple()` for related assertions
- Test names follow `MethodName_Scenario_ExpectedBehavior`
- Group related tests in `#region` blocks
- Use realistic, meaningful test data (document numbers, revision descriptions)
- All test files must use Windows line endings (CRLF)
