# IDatabaseService

Interface for database connection and management using sqlite-net-pcl. Provides both asynchronous and synchronous database operations. Implemented by `DatabaseService`.

---

## Architecture Summary

`IDatabaseService` / `DatabaseService` is built entirely on **sqlite-net-pcl**. No separate low-level SQLite package is required.

### sqlite-net-pcl Integration
- **Direct connection exposure**: both `SQLiteAsyncConnection` and `SQLiteConnection` are exposed for use by repositories
- **ORM operations** via the async connection: `CreateTablesAsync<T>()`, `InsertAsync()`, `UpdateAsync()`, `DeleteAsync()`, `Table<T>().Where().ToListAsync()`, `RunInTransactionAsync()`
- **ORM operations** via the sync connection: `CreateTable<T>()`, `Insert()`, `Update()`, `Delete()`, `Table<T>().Where().ToList()`, `RunInTransaction()`
- **Raw SQL** via `ExecuteAsync` / `ExecuteScalarAsync` (async) and `Execute` / `ExecuteScalar` (sync) for operations not covered by the ORM: PRAGMAs, custom indexes, integrity checks, and diagnostics

### Dual Connection Design
`IDatabaseService` exposes two connections:

| Connection | Type | Path |
|---|---|---|
| `Connection` | `SQLiteAsyncConnection` | Used by the WPF standalone application |
| `SyncConnection` | `SQLiteConnection` | Used by the Revit plugin via IronPython/PyRevit |

The sync connection exists solely to support IronPython compatibility. IronPython cannot consume `async`/`await` patterns, so the Revit plugin must use the synchronous surface throughout.

### Busy Timeout
Both connections are configured with a **5-second busy timeout** immediately after creation:
- Async connection: configured via `PRAGMA busy_timeout = 5000` (the `SQLiteAsyncConnection` type does not expose `BusyTimeout` as a property)
- Sync connection: configured via `_syncConnection.BusyTimeout = TimeSpan.FromSeconds(5)`

This causes SQLite to wait and retry before throwing `SQLiteBusyException` when a second writer hits a file lock. For 2–3 users with infrequent simultaneous writes, this eliminates the vast majority of collision errors.

### Repository Pattern
Repositories and the Unit of Work are built on top of `IDatabaseService`. Business logic never holds a reference to `IDatabaseService` directly — it accesses data through `IUnitOfWork` (async) or `IUnitOfWorkSync` (sync). `IDatabaseService` is a construction-time dependency of those classes only.

---

## Interface Members

### Properties

| Member | Type | Description |
|---|---|---|
| `Connection` | `SQLiteAsyncConnection` | The async database connection. Throws `InvalidOperationException` if accessed before `InitializeAsync` is called. |
| `SyncConnection` | `SQLiteConnection` | The sync database connection. Throws `InvalidOperationException` if accessed before `Initialize` is called. |
| `IsInitialized` | `bool` | Returns `true` if either connection has been initialised. |
| `DatabasePath` | `string?` | The path to the current database file. `null` before initialisation or after close. |

---

### Async Methods

#### `InitializeAsync(string databasePath)`
Sets up the async connection to the database at the specified path. Creates the directory structure if it does not exist, opens the connection, applies the busy timeout, and calls `CreateTablesAsync`. If the service was already initialised, the existing async connection is closed before the new one is opened.

Throws `ArgumentNullException` if `databasePath` is null. Throws `ArgumentException` if `databasePath` is empty or whitespace.

---

#### `CreateTablesAsync()`
Creates all required tables using sqlite-net-pcl's ORM attribute mapping. Tables created: `Revision`, `Document`, `CustomFieldDefinition`, `CustomProperty`. This is called automatically by `InitializeAsync` and does not need to be called separately under normal use.

---

#### `CloseAsync()`
Closes the async connection and sets `DatabasePath` to null. The connection is managed by this service; callers should not close it directly.

---

#### `CheckDatabaseIntegrityAsync()`
Lightweight connectivity test. Executes a simple query against `sqlite_master` and returns `true` if the connection can execute queries without throwing. Returns `false` on any exception.

> **Note:** This is a connectivity test, not a structural integrity check. It does not run `PRAGMA integrity_check` or validate table schemas. It confirms the connection is functional, not that the database is corruption-free.

---

#### `GetDataVersionAsync()`
Returns the current value of SQLite's `PRAGMA data_version` for this connection. The value increments whenever any connection writes to the database file, regardless of which process or user made the write.

This is used by the standalone WPF application to detect changes made by Revit plugin users. The recommended polling interval is 30–60 seconds using a `PeriodicTimer`. When the value has increased since the last check, the affected data should be reloaded.

```csharp
private int _lastDataVersion = -1;
private PeriodicTimer? _pollingTimer;

private async Task StartPollingAsync()
{
    _pollingTimer = new PeriodicTimer(TimeSpan.FromSeconds(30));
    while (await _pollingTimer.WaitForNextTickAsync())
    {
        var current = await _databaseService.GetDataVersionAsync();
        if (_lastDataVersion >= 0 && current != _lastDataVersion)
        {
            await RefreshAsync();
        }
        _lastDataVersion = current;
    }
}
```

The Revit plugin does not poll — it is the writer.

---

### Sync Methods

The sync methods mirror the async surface exactly. They exist solely to support the Revit plugin, which runs under IronPython and cannot use `async`/`await`.

#### `Initialize(string databasePath)`
Sync equivalent of `InitializeAsync`. Opens the sync connection, applies the 5-second `BusyTimeout`, and calls `CreateTables`.

---

#### `CreateTables()`
Sync equivalent of `CreateTablesAsync`. Creates `Revision`, `Document`, `CustomFieldDefinition`, and `CustomProperty` tables using the ORM.

---

#### `Close()`
Sync equivalent of `CloseAsync`.

---

#### `CheckDatabaseIntegrity()`
Sync equivalent of `CheckDatabaseIntegrityAsync`. Same lightweight connectivity-test semantics — not a structural integrity check.

---

#### `GetDataVersion()`
Sync equivalent of `GetDataVersionAsync`. The Revit plugin does not need to call this — it is the writer, not the observer. This method is available for completeness and future use.

---

## Design Notes

### What IDatabaseService Does Not Do
- It does not manage transactions. Atomic multi-step writes go through `IUnitOfWork.RunInTransactionAsync` (async) or `IUnitOfWorkSync.RunInTransaction` (sync).
- It does not expose query or CRUD methods. All data access goes through the repository interfaces.
- It does not enable WAL mode. WAL mode is unreliable on network shares (SMB/CIFS) and is not appropriate for this deployment pattern.

### Future Upgrade Path
The `IDatabaseService` abstraction is the correct seam if the backend storage ever needs to change. Adding a lightweight REST or gRPC service layer, or migrating to SQL Server Express, requires changes only to `DatabaseService` and the repository classes. All ViewModel and business logic code remains untouched.
