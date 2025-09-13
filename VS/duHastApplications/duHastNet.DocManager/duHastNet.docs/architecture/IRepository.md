Here's the generic IRepository<T> interface with:
Core CRUD operations:

GetByIdAsync - Single entity retrieval
GetAllAsync - Get all entities
FindAsync - Query with predicate
FirstOrDefaultAsync - Single or null result
InsertAsync/UpdateAsync/DeleteAsync - Basic modifications

Additional useful methods:

CountAsync - Both total count and conditional count
ExistsAsync - Check existence without retrieving data
Batch operations (InsertAllAsync, UpdateAllAsync, DeleteAllAsync) - For performance with multiple entities

Key design decisions:

Generic constraint where T : class, new() - Required for sqlite-net-pcl
All methods are async - Modern best practice for data access
Returns int for modification operations - Number of affected rows
Uses Expression<Func<T, bool>> - Enables LINQ queries that translate to SQL

This provides a consistent interface that all your specific repositories (Revision, Document, CustomProperty) will implement.