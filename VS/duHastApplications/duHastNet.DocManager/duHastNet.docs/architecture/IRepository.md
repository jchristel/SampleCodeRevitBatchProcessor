# IRepository and IRepositorySync

DocManager has two parallel repository interfaces: `IRepository<T>` for the async path used by the WPF standalone application, and `IRepositorySync<T>` for the sync path used by the Revit plugin via IronPython/PyRevit. Both are implemented by their respective base classes (`BaseRepository<T>` and `BaseRepositorySync<T>`) and consumed through the Unit of Work interfaces (`IUnitOfWork` and `IUnitOfWorkSync`).

---

## IRepository\<T\> (Async)

Generic repository interface for async CRUD operations. All concrete repositories (`RevisionRepository`, `DocumentRepository`, `CustomPropertyRepository`, `CustomFieldDefinitionRepository`) extend `BaseRepository<T>` which provides the default implementation of every method below.

### Type Constraint
```csharp
where T : class, new()
```
Both constraints are required by sqlite-net-pcl: `class` because the ORM works with reference types, and `new()` because sqlite-net-pcl instantiates entities via a default constructor when materialising query results.

### Methods

#### Queries

| Method | Returns | Description |
|---|---|---|
| `GetByIdAsync(int id)` | `Task<T?>` | Returns the entity with the given primary key, or `null` if not found. Uses sqlite-net-pcl's `FindAsync<T>(id)`. |
| `GetAllAsync()` | `Task<List<T>>` | Returns all entities of type `T`. |
| `FindAsync(Expression<Func<T, bool>> predicate)` | `Task<List<T>>` | Returns all entities matching the predicate. The expression is translated to SQL by sqlite-net-pcl's LINQ provider. |
| `FirstOrDefaultAsync(Expression<Func<T, bool>> predicate)` | `Task<T?>` | Returns the first matching entity, or `null`. |
| `CountAsync()` | `Task<int>` | Returns the total number of entities of type `T`. |
| `CountAsync(Expression<Func<T, bool>> predicate)` | `Task<int>` | Returns the count of entities matching the predicate. |
| `ExistsAsync(Expression<Func<T, bool>> predicate)` | `Task<bool>` | Returns `true` if any entity matches the predicate. Implemented as `CountAsync(predicate) > 0`. |

#### Single-Entity Writes

| Method | Returns | Description |
|---|---|---|
| `InsertAsync(T entity)` | `Task<int>` | Inserts the entity and returns the number of rows affected. sqlite-net-pcl automatically sets the `Id` property on the entity after insert. |
| `UpdateAsync(T entity)` | `Task<int>` | Updates the entity matched by primary key. Returns rows affected. |
| `DeleteAsync(T entity)` | `Task<int>` | Deletes the entity matched by primary key. Returns rows affected. |
| `DeleteAsync(int id)` | `Task<int>` | Deletes the entity with the given primary key. Returns rows affected. |

Single-row operations do not require explicit transactions — sqlite-net-pcl wraps each single statement in an implicit transaction.

#### Batch Writes

| Method | Returns | Description |
|---|---|---|
| `InsertAllAsync(IEnumerable<T> entities)` | `Task<int>` | Inserts all entities atomically. sqlite-net-pcl wraps `InsertAllAsync` in an internal transaction — all rows succeed or none are committed. |
| `UpdateAllAsync(IEnumerable<T> entities)` | `Task<int>` | Updates all entities atomically. sqlite-net-pcl wraps `UpdateAllAsync` in an internal transaction. |
| `DeleteAllAsync(IEnumerable<T> entities)` | `Task<int>` | Deletes all entities atomically. Implemented with an explicit `RunInTransactionAsync` in `BaseRepository<T>` because sqlite-net-pcl does not provide a built-in `DeleteAllAsync`. All deletions succeed or none are committed. |

All batch operations are atomic — if any item fails, the entire batch is rolled back.

---

## IRepositorySync\<T\> (Sync)

Mirrors `IRepository<T>` exactly, but with synchronous signatures. Exists solely to support the Revit plugin, which runs under IronPython and cannot consume `async`/`await`.

### Type Constraint
```csharp
where T : class
```
Note: the sync interface uses `where T : class` only (without `new()`). The `new()` constraint is applied by `BaseRepositorySync<T>` in its concrete implementation, keeping the interface itself slightly more permissive.

### Methods

The sync interface provides exact counterparts to every method in `IRepository<T>`, with synchronous signatures:

| Async (`IRepository<T>`) | Sync (`IRepositorySync<T>`) |
|---|---|
| `GetByIdAsync(int id)` | `GetById(int id)` |
| `GetAllAsync()` | `GetAll()` |
| `FindAsync(predicate)` | `Find(predicate)` |
| `FirstOrDefaultAsync(predicate)` | `FirstOrDefault(predicate)` |
| `InsertAsync(entity)` | `Insert(entity)` |
| `UpdateAsync(entity)` | `Update(entity)` |
| `DeleteAsync(entity)` | `Delete(entity)` |
| `DeleteAsync(int id)` | `Delete(int id)` |
| `CountAsync()` | `Count()` |
| `CountAsync(predicate)` | `Count(predicate)` |
| `ExistsAsync(predicate)` | `Exists(predicate)` |
| `InsertAllAsync(entities)` | `InsertAll(entities)` |
| `UpdateAllAsync(entities)` | `UpdateAll(entities)` |
| `DeleteAllAsync(entities)` | `DeleteAll(entities)` |

Batch operation atomicity follows the same rules as the async interface. `DeleteAll` uses an explicit `RunInTransaction` in `BaseRepositorySync<T>`.

---

## Transaction Handling

Neither `IRepository<T>` nor `IRepositorySync<T>` expose transaction methods. Multi-step atomic write operations are coordinated through the Unit of Work:

- **Async**: `IUnitOfWork.RunInTransactionAsync(Action<SQLiteConnection> action)`
- **Sync**: `IUnitOfWorkSync.RunInTransaction(Action action)`

Any operation that writes more than one row across one or more repositories must be wrapped in the appropriate `RunInTransaction` call via the Unit of Work. Single-row writes and the batch methods on these interfaces handle their own atomicity internally.

```csharp
// Example: inserting a revision and its documents atomically (async path)
await _unitOfWork.RunInTransactionAsync(conn =>
{
    conn.Insert(revision);
    foreach (var doc in documents)
    {
        doc.RevisionId = revision.Id;
        conn.Insert(doc);
    }
});
```

---

## Concrete Repositories

| Interface | Sync Interface | Concrete (Async) | Concrete (Sync) |
|---|---|---|---|
| `IRevisionRepository` | `IRevisionRepositorySync` | `RevisionRepository` | `RevisionRepositorySync` |
| `IDocumentRepository` | `IDocumentRepositorySync` | `DocumentRepository` | `DocumentRepositorySync` |
| `ICustomPropertyRepository` | `ICustomPropertyRepositorySync` | `CustomPropertyRepository` | `CustomPropertyRepositorySync` |
| `ICustomFieldDefinitionRepository` | `ICustomFieldDefinitionRepositorySync` | `CustomFieldDefinitionRepository` | `CustomFieldDefinitionRepositorySync` |

Each concrete repository extends `BaseRepository<T>` (async) or `BaseRepositorySync<T>` (sync) and may override methods to add domain-specific behaviour — for example, enforcing uniqueness rules or returning entities in a specific order.
