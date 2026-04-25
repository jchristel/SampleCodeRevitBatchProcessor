# Synchronous Database Tests - Coverage Summary

## Overview

Test suite for synchronous database access in the `.Core` namespace. All tests follow the project's test style guidelines and database testing best practices. This document reflects the current state of coverage including known gaps.

---

## Completed Test Files

### 1. BaseRepositorySyncTests.cs (442 lines)

Tests for `BaseRepositorySync<T>` providing foundational CRUD operations.

**Coverage:**
- ✅ Insert / InsertAll operations
- ✅ GetById / GetAll operations
- ✅ Update / UpdateAll operations
- ✅ Delete / DeleteAll operations (by entity and by ID)
- ✅ Find with predicates
- ✅ FirstOrDefault queries
- ✅ Count (with and without predicates)
- ✅ Exists checks

---

### 2. UnitOfWorkSyncTests.cs (341 lines)

Tests for `UnitOfWorkSync` managing repository coordination.

**Coverage:**
- ✅ Constructor initialisation of all repositories
- ✅ SaveChanges compatibility
- ✅ Repository instances sharing same connection
- ✅ Cross-repository operations
- ✅ Immediate persistence verification
- ✅ Dispose behaviour
- ✅ Multiple repository method calls
- ✅ Complex workflows using all repositories

**Known gaps — see Gaps section:**
- ❌ `RunInTransaction` commit path not tested
- ❌ `RunInTransaction` rollback path not tested

---

### 3. CustomFieldDefinitionRepositorySyncTests.cs (929 lines)

Tests for `CustomFieldDefinitionRepositorySync`.

**Coverage:**
- ✅ GetByPropertyName — finding definitions by name
- ✅ GetActive / GetInactive — active/inactive filtering with ordering
- ✅ PropertyNameExists — case-insensitive existence checking
- ✅ UpdateIsActive — toggling active status
- ✅ All inherited BaseRepositorySync methods
- ✅ Bulk operations (InsertAll, UpdateAll, DeleteAll)
- ✅ Integration tests for complete lifecycle
- ✅ Multi-definition filtering and sorting scenarios

---

### 4. CustomPropertyRepositorySyncTests.cs (504 lines)

Tests for `CustomPropertyRepositorySync`.

**Coverage:**
- ✅ GetPropertiesByDocument — retrieving properties with ordering
- ✅ GetDistinctPropertyNames — unique property name extraction
- ✅ Empty result handling
- ✅ Non-existent document scenarios
- ✅ All inherited BaseRepositorySync methods
- ✅ Bulk insert operations
- ✅ Integration tests for complete workflows
- ✅ Multi-document property scenarios

---

### 5. DocumentRepositorySyncTests.cs (801 lines)

Tests for `DocumentRepositorySync`.

**Coverage:**
- ✅ GetDocumentsByRevision — revision filtering (active-only)
- ✅ GetDocumentsByNumber — all revisions of a document
- ✅ GetLatestDocumentRevision — most recent active revision
- ✅ GetDistinctDocumentNumbers — unique document numbers
- ✅ SearchDocuments — case-insensitive search
- ✅ DocumentExists — active document checking
- ✅ GetActiveDocuments / GetInactiveDocuments — status filtering
- ✅ UpdateActiveStatus — status toggling
- ✅ GetDocumentsByHistoryNumber — historical number search
- ✅ DocumentNumberExistsAnywhere — current + historical check
- ✅ GetAllDocumentNumbersEverUsed — complete number history
- ✅ GetAllDocumentsByRevision / Number — including inactive
- ✅ AnyDocumentExists — existence with inactive included
- ✅ Integration tests for complete document lifecycle

---

### 6. RevisionRepositorySyncTests.cs (791 lines)

Tests for `RevisionRepositorySync`.

**Coverage:**
- ✅ GetRevisionsByDateRange — date range filtering with ordering
- ✅ GetLatestRevision — most recent revision
- ✅ GetRevisionsByDate — specific date queries (time-agnostic)
- ✅ AddDocumentToRevision — single document association
- ✅ RemoveDocumentFromRevision — single document removal
- ✅ AddDocumentsToRevision — bulk document association
- ✅ RemoveDocumentsFromRevision — bulk document removal
- ✅ SetRevisionDocuments — complete replacement
- ✅ GetRevisionsByDocumentId — finding revisions containing a document
- ✅ GetDocumentCount — document count per revision
- ✅ RevisionContainsDocument — document membership check
- ✅ GetEmptyRevisions — revisions with no documents
- ✅ GetRevisionStatistics — comprehensive statistics
- ✅ All inherited BaseRepositorySync methods
- ✅ Integration tests for complete revision lifecycle

---

## Coverage Statistics

| Class | Test File | Lines | Tests | Integration Tests |
|---|---|---|---|---|
| BaseRepositorySync | BaseRepositorySyncTests.cs | 442 | 18 | N/A |
| UnitOfWorkSync | UnitOfWorkSyncTests.cs | 341 | 9 | 1 |
| CustomFieldDefinitionRepositorySync | CustomFieldDefinitionRepositorySyncTests.cs | 929 | 35 | 2 |
| CustomPropertyRepositorySync | CustomPropertyRepositorySyncTests.cs | 504 | 16 | 2 |
| DocumentRepositorySync | DocumentRepositorySyncTests.cs | 801 | 30 | 1 |
| RevisionRepositorySync | RevisionRepositorySyncTests.cs | 791 | 42 | 1 |
| **TOTAL** | **6 files** | **3,808** | **150+** | **7** |

---

## Known Gaps

The following sync-path features have no test coverage. These gaps were introduced during the SQLite hardening implementation and must be addressed.

### GAP 1 — `DatabaseService` Sync Path (No coverage)

`DatabaseService` has a complete synchronous surface (`Initialize`, `CreateTables`, `Close`, `CheckDatabaseIntegrity`, `GetDataVersion`) used by the Revit plugin via IronPython. None of these methods have tests. All existing `DatabaseServiceTests_*` files cover the async path only.

A new test file `DatabaseServiceTests_Sync.cs` is required. Minimum coverage:

- `Initialize_WithValidPath_InitializesSuccessfully`
- `Initialize_WithNullPath_ThrowsArgumentNullException`
- `Initialize_WithEmptyPath_ThrowsArgumentException`
- `Initialize_WithWhitespacePath_ThrowsArgumentException`
- `Initialize_ConfiguresBusyTimeout` — verifies `SyncConnection.BusyTimeout` is `TimeSpan.FromSeconds(5)`
- `Initialize_WithNonExistentDirectory_CreatesDirectory`
- `CreateTables_CreatesAllRequiredTables`
- `Close_AfterInitialization_ClosesConnection`
- `Close_WithoutInitialization_DoesNotThrow`
- `CheckDatabaseIntegrity_AfterInitialization_ReturnsTrue`
- `GetDataVersion_AfterInitialization_ReturnsNonNegativeValue`
- `GetDataVersion_AfterWrite_ReturnsIncrementedValue`
- `GetDataVersion_AfterReadOnly_ReturnsSameValue`

---

### GAP 2 — `UnitOfWorkSync.RunInTransaction` (No coverage)

`UnitOfWorkSyncTests.cs` does not contain any test for `RunInTransaction`. This is the method callers use for all atomic multi-step write operations. Two tests are required:

- `RunInTransaction_OnSuccess_CommitsAllWrites` — verifies all rows inside the transaction are visible after completion
- `RunInTransaction_OnException_RollsBackAllWrites` — verifies no rows persist if the action throws

These should be added to `UnitOfWorkSyncTests.cs`.

---

### GAP 3 — `UnitOfWork.RunInTransactionAsync` (No coverage, async path)

The async `UnitOfWorkTests.cs` file tests `BeginTransactionAsync`, `CommitTransactionAsync`, and `RollbackTransactionAsync` — methods that **no longer exist** on `IUnitOfWork` or `UnitOfWork`. These tests are testing a removed API and must be replaced.

The current `IUnitOfWork` interface exposes `RunInTransactionAsync(Action<SQLiteConnection> action)`. Tests required:

- `RunInTransactionAsync_OnSuccess_CommitsAllWrites`
- `RunInTransactionAsync_OnException_RollsBackAllWrites`

The three stale tests (`BeginTransactionAsync_CompletesSuccessfully`, `CommitTransactionAsync_CompletesSuccessfully`, `RollbackTransactionAsync_CompletesSuccessfully`) must be removed.

---

### GAP 4 — `GetDataVersionAsync` (No coverage, async path)

`IDatabaseService.GetDataVersionAsync()` is implemented in `DatabaseService` but has no tests in any of the `DatabaseServiceTests_*` files. Three tests are required, to be added to `DatabaseServiceTests_SqlOperations.cs` or a dedicated `DatabaseServiceTests_Hardening.cs`:

- `GetDataVersionAsync_AfterInitialization_ReturnsNonNegativeValue`
- `GetDataVersionAsync_AfterWrite_ReturnsIncrementedValue`
- `GetDataVersionAsync_AfterReadOnly_ReturnsSameValue`

---

## Key Implementation Standards

### ✅ Test Style Guidelines
- NUnit framework with `[TestFixture]`, `[Test]`, `[SetUp]`, `[TearDown]`
- AAA (Arrange-Act-Assert) pattern with clear section comments
- Test naming: `MethodName_Scenario_ExpectedBehavior`
- `Assert.Multiple()` for related assertions
- NUnit constraint model (`Is.EqualTo`, `Does.Contain`, `Has.Count`)

### ✅ Database Test Best Practices
- ORM-first approach using sqlite-net-pcl
- Unique test database paths with GUIDs
- Proper Setup/TearDown with resource cleanup
- All tests are independent and can run in any order
- No mocking — tests use real SQLite connections

### ✅ Synchronous Implementation Standards
- All methods are synchronous (no `async`/`await`)
- Uses `SQLiteConnection` instead of `SQLiteAsyncConnection`
- Method naming without "Async" suffix

### ✅ Windows Line Endings
- All files use CRLF line endings

---

## File Location

```
duHastNet.DocManager.Core.Tests/
├── Services/
│   ├── DatabaseServiceTests_Initialization.cs
│   ├── DatabaseServiceTests_ConnectionManagement.cs
│   ├── DatabaseServiceTests_TablesAndIndexes.cs
│   ├── DatabaseServiceTests_SqlOperations.cs
│   ├── DatabaseServiceTests_MaintenanceOperations.cs
│   ├── DatabaseServiceTests_Dispose.cs
│   ├── DatabaseServiceTests_AdditionalScenarios.cs
│   └── DatabaseServiceTests_Sync.cs          ← TO BE CREATED
│
│   └── Repositories/
│       ├── BaseRepositorySyncTests.cs
│       ├── UnitOfWorkTests.cs                 ← NEEDS UPDATES (stale + missing)
│       ├── UnitOfWorkSyncTests.cs             ← NEEDS UPDATES (missing)
│       ├── CustomFieldDefinitionRepositorySyncTests.cs
│       ├── CustomPropertyRepositorySyncTests.cs
│       ├── DocumentRepositorySyncTests.cs
│       └── RevisionRepositorySyncTests.cs
```

---

## Dependencies

- NUnit Framework
- sqlite-net-pcl
- System.IO
- All sync and async repository and service implementations in duHastNet.DocManager.Core
