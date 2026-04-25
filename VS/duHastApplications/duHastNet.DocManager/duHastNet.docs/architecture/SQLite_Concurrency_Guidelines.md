# DocManager — SQLite Concurrency Guidelines
*Hardening the database layer for multi-user access*

---

## 1. Context and Usage Pattern

DocManager operates in two modes that both write to the same SQLite database:

| Mode | Description |
|---|---|
| DocManager Standalone | Desktop WPF application. Users browse, review, and manage documents. |
| DocManager for Revit | Revit plugin. Users add or update documents directly from a Revit model. |

The expected concurrent usage profile is:

- Maximum 2–3 users at any one time
- Workflow is loosely sequential: one user notices missing documents, asks another to add them via Revit, then re-checks
- Simultaneous writes are rare and brief — two Revit users saving at the exact same moment is the most likely collision scenario

> **Conclusion:** SQLite is appropriate for this usage pattern. The scenarios below are hardening measures, not a reason to replace the database.

---

## 2. How SQLite Handles Concurrent Access

SQLite uses file-level locking, not row or table locking. Key behaviours to understand:

| Scenario | Behaviour | Risk |
|---|---|---|
| Multiple readers | All succeed simultaneously | None |
| One writer + readers | Writer locks briefly; readers may wait | Low |
| Two writers simultaneously | Second writer waits for busy timeout, then retries or throws SQLiteBusyException | Low-Medium |
| Network share (multiple machines) | File locking is unreliable on SMB/CIFS | Medium — mitigate with busy timeout |

> **Network Share Warning:** SQLite file locking is not guaranteed to work correctly across machines on a network share (SMB/CIFS). For this usage pattern the risk is acceptable, but a busy timeout must be configured to handle brief collisions gracefully.

---

## 3. Required Implementation Changes

The following changes must be made to harden the database layer. They are listed in priority order.

---

### 3.1 Add a Busy Timeout (Priority: High)

Without a busy timeout, if two users write at the same moment SQLite immediately throws `SQLiteBusyException`. A busy timeout instructs SQLite to wait and retry before giving up. This eliminates the vast majority of collision errors for this usage pattern.

In `DatabaseService.cs`, apply the timeout immediately after creating each connection:

**Async connection (`InitializeAsync` method):**
```csharp
_connection = new SQLiteAsyncConnection(databasePath);
_connection.BusyTimeout = TimeSpan.FromSeconds(5);
```

**Sync connection (`Initialize` method):**
```csharp
_syncConnection = new SQLiteConnection(databasePath);
_syncConnection.BusyTimeout = TimeSpan.FromSeconds(5);
```

> **Why 5 seconds?** For 2–3 users with infrequent simultaneous writes, 5 seconds is far more than needed. A brief write lock is typically released in milliseconds. 5 seconds provides comfortable headroom without making the UI feel unresponsive if something goes wrong.

---

### 3.2 Fix No-Op Transactions (Priority: High)

The current `UnitOfWork` implementation has `BeginTransactionAsync`, `CommitTransactionAsync`, and `RollbackTransactionAsync` as no-ops. This means that multi-step write operations — for example, inserting a `Document` and its associated `CustomProperties` — are not atomic. If a failure occurs mid-way, the database is left in a partial state.

Any operation that writes more than one row must be wrapped in `RunInTransactionAsync`. This applies to both the async and sync connection paths.

**Example — inserting a document with custom properties:**
```csharp
await _connection.RunInTransactionAsync(conn =>
{
    conn.Insert(document);
    conn.Insert(customProperty1);
    conn.Insert(customProperty2);
});
```

**For the sync connection:**
```csharp
_syncConnection.RunInTransaction(() =>
{
    _syncConnection.Insert(document);
    _syncConnection.Insert(customProperty);
});
```

> **Scope:** Review all repository methods that perform more than a single insert, update, or delete. Any multi-step operation is a candidate for wrapping in a transaction. Single-row operations do not need explicit transactions.

---

### 3.3 Detect External Database Changes (Priority: Medium)

When the standalone app is open and a Revit user adds documents, the standalone user currently has no way of knowing the database changed without manually refreshing. A polling mechanism using SQLite's built-in `data_version` pragma provides a lightweight, schema-free way to detect this.

**How `data_version` works:**
- SQLite maintains an integer counter per connection that increments whenever a write occurs from any connection
- Reading `PRAGMA data_version` is extremely cheap — it does not scan tables
- If the value has increased since the last check, the database was modified externally

**Step 1 — Add method to `IDatabaseService`:**
```csharp
Task<int> GetDataVersionAsync();
int GetDataVersion();
```

**Step 2 — Implement in `DatabaseService`:**
```csharp
public async Task<int> GetDataVersionAsync()
{
    return await Connection.ExecuteScalarAsync<int>("PRAGMA data_version");
}

public int GetDataVersion()
{
    return SyncConnection.ExecuteScalar<int>("PRAGMA data_version");
}
```

**Step 3 — Poll in the standalone ViewModel:**

Use a `PeriodicTimer` or `DispatcherTimer` in the main ViewModel. A 30–60 second interval is appropriate for this workflow.

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
            // Database was updated externally — reload affected data
            await RefreshAsync();
        }
        _lastDataVersion = current;
    }
}
```

> **Note on Revit plugin:** The Revit plugin does not need polling — it is the writer. Polling is only needed in the standalone app, which is the passive observer waiting for Revit users to complete their work.

---

## 4. What Is Not Required For This Usage Pattern

The following are valid solutions for high-concurrency scenarios but are unnecessary overhead for 2–3 users with infrequent simultaneous writes:

- **WAL (Write-Ahead Log) mode** — beneficial on a single machine but unreliable over a network share, and not needed for this write frequency
- **A dedicated database server (PostgreSQL, SQL Server)** — appropriate for many concurrent writers; overkill here
- **A REST/gRPC service layer in front of SQLite** — useful for serialising writes under load; not needed for this usage pattern
- **Row-level or optimistic locking** — not warranted when collisions are this infrequent

---

## 5. Implementation Checklist

Work through the following items in order:

| # | Task | File | Priority |
|---|---|---|---|
| 1 | Set `BusyTimeout = TimeSpan.FromSeconds(5)` on async connection after creation | `DatabaseService.cs` — `InitializeAsync` | **High** |
| 2 | Set `BusyTimeout = TimeSpan.FromSeconds(5)` on sync connection after creation | `DatabaseService.cs` — `Initialize` | **High** |
| 3 | Add `GetDataVersionAsync()` and `GetDataVersion()` to `IDatabaseService` interface | `IDatabaseService.cs` | Medium |
| 4 | Implement `GetDataVersionAsync()` and `GetDataVersion()` in `DatabaseService` | `DatabaseService.cs` | Medium |
| 5 | Audit all repository methods for multi-step writes and wrap in `RunInTransactionAsync` or `RunInTransaction` | All Repository classes | **High** |
| 6 | Implement polling timer in standalone ViewModel using `data_version` | Main ViewModel | Medium |
| 7 | Wire up `RefreshAsync` to reload only affected data when version change detected | Relevant ViewModels | Medium |

---

## 6. Future Upgrade Path

If the usage pattern grows significantly beyond 2–3 users, or if network share corruption is observed in practice, the recommended upgrade path is:

**Option A — Add a lightweight service layer (lower effort)**

Run a small REST or gRPC service on the machine hosting the database. All clients talk to the service rather than directly to the file. The existing `IDatabaseService` abstraction is the correct seam for this change — repository and ViewModel code remains untouched.

**Option B — Migrate to SQL Server Express (higher effort, fully robust)**

SQL Server Express is free, integrates naturally into Windows environments, and supports true concurrent writes. The repository pattern already isolates all database access, so the blast radius of this migration is contained to the repository and `DatabaseService` classes only.

> **Design Note:** The repository pattern and `IDatabaseService` abstraction already in place mean that either upgrade path is a bounded, manageable change. The application is not locked into SQLite.
