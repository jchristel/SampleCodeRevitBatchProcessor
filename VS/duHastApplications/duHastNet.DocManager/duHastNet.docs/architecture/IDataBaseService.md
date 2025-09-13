Here's the IDatabaseService interface with comprehensive database management capabilities:

## Architecture Summary

**IDatabaseService/DatabaseService heavily relies on sqlite-net-pcl:**

### Primary sqlite-net-pcl Integration:
- **Direct Exposure**: `SQLiteAsyncConnection Connection { get; }` - exposes sqlite-net-pcl connection directly
- **ORM Operations**: Uses sqlite-net-pcl's built-in ORM features:
  - `CreateTableAsync<T>()` with attribute mapping
  - `InsertAsync()`, `UpdateAsync()`, `DeleteAsync()` with automatic ID handling
  - `Table<T>().Where().ToListAsync()` LINQ-to-SQL queries
  - `RunInTransactionAsync()` for transaction management

### Raw SQL for Advanced Operations:
Some operations require raw SQL where sqlite-net-pcl doesn't provide abstractions:
- **Database Maintenance**: `VACUUM`, `ANALYZE`, `REINDEX` commands
- **Custom Indexes**: Complex index creation beyond attributes
- **Integrity Checks**: `PRAGMA integrity_check` and diagnostics
- **Statistics**: Custom reporting queries and schema inspection

## Core Database Operations:

- **Connection** - Direct access to SQLite connection (sqlite-net-pcl)
- **InitializeAsync** - Setup database with proper configuration
- **CreateTablesAsync** - Creates all tables using sqlite-net-pcl ORM (Revisions, Documents, CustomProperties)
- **CloseAsync** - Clean shutdown

## Database Management:

- **IsInitialized & DatabasePath** - State tracking
- **CheckDatabaseIntegrityAsync** - Data validation using PRAGMA commands

## Design Philosophy:

The interface abstracts SQLite-specific operations while leveraging sqlite-net-pcl's strengths:
- **High-level operations** use sqlite-net-pcl ORM for type safety and convenience
- **Low-level operations** use raw SQL for performance and advanced features not available in ORM
- **Repository pattern** built on top provides business-focused abstractions
- **File-based approach** enables project-specific database isolation

This hybrid approach maximizes sqlite-net-pcl's productivity benefits while maintaining access to SQLite's full feature set when needed.