using NUnit.Framework;
using duHastNet.DocManager.Core.Services;
using duHastNet.DocManager.Core.Models;
using System.IO;

namespace duHastNet.DocManager.Core.Tests.Services;

[TestFixture]
public class DatabaseServiceTests_MaintenanceOperations
{
    private DatabaseService _databaseService;
    private string _testDatabasePath;
    private string _testDirectory;

    [SetUp]
    public void Setup()
    {
        _databaseService = new DatabaseService();
        _testDirectory = Path.Combine(Path.GetTempPath(), "DatabaseServiceTests", Guid.NewGuid().ToString());
        _testDatabasePath = Path.Combine(_testDirectory, "test.db");
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

    #region CheckDatabaseIntegrityAsync Tests

    [Test]
    public async Task CheckDatabaseIntegrityAsync_WithValidDatabase_ReturnsTrue()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        // Act
        var result = await _databaseService.CheckDatabaseIntegrityAsync();

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public async Task CheckDatabaseIntegrityAsync_WithFreshDatabase_ReturnsTrue()
    {
        // Arrange - Fresh database with no tables yet
        await _databaseService.InitializeAsync(_testDatabasePath);

        // Act
        var result = await _databaseService.CheckDatabaseIntegrityAsync();

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public async Task CheckDatabaseIntegrityAsync_WithDataInTables_ReturnsTrue()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        // Add test data using sqlite-net-pcl ORM
        var revision = new Revision(DateTime.Now, "Integrity Test Revision");
        await _databaseService.Connection.InsertAsync(revision);

        var document = new Document("A-101", "Test Document", "1", revision.Id);
        await _databaseService.Connection.InsertAsync(document);

        var customProperty = new CustomProperty(document.Id, "TestProperty", "TestValue");
        await _databaseService.Connection.InsertAsync(customProperty);

        // Act
        var result = await _databaseService.CheckDatabaseIntegrityAsync();

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public async Task CheckDatabaseIntegrityAsync_WithLargeDataset_ReturnsTrue()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        // Create large dataset using sqlite-net-pcl batch operations
        var revisions = new List<Revision>();
        for (int i = 0; i < 100; i++)
        {
            revisions.Add(new Revision(DateTime.Now.AddDays(-i), $"Revision {i}"));
        }
        await _databaseService.Connection.InsertAllAsync(revisions);

        var documents = new List<Document>();
        for (int i = 0; i < 500; i++)
        {
            var revisionId = revisions[i % 100].Id;
            documents.Add(new Document($"DOC-{i:000}", $"Document {i}", "1", revisionId));
        }
        await _databaseService.Connection.InsertAllAsync(documents);

        // Act
        var result = await _databaseService.CheckDatabaseIntegrityAsync();

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public void CheckDatabaseIntegrityAsync_WithoutInitialization_ReturnsFalse()
    {
        // Act
        var result = _databaseService.CheckDatabaseIntegrityAsync().Result;

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public async Task CheckDatabaseIntegrityAsync_AfterClose_ReturnsFalse()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CloseAsync();

        // Act
        var result = await _databaseService.CheckDatabaseIntegrityAsync();

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public async Task CheckDatabaseIntegrityAsync_MultipleCalls_ConsistentResults()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        // Act - Multiple consecutive integrity checks
        var result1 = await _databaseService.CheckDatabaseIntegrityAsync();
        var result2 = await _databaseService.CheckDatabaseIntegrityAsync();
        var result3 = await _databaseService.CheckDatabaseIntegrityAsync();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result1, Is.True);
            Assert.That(result2, Is.True);
            Assert.That(result3, Is.True);
        });
    }

    [Test]
    public async Task CheckDatabaseIntegrityAsync_AfterHeavyOrmOperations_ReturnsTrue()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        // Perform heavy operations using sqlite-net-pcl ORM
        for (int i = 0; i < 50; i++)
        {
            var revision = new Revision(DateTime.Now.AddMinutes(-i), $"Heavy Operation {i}");
            await _databaseService.Connection.InsertAsync(revision);

            // Update the revision using ORM
            revision.Description = $"Updated Heavy Operation {i}";
            await _databaseService.Connection.UpdateAsync(revision);

            // Delete some revisions periodically using ORM
            if (i % 10 == 0 && i > 0)
            {
                await _databaseService.Connection.DeleteAsync<Revision>(revision.Id - 5);
            }
        }

        // Act
        var result = await _databaseService.CheckDatabaseIntegrityAsync();

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public async Task CheckDatabaseIntegrityAsync_WithTransactionOperations_ReturnsTrue()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        // Perform operations within sqlite-net-pcl transactions
        await _databaseService.Connection.RunInTransactionAsync((conn) =>
        {
            for (int i = 0; i < 10; i++)
            {
                var revision = new Revision(DateTime.Now.AddHours(-i), $"Transaction Revision {i}");
                conn.Insert(revision);

                var document = new Document($"TXN-{i:00}", $"Transaction Document {i}", "1", revision.Id);
                conn.Insert(document);
            }
        });

        // Act
        var result = await _databaseService.CheckDatabaseIntegrityAsync();

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public async Task CheckDatabaseIntegrityAsync_AfterDatabaseReopen_ReturnsTrue()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        // Add some data using ORM
        var revision = new Revision(DateTime.Now, "Reopen Test");
        await _databaseService.Connection.InsertAsync(revision);

        // Verify data exists before close
        var preCloseCount = await _databaseService.Connection.ExecuteScalarAsync<int>("SELECT COUNT(*) FROM Revisions");
        Assert.That(preCloseCount, Is.EqualTo(1));

        // Close and reopen
        await _databaseService.CloseAsync();
        await _databaseService.InitializeAsync(_testDatabasePath);
        // Note: Tables already exist in the database file from previous operations

        // Act
        var result = await _databaseService.CheckDatabaseIntegrityAsync();

        // Assert
        Assert.That(result, Is.True);

        // Verify data is still accessible using ORM
        var revisions = await _databaseService.Connection.Table<Revision>().ToListAsync();
        Assert.That(revisions, Has.Count.EqualTo(1));
        Assert.That(revisions[0].Description, Is.EqualTo("Reopen Test"));
    }

    #endregion

    #region Database Operations and Data Integrity Tests

    [Test]
    public async Task DatabaseIntegrity_AfterDataFragmentation_RemainsStable()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        // Create data fragmentation scenario through ORM insert/delete cycles
        var revisions = new List<Revision>();
        for (int i = 0; i < 100; i++)
        {
            revisions.Add(new Revision(DateTime.Now.AddDays(-i), $"Fragmentation Test {i}"));
        }
        await _databaseService.Connection.InsertAllAsync(revisions);

        // Delete every other revision using ORM to create fragmentation
        for (int i = 1; i < revisions.Count; i += 2)
        {
            await _databaseService.Connection.DeleteAsync<Revision>(revisions[i].Id);
        }

        // Act - Check integrity after fragmentation
        var integrityResult = await _databaseService.CheckDatabaseIntegrityAsync();

        // Assert - Integrity should remain good despite fragmentation
        Assert.That(integrityResult, Is.True);

        // Verify remaining data is accessible using ORM LINQ
        var remainingRevisions = await _databaseService.Connection.Table<Revision>().ToListAsync();
        Assert.That(remainingRevisions, Has.Count.EqualTo(50));
    }

    [Test]
    public async Task DatabaseIntegrity_AfterLargeDatasetOperations_RemainsStable()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        // Add large dataset using ORM batch operations
        var revisions = Enumerable.Range(0, 100)
            .Select(i => new Revision(DateTime.Now.AddDays(-i), $"Large Dataset Test {i}"))
            .ToList();
        await _databaseService.Connection.InsertAllAsync(revisions);

        // Act - Check integrity after large operations
        var integrityResult = await _databaseService.CheckDatabaseIntegrityAsync();

        // Assert - Database should remain functional
        Assert.That(integrityResult, Is.True);

        // Verify count using both ORM and raw SQL
        var ormCount = await _databaseService.Connection.Table<Revision>().CountAsync();
        var sqlCount = await _databaseService.Connection.ExecuteScalarAsync<int>("SELECT COUNT(*) FROM Revisions");

        Assert.Multiple(() =>
        {
            Assert.That(ormCount, Is.EqualTo(100));
            Assert.That(sqlCount, Is.EqualTo(100));
        });
    }

    [Test]
    public async Task DatabaseIntegrity_WithComplexRelationships_RemainsStable()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        // Create complex data relationships using ORM
        var revision = new Revision(DateTime.Now, "Relationship Test");
        await _databaseService.Connection.InsertAsync(revision);

        var documents = new List<Document>();
        for (int i = 0; i < 50; i++)
        {
            documents.Add(new Document($"REL-{i:000}", $"Relationship Document {i}", "1", revision.Id));
        }
        await _databaseService.Connection.InsertAllAsync(documents);

        var properties = new List<CustomProperty>();
        foreach (var doc in documents)
        {
            properties.Add(new CustomProperty(doc.Id, "Category", $"Category_{doc.Id % 5}"));
            properties.Add(new CustomProperty(doc.Id, "Priority", $"Priority_{doc.Id % 3}"));
        }
        await _databaseService.Connection.InsertAllAsync(properties);

        // Act
        var integrityResult = await _databaseService.CheckDatabaseIntegrityAsync();

        // Assert
        Assert.That(integrityResult, Is.True);

        // Verify relationships using ORM LINQ queries
        var documentsInRevision = await _databaseService.Connection.Table<Document>()
            .Where(d => d.RevisionId == revision.Id)
            .ToListAsync();

        var propertiesForDocuments = await _databaseService.Connection.Table<CustomProperty>()
            .Where(cp => documents.Select(d => d.Id).Contains(cp.DocumentId))
            .ToListAsync();

        Assert.Multiple(() =>
        {
            Assert.That(documentsInRevision, Has.Count.EqualTo(50));
            Assert.That(propertiesForDocuments, Has.Count.EqualTo(100)); // 2 properties per document
        });
    }

    #endregion

    #region Database Size and Statistics Tests

    [Test]
    public async Task DatabaseFile_HasReasonableSize_AfterOrmOperations()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        var initialSize = new FileInfo(_testDatabasePath).Length;

        // Add significant data using ORM operations
        var revisions = Enumerable.Range(0, 50)
            .Select(i => new Revision(DateTime.Now.AddDays(-i), $"Size Test Revision {i}"))
            .ToList();
        await _databaseService.Connection.InsertAllAsync(revisions);

        var documents = new List<Document>();
        foreach (var rev in revisions)
        {
            for (int j = 0; j < 10; j++)
            {
                documents.Add(new Document($"SIZE-{rev.Id}-{j:00}", $"Size Test Document {j}", "1", rev.Id));
            }
        }
        await _databaseService.Connection.InsertAllAsync(documents);

        // Act - Get final size
        var finalSize = new FileInfo(_testDatabasePath).Length;

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(finalSize, Is.GreaterThan(initialSize));
            Assert.That(finalSize, Is.LessThan(50 * 1024 * 1024)); // Should be less than 50MB for this test data
            Assert.That(File.Exists(_testDatabasePath), Is.True);
        });
    }

    [Test]
    public async Task DatabaseStatistics_CanBeQueried_ReturnsValidData()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        // Add test data using ORM
        var revision = new Revision(DateTime.Now, "Statistics Test");
        await _databaseService.Connection.InsertAsync(revision);

        var documents = Enumerable.Range(0, 25)
            .Select(i => new Document($"STAT-{i:000}", $"Statistics Document {i}", "1", revision.Id))
            .ToList();
        await _databaseService.Connection.InsertAllAsync(documents);

        // Act - Query database statistics using both ORM and SQL
        var revisionCount = await _databaseService.Connection.Table<Revision>().CountAsync();
        var documentCount = await _databaseService.Connection.Table<Document>().CountAsync();
        var sqlTableCount = await _databaseService.Connection.ExecuteScalarAsync<int>(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'");

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(revisionCount, Is.EqualTo(1));
            Assert.That(documentCount, Is.EqualTo(25));
            Assert.That(sqlTableCount, Is.EqualTo(3)); // Revisions, Documents, CustomProperties
        });
    }

    #endregion

    #region Database Maintenance Under Load Tests

    [Test]
    public async Task IntegrityCheck_DuringConcurrentOrmOperations_HandlesCorrectly()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        var concurrentTasks = new List<Task>();

        // Start concurrent ORM operations
        for (int i = 0; i < 10; i++)
        {
            var index = i;
            concurrentTasks.Add(Task.Run(async () =>
            {
                var revision = new Revision(DateTime.Now.AddMinutes(-index), $"Concurrent {index}");
                await _databaseService.Connection.InsertAsync(revision);

                await Task.Delay(50 + (index * 10)); // Stagger operations

                var document = new Document($"CONC-{index:00}", $"Concurrent Document {index}", "1", revision.Id);
                await _databaseService.Connection.InsertAsync(document);
            }));
        }

        // Act - Perform integrity check during operations
        var integrityTask = Task.Run(async () =>
        {
            await Task.Delay(100); // Let some operations start
            return await _databaseService.CheckDatabaseIntegrityAsync();
        });

        // Wait for all operations to complete
        await Task.WhenAll(concurrentTasks);
        var integrityResult = await integrityTask;

        // Assert
        Assert.That(integrityResult, Is.True);

        // Verify final state using ORM
        var finalRevisionCount = await _databaseService.Connection.Table<Revision>().CountAsync();
        var finalDocumentCount = await _databaseService.Connection.Table<Document>().CountAsync();

        Assert.Multiple(() =>
        {
            Assert.That(finalRevisionCount, Is.EqualTo(10));
            Assert.That(finalDocumentCount, Is.EqualTo(10));
        });
    }

    [Test]
    public async Task MaintenanceOperations_WithActiveTransactions_HandleCorrectly()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        var maintenanceTasks = new List<Task<bool>>();

        // Start a long-running sqlite-net-pcl transaction
        var transactionTask = Task.Run(async () =>
        {
            await _databaseService.Connection.RunInTransactionAsync((conn) =>
            {
                for (int i = 0; i < 20; i++)
                {
                    var revision = new Revision(DateTime.Now.AddMinutes(-i), $"Transaction Revision {i}");
                    conn.Insert(revision);
                    Thread.Sleep(10); // Simulate work
                }
            });
        });

        // Start maintenance operations
        await Task.Delay(50); // Let transaction start

        maintenanceTasks.Add(Task.Run(async () => await _databaseService.CheckDatabaseIntegrityAsync()));
        maintenanceTasks.Add(Task.Run(async () =>
        {
            await Task.Delay(30);
            return await _databaseService.CheckDatabaseIntegrityAsync();
        }));

        // Wait for all operations
        await Task.WhenAll(transactionTask);
        var maintenanceResults = await Task.WhenAll(maintenanceTasks);

        // Assert
        Assert.That(maintenanceResults.All(r => r == true), Is.True);

        // Verify transaction completed successfully using ORM
        var revisionCount = await _databaseService.Connection.Table<Revision>().CountAsync();
        Assert.That(revisionCount, Is.EqualTo(20));
    }

    #endregion

    #region Edge Cases and Error Recovery Tests

    [Test]
    public async Task MaintenanceOperations_WithEmptyDatabase_HandleCorrectly()
    {
        // Arrange - Empty database
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        // Act & Assert - Integrity check should work with empty database
        var integrityResult = await _databaseService.CheckDatabaseIntegrityAsync();
        Assert.That(integrityResult, Is.True);

        // Verify database is still functional with ORM operations
        var tableCount = await _databaseService.Connection.ExecuteScalarAsync<int>(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'");
        Assert.That(tableCount, Is.EqualTo(3));

        // Verify ORM operations still work
        var revision = new Revision(DateTime.Now, "Empty DB Test");
        await _databaseService.Connection.InsertAsync(revision);

        var insertedCount = await _databaseService.Connection.Table<Revision>().CountAsync();
        Assert.That(insertedCount, Is.EqualTo(1));
    }

    [Test]
    public async Task MaintenanceOperations_AfterReinitialize_WorkCorrectly()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        // Add data using ORM
        var revision = new Revision(DateTime.Now, "Reinitialize Test");
        await _databaseService.Connection.InsertAsync(revision);

        // Close and reinitialize
        await _databaseService.CloseAsync();
        await _databaseService.InitializeAsync(_testDatabasePath);

        // Act - Maintenance operations after reinitialize
        var integrityResult = await _databaseService.CheckDatabaseIntegrityAsync();

        // Assert
        Assert.That(integrityResult, Is.True);

        // Verify data is still accessible using ORM
        var revisions = await _databaseService.Connection.Table<Revision>().ToListAsync();
        Assert.That(revisions, Has.Count.EqualTo(1));
        Assert.That(revisions[0].Description, Is.EqualTo("Reinitialize Test"));
    }

    [Test]
    public async Task DatabaseMaintenance_PerformanceCharacteristics_WithinReasonableBounds()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        // Create substantial dataset using ORM batch operations
        var revisions = Enumerable.Range(0, 100)
            .Select(i => new Revision(DateTime.Now.AddDays(-i), $"Performance Test {i}"))
            .ToList();
        await _databaseService.Connection.InsertAllAsync(revisions);

        var documents = new List<Document>();
        foreach (var rev in revisions)
        {
            for (int j = 0; j < 20; j++)
            {
                documents.Add(new Document($"PERF-{rev.Id}-{j:00}", $"Performance Document {j}", "1", rev.Id));
            }
        }
        await _databaseService.Connection.InsertAllAsync(documents);

        // Act - Time integrity check operation
        var stopwatch = System.Diagnostics.Stopwatch.StartNew();
        var integrityResult = await _databaseService.CheckDatabaseIntegrityAsync();
        stopwatch.Stop();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(integrityResult, Is.True);
            Assert.That(stopwatch.ElapsedMilliseconds, Is.LessThan(5000)); // Should complete within 5 seconds
        });

        // Verify data integrity after performance test using ORM
        var revisionCount = await _databaseService.Connection.Table<Revision>().CountAsync();
        var documentCount = await _databaseService.Connection.Table<Document>().CountAsync();

        Assert.Multiple(() =>
        {
            Assert.That(revisionCount, Is.EqualTo(100));
            Assert.That(documentCount, Is.EqualTo(2000));
        });
    }

    #endregion
}