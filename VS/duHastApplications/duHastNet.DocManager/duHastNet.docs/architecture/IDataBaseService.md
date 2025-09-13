Here's the IDatabaseService interface with comprehensive database management capabilities:
Core Database Operations:

Connection - Direct access to SQLite connection
InitializeAsync - Setup database with proper configuration
CreateTablesAsync - Creates all tables (Revisions, Documents, CustomProperties)
CreateIndexesAsync - Performance indexes
CloseAsync - Clean shutdown

Database Management:

IsInitialized & DatabasePath - State tracking
CreateBackupAsync & RestoreFromBackupAsync - Data protection
OptimizeDatabaseAsync - VACUUM and ANALYZE for performance
GetDatabaseSizeAsync - Storage monitoring
CheckDatabaseIntegrityAsync - Data validation

Advanced Operations:

ExecuteAsync - Raw SQL commands (for schema changes, custom operations)
QueryAsync<T> - Raw SQL queries with typed results (for complex reporting)

This interface abstracts all SQLite-specific operations and provides everything needed for robust database management. The implementation will handle SQLite configuration, connection lifecycle, and provide a foundation for all repository operations.