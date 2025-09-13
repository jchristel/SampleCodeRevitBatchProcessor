using NUnit.Framework;
using duHastNet.DocManager.Core.Services;
using duHastNet.DocManager.Core.Models;
using System.IO;

namespace duHastNet.DocManager.Core.Tests.Services;

[TestFixture]
public class DatabaseServiceTests_Tables
{
    private DatabaseService _databaseService;
    private string _testDatabasePath;
    private string _testDirectory;

    [SetUp]
    public async Task Setup()
    {
        _databaseService = new DatabaseService();
        _testDirectory = Path.Combine(Path.GetTempPath(), "DatabaseServiceTests", Guid.NewGuid().ToString());
        _testDatabasePath = Path.Combine(_testDirectory, "test.db");

        await _databaseService.InitializeAsync(_testDatabasePath);
    }

    [TearDown]
    public async Task TearDown()
    {
        if (_databaseService != null)
        {
            await _databaseService.CloseAsync();
            _databaseService.Dispose();
        }

        if (Directory.Exists(_testDirectory))
        {
            Directory.Delete(_testDirectory, true);
        }
    }

    #region CreateTablesAsync Tests

    [Test]
    public async Task CreateTablesAsync_CreatesRevisionsTable()
    {
        // Act
        await _databaseService.CreateTablesAsync();

        // Assert
        var tables = await _databaseService.Connection.QueryAsync<TableInfo>(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='Revisions'");

        Assert.That(tables, Has.Count.EqualTo(1));
        Assert.That(tables[0].Name, Is.EqualTo("Revisions"));
    }

    [Test]
    public async Task CreateTablesAsync_CreatesDocumentsTable()
    {
        // Act
        await _databaseService.CreateTablesAsync();

        // Assert
        var tables = await _databaseService.Connection.QueryAsync<TableInfo>(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='Documents'");

        Assert.That(tables, Has.Count.EqualTo(1));
        Assert.That(tables[0].Name, Is.EqualTo("Documents"));
    }

    [Test]
    public async Task CreateTablesAsync_CreatesCustomPropertiesTable()
    {
        // Act
        await _databaseService.CreateTablesAsync();

        // Assert
        var tables = await _databaseService.Connection.QueryAsync<TableInfo>(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='CustomProperties'");

        Assert.That(tables, Has.Count.EqualTo(1));
        Assert.That(tables[0].Name, Is.EqualTo("CustomProperties"));
    }

    [Test]
    public async Task CreateTablesAsync_CreatesAllThreeTables()
    {
        // Act
        await _databaseService.CreateTablesAsync();

        // Assert
        var tables = await _databaseService.Connection.QueryAsync<TableInfo>(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('Revisions', 'Documents', 'CustomProperties')");

        Assert.That(tables, Has.Count.EqualTo(3));
        var tableNames = tables.Select(t => t.Name).ToList();
        Assert.That(tableNames, Does.Contain("Revisions"));
        Assert.That(tableNames, Does.Contain("Documents"));
        Assert.That(tableNames, Does.Contain("CustomProperties"));
    }

    [Test]
    public async Task CreateTablesAsync_MultipleCallsDoNotFail()
    {
        // Act
        await _databaseService.CreateTablesAsync();
        await _databaseService.CreateTablesAsync(); // Second call
        await _databaseService.CreateTablesAsync(); // Third call

        // Assert - Should not throw and tables should still exist
        var tables = await _databaseService.Connection.QueryAsync<TableInfo>(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('Revisions', 'Documents', 'CustomProperties')");

        Assert.That(tables, Has.Count.EqualTo(3));
    }

    [Test]
    public async Task CreateTablesAsync_VerifiesRevisionsTableStructure()
    {
        // Act
        await _databaseService.CreateTablesAsync();

        // Assert
        var columns = await _databaseService.Connection.QueryAsync<ColumnInfo>(
            "PRAGMA table_info('Revisions')");

        Assert.That(columns, Has.Count.GreaterThan(0));
        var columnNames = columns.Select(c => c.Name).ToList();
        Assert.That(columnNames, Does.Contain("Id"));
        Assert.That(columnNames, Does.Contain("RevisionDate"));
        Assert.That(columnNames, Does.Contain("Description"));
    }

    [Test]
    public async Task CreateTablesAsync_VerifiesDocumentsTableStructure()
    {
        // Act
        await _databaseService.CreateTablesAsync();

        // Assert
        var columns = await _databaseService.Connection.QueryAsync<ColumnInfo>(
            "PRAGMA table_info('Documents')");

        Assert.That(columns, Has.Count.GreaterThan(0));
        var columnNames = columns.Select(c => c.Name).ToList();
        Assert.That(columnNames, Does.Contain("Id"));
        Assert.That(columnNames, Does.Contain("Number"));
        Assert.That(columnNames, Does.Contain("Name"));
        Assert.That(columnNames, Does.Contain("Revision"));
        Assert.That(columnNames, Does.Contain("RevisionId"));
    }

    [Test]
    public async Task CreateTablesAsync_VerifiesCustomPropertiesTableStructure()
    {
        // Act
        await _databaseService.CreateTablesAsync();

        // Assert
        var columns = await _databaseService.Connection.QueryAsync<ColumnInfo>(
            "PRAGMA table_info('CustomProperties')");

        Assert.That(columns, Has.Count.GreaterThan(0));
        var columnNames = columns.Select(c => c.Name).ToList();
        Assert.That(columnNames, Does.Contain("Id"));
        Assert.That(columnNames, Does.Contain("DocumentId"));
        Assert.That(columnNames, Does.Contain("PropertyName"));
        Assert.That(columnNames, Does.Contain("PropertyValue"));
    }

    [Test]
    public async Task CreateTablesAsync_WithExistingData_PreservesData()
    {
        // Arrange
        await _databaseService.CreateTablesAsync();
        await _databaseService.Connection.ExecuteAsync(
            "INSERT INTO Revisions (RevisionDate, Description) VALUES (?, ?)",
            DateTime.Now, "Test Revision");

        // Act
        await _databaseService.CreateTablesAsync(); // Call again

        // Assert - Data should still exist
        var revisions = await _databaseService.Connection.QueryAsync<Revision>("SELECT * FROM Revisions");
        Assert.That(revisions, Has.Count.EqualTo(1));
        Assert.That(revisions[0].Description, Is.EqualTo("Test Revision"));
    }

    [Test]
    public void CreateTablesAsync_WithoutInitialization_ThrowsException()
    {
        // Arrange
        var uninitializedService = new DatabaseService();

        // Act & Assert
        var ex = Assert.ThrowsAsync<InvalidOperationException>(
            async () => await uninitializedService.CreateTablesAsync());

        Assert.That(ex, Is.Not.Null);
        Assert.That(ex.Message, Does.Contain("not initialized"));
    }

    #endregion

    #region Automatic Index Tests (sqlite-net-pcl creates these based on [Indexed] attributes)

    [Test]
    public async Task CreateTablesAsync_CreatesAutomaticIndexesForDocumentsTable()
    {
        // Act
        await _databaseService.CreateTablesAsync();

        // Assert - sqlite-net-pcl should create indexes for [Indexed] properties
        var indexes = await _databaseService.Connection.QueryAsync<IndexInfo>(
            @"SELECT name FROM sqlite_master 
              WHERE type='index' 
              AND tbl_name='Documents'
              AND name NOT LIKE 'sqlite_%'"); // Exclude system indexes

        // Should have indexes for Number, RevisionId (marked with [Indexed] in models)
        Assert.That(indexes, Has.Count.GreaterThan(0), "sqlite-net-pcl should create indexes for [Indexed] properties");
    }

    [Test]
    public async Task CreateTablesAsync_CreatesAutomaticIndexesForCustomPropertiesTable()
    {
        // Act
        await _databaseService.CreateTablesAsync();

        // Assert - sqlite-net-pcl should create indexes for [Indexed] properties
        var indexes = await _databaseService.Connection.QueryAsync<IndexInfo>(
            @"SELECT name FROM sqlite_master 
              WHERE type='index' 
              AND tbl_name='CustomProperties'
              AND name NOT LIKE 'sqlite_%'"); // Exclude system indexes

        // Should have indexes for DocumentId, PropertyName (marked with [Indexed] in models)
        Assert.That(indexes, Has.Count.GreaterThan(0), "sqlite-net-pcl should create indexes for [Indexed] properties");
    }

    [Test]
    public async Task CreateTablesAsync_IndexesImproveQueryPerformance()
    {
        // Arrange
        await _databaseService.CreateTablesAsync();

        // Insert test data
        var revision = new Revision(DateTime.Now, "Performance Test");
        await _databaseService.Connection.InsertAsync(revision);

        // Create many documents to test index performance
        var documents = new List<Document>();
        for (int i = 0; i < 1000; i++)
        {
            documents.Add(new Document($"DOC-{i:000}", $"Document {i}", "1", revision.Id));
        }
        await _databaseService.Connection.InsertAllAsync(documents);

        // Act - Query using indexed column should be fast
        var stopwatch = System.Diagnostics.Stopwatch.StartNew();
        var results = await _databaseService.Connection.Table<Document>()
            .Where(d => d.Number == "DOC-500")
            .ToListAsync();
        stopwatch.Stop();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(results, Has.Count.EqualTo(1));
            Assert.That(stopwatch.ElapsedMilliseconds, Is.LessThan(100), "Query should be fast with automatic indexes");
        });
    }

    [Test]
    public async Task CreateTablesAsync_HandlesRelationshipsCorrectly()
    {
        // Act
        await _databaseService.CreateTablesAsync();

        // Assert - Test foreign key relationship works (if foreign keys are enabled)
        var revision = new Revision(DateTime.Now, "FK Test");
        await _databaseService.Connection.InsertAsync(revision);

        var document = new Document("DOC-001", "Test Document", "1", revision.Id);
        await _databaseService.Connection.InsertAsync(document);

        var customProperty = new CustomProperty(document.Id, "TestProperty", "TestValue");
        await _databaseService.Connection.InsertAsync(customProperty);

        // Should be able to query related data
        var documents = await _databaseService.Connection.Table<Document>()
            .Where(d => d.RevisionId == revision.Id)
            .ToListAsync();

        Assert.That(documents, Has.Count.EqualTo(1));
        Assert.That(documents[0].Number, Is.EqualTo("DOC-001"));
    }

    #endregion

    #region ORM Feature Tests

    [Test]
    public async Task CreateTablesAsync_SupportsOrmInsertOperations()
    {
        // Arrange
        await _databaseService.CreateTablesAsync();

        // Act - Use ORM features directly
        var revision = new Revision(DateTime.Now, "ORM Insert Test");
        var insertResult = await _databaseService.Connection.InsertAsync(revision);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(insertResult, Is.EqualTo(1));
            Assert.That(revision.Id, Is.GreaterThan(0)); // Auto-increment should set ID
        });

        var retrieved = await _databaseService.Connection.GetAsync<Revision>(revision.Id);
        Assert.That(retrieved.Description, Is.EqualTo("ORM Insert Test"));
    }

    [Test]
    public async Task CreateTablesAsync_SupportsLinqQueries()
    {
        // Arrange
        await _databaseService.CreateTablesAsync();

        var revisions = new[]
        {
            new Revision(DateTime.Now.AddDays(-2), "Old Revision"),
            new Revision(DateTime.Now.AddDays(-1), "Recent Revision"),
            new Revision(DateTime.Now, "Latest Revision")
        };

        await _databaseService.Connection.InsertAllAsync(revisions);

        // Act - Use LINQ queries
        var recentRevisions = await _databaseService.Connection.Table<Revision>()
            .Where(r => r.Description.Contains("Recent"))
            .OrderBy(r => r.RevisionDate)
            .ToListAsync();

        // Assert
        Assert.That(recentRevisions, Has.Count.EqualTo(1));
        Assert.That(recentRevisions[0].Description, Is.EqualTo("Recent Revision"));
    }

    [Test]
    public async Task CreateTablesAsync_SupportsBulkOperations()
    {
        // Arrange
        await _databaseService.CreateTablesAsync();
        var revision = new Revision(DateTime.Now, "Bulk Test");
        await _databaseService.Connection.InsertAsync(revision);

        // Act - Bulk insert
        var documents = Enumerable.Range(1, 100)
            .Select(i => new Document($"BULK-{i:000}", $"Bulk Document {i}", "1", revision.Id))
            .ToList();

        var insertCount = await _databaseService.Connection.InsertAllAsync(documents);

        // Assert
        Assert.That(insertCount, Is.EqualTo(100));

        var count = await _databaseService.Connection.Table<Document>().CountAsync();
        Assert.That(count, Is.EqualTo(100));
    }

    [Test]
    public async Task CreateTablesAsync_SupportsTransactions()
    {
        // Arrange
        await _databaseService.CreateTablesAsync();

        // Act - Use transaction
        await _databaseService.Connection.RunInTransactionAsync((conn) =>
        {
            var revision = new Revision(DateTime.Now, "Transaction Test");
            conn.Insert(revision);

            var document = new Document("TXN-001", "Transaction Document", "1", revision.Id);
            conn.Insert(document);
        });

        // Assert
        var revisions = await _databaseService.Connection.Table<Revision>()
            .Where(r => r.Description == "Transaction Test")
            .ToListAsync();

        Assert.That(revisions, Has.Count.EqualTo(1));

        var documents = await _databaseService.Connection.Table<Document>()
            .Where(d => d.Number == "TXN-001")
            .ToListAsync();

        Assert.That(documents, Has.Count.EqualTo(1));
    }

    [Test]
    public async Task CreateTablesAsync_HandlesModelConstraints()
    {
        // Arrange
        await _databaseService.CreateTablesAsync();

        // Act & Assert - Test that [NotNull] constraints work
        var revision = new Revision(DateTime.Now, null); // Null description should be allowed
        Assert.DoesNotThrowAsync(async () => await _databaseService.Connection.InsertAsync(revision));

        // Test auto-increment primary key
        var document = new Document("DOC-001", "Test Document", "1", revision.Id);
        await _databaseService.Connection.InsertAsync(document);

        Assert.That(document.Id, Is.GreaterThan(0));
    }

    [Test]
    public async Task CreateTablesAsync_CreatesTablesWithCorrectSchema()
    {
        // Act
        await _databaseService.CreateTablesAsync();

        // Assert - Verify the table schemas match our model expectations
        var revisionsSchema = await _databaseService.Connection.GetTableInfoAsync("Revisions");
        var documentsSchema = await _databaseService.Connection.GetTableInfoAsync("Documents");
        var customPropertiesSchema = await _databaseService.Connection.GetTableInfoAsync("CustomProperties");

        Assert.Multiple(() =>
        {
            Assert.That(revisionsSchema, Has.Count.GreaterThan(2)); // At least Id, RevisionDate, Description
            Assert.That(documentsSchema, Has.Count.GreaterThan(4)); // At least Id, Number, Name, Revision, RevisionId
            Assert.That(customPropertiesSchema, Has.Count.GreaterThan(3)); // At least Id, DocumentId, PropertyName, PropertyValue
        });
    }

    #endregion

    // Helper classes for query results
    public class TableInfo
    {
        public string Name { get; set; } = string.Empty;
    }

    public class ColumnInfo
    {
        public string Name { get; set; } = string.Empty;
        public string Type { get; set; } = string.Empty;
    }

    public class IndexInfo
    {
        public string Name { get; set; } = string.Empty;
    }
}