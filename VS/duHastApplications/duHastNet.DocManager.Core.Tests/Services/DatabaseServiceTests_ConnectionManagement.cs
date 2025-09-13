using NUnit.Framework;
using duHastNet.DocManager.Core.Services;
using duHastNet.DocManager.Core.Models;
using System.IO;

namespace duHastNet.DocManager.Core.Tests.Services;

[TestFixture]
public class DatabaseServiceTests_ConnectionManagement
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

    #region CloseAsync Tests

    [Test]
    public async Task CloseAsync_AfterInitialization_ClosesConnection()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        Assert.That(_databaseService.IsInitialized, Is.True);

        // Act
        await _databaseService.CloseAsync();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(_databaseService.IsInitialized, Is.False);
            Assert.That(_databaseService.DatabasePath, Is.Null);
        });
    }

    [Test]
    public async Task CloseAsync_WithoutInitialization_DoesNotThrow()
    {
        // Act & Assert
        Assert.DoesNotThrowAsync(async () => await _databaseService.CloseAsync());
        Assert.That(_databaseService.IsInitialized, Is.False);
    }

    [Test]
    public async Task CloseAsync_MultipleCalls_DoesNotThrow()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);

        // Act & Assert
        await _databaseService.CloseAsync();
        Assert.DoesNotThrowAsync(async () => await _databaseService.CloseAsync());
        Assert.DoesNotThrowAsync(async () => await _databaseService.CloseAsync());
    }

    [Test]
    public async Task CloseAsync_AfterDataOperations_ClosesSuccessfully()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();
        await _databaseService.Connection.ExecuteAsync(
            "INSERT INTO Revisions (RevisionDate, Description) VALUES (?, ?)",
            DateTime.Now, "Test Revision");

        // Act
        await _databaseService.CloseAsync();

        // Assert
        Assert.That(_databaseService.IsInitialized, Is.False);
    }

    [Test]
    public void CloseAsync_ThenAccessConnection_ThrowsException()
    {
        // Arrange
        _databaseService.InitializeAsync(_testDatabasePath).Wait();
        _databaseService.CloseAsync().Wait();

        // Act & Assert
        var ex = Assert.Throws<InvalidOperationException>(() =>
        {
            var connection = _databaseService.Connection;
        });

        Assert.That(ex.Message, Does.Contain("not initialized"));
    }

    [Test]
    public async Task CloseAsync_ThenReinitialize_WorksCorrectly()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CloseAsync();

        // Act
        await _databaseService.InitializeAsync(_testDatabasePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(_databaseService.IsInitialized, Is.True);
            Assert.That(_databaseService.DatabasePath, Is.EqualTo(_testDatabasePath));
            Assert.That(_databaseService.Connection, Is.Not.Null);
        });
    }

    [Test]
    public async Task CloseAsync_PreservesFileOnDisk()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();
        await _databaseService.Connection.ExecuteAsync(
            "INSERT INTO Revisions (RevisionDate, Description) VALUES (?, ?)",
            DateTime.Now, "Test Revision");

        // Act
        await _databaseService.CloseAsync();

        // Assert
        Assert.That(File.Exists(_testDatabasePath), Is.True);

        // Verify data is persisted
        await _databaseService.InitializeAsync(_testDatabasePath);
        var revisions = await _databaseService.Connection.QueryAsync<Revision>("SELECT * FROM Revisions");
        Assert.That(revisions, Has.Count.EqualTo(1));
    }

    [Test]
    public async Task CloseAsync_DuringActiveTransaction_HandlesGracefully()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        // Start a transaction implicitly by using sqlite-net-pcl's transaction support
        await _databaseService.Connection.RunInTransactionAsync((conn) =>
        {
            conn.Execute("INSERT INTO Revisions (RevisionDate, Description) VALUES (?, ?)",
                DateTime.Now, "Test Revision");
            // Don't commit - let CloseAsync handle it
        });

        // Act - Close should handle the transaction gracefully
        Assert.DoesNotThrowAsync(async () => await _databaseService.CloseAsync());

        // Assert
        Assert.That(_databaseService.IsInitialized, Is.False);
    }

    [Test]
    public void CloseAsync_ClearsConnectionReference()
    {
        // Arrange
        _databaseService.InitializeAsync(_testDatabasePath).Wait();
        var connection = _databaseService.Connection;
        Assert.That(connection, Is.Not.Null);

        // Act
        _databaseService.CloseAsync().Wait();

        // Assert
        Assert.Throws<InvalidOperationException>(() =>
        {
            var conn = _databaseService.Connection;
        });
    }

    [Test]
    public async Task CloseAsync_WithConcurrentOperations_HandlesCorrectly()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        var tasks = new List<Task>();

        // Start some concurrent operations
        for (int i = 0; i < 5; i++)
        {
            var index = i;
            tasks.Add(Task.Run(async () =>
            {
                try
                {
                    await _databaseService.Connection.ExecuteAsync(
                        "INSERT INTO Revisions (RevisionDate, Description) VALUES (?, ?)",
                        DateTime.Now, $"Test Revision {index}");
                }
                catch (InvalidOperationException)
                {
                    // Expected if connection is closed during operation
                }
                catch (SQLite.SQLiteException)
                {
                    // Expected if database is closed during operation
                }
            }));
        }

        // Act - Close while operations are running
        await _databaseService.CloseAsync();

        // Wait for all tasks to complete (they may throw exceptions)
        await Task.WhenAll(tasks.Select(async t =>
        {
            try
            {
                await t;
            }
            catch
            {
                // Ignore exceptions from concurrent operations
            }
        }));

        // Assert
        Assert.That(_databaseService.IsInitialized, Is.False);
    }

    #endregion

    #region Connection Property Tests

    [Test]
    public void Connection_BeforeInitialization_ThrowsException()
    {
        // Act & Assert
        var ex = Assert.Throws<InvalidOperationException>(() =>
        {
            var connection = _databaseService.Connection;
        });

        Assert.That(ex.Message, Does.Contain("not initialized"));
    }

    [Test]
    public async Task Connection_AfterInitialization_ReturnsValidConnection()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);

        // Act
        var connection = _databaseService.Connection;

        // Assert
        Assert.That(connection, Is.Not.Null);
    }

    [Test]
    public async Task Connection_MultipleAccess_ReturnsSameInstance()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);

        // Act
        var connection1 = _databaseService.Connection;
        var connection2 = _databaseService.Connection;

        // Assert
        Assert.That(connection1, Is.SameAs(connection2));
    }

    [Test]
    public async Task Connection_AfterReinitialization_ReturnsNewInstance()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        var originalConnection = _databaseService.Connection;

        // Act
        await _databaseService.InitializeAsync(_testDatabasePath);
        var newConnection = _databaseService.Connection;

        // Assert
        Assert.That(newConnection, Is.Not.SameAs(originalConnection));
    }

    [Test]
    public async Task Connection_CanExecuteQueries()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();
        var connection = _databaseService.Connection;

        // Act
        var result = await connection.ExecuteAsync(
            "INSERT INTO Revisions (RevisionDate, Description) VALUES (?, ?)",
            DateTime.Now, "Test Revision");

        // Assert
        Assert.That(result, Is.EqualTo(1));
    }

    [Test]
    public void Connection_AfterClose_ThrowsException()
    {
        // Arrange
        _databaseService.InitializeAsync(_testDatabasePath).Wait();
        _databaseService.CloseAsync().Wait();

        // Act & Assert
        var ex = Assert.Throws<InvalidOperationException>(() =>
        {
            var connection = _databaseService.Connection;
        });

        Assert.That(ex.Message, Does.Contain("not initialized"));
    }

    [Test]
    public async Task Connection_ConcurrentAccess_ThreadSafe()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        var connections = new List<object>();
        var tasks = new List<Task>();

        // Act - Access connection from multiple threads
        for (int i = 0; i < 10; i++)
        {
            tasks.Add(Task.Run(() =>
            {
                var conn = _databaseService.Connection;
                lock (connections)
                {
                    connections.Add(conn);
                }
            }));
        }

        await Task.WhenAll(tasks);

        // Assert - All should be the same instance
        Assert.That(connections, Has.Count.EqualTo(10));
        Assert.That(connections.All(c => c == connections[0]), Is.True);
    }

    [Test]
    public async Task Connection_WithDatabaseOperations_MaintainsConsistency()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();
        var connection = _databaseService.Connection;

        // Act - Perform multiple operations
        await connection.ExecuteAsync(
            "INSERT INTO Revisions (RevisionDate, Description) VALUES (?, ?)",
            DateTime.Now, "Test Revision 1");

        await connection.ExecuteAsync(
            "INSERT INTO Revisions (RevisionDate, Description) VALUES (?, ?)",
            DateTime.Now.AddDays(1), "Test Revision 2");

        var count = await connection.ExecuteScalarAsync<int>("SELECT COUNT(*) FROM Revisions");

        // Assert
        Assert.That(count, Is.EqualTo(2));
    }

    [Test]
    public async Task Connection_UsingSqliteNetPclOrmFeatures_WorksCorrectly()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();
        var connection = _databaseService.Connection;

        // Act - Use sqlite-net-pcl ORM features directly
        var revision = new Revision(DateTime.Now, "ORM Test Revision");
        await connection.InsertAsync(revision);

        var retrievedRevisions = await connection.Table<Revision>()
            .Where(r => r.Description.Contains("ORM"))
            .ToListAsync();

        // Assert
        Assert.That(retrievedRevisions, Has.Count.EqualTo(1));
        Assert.That(retrievedRevisions[0].Description, Is.EqualTo("ORM Test Revision"));
    }

    [Test]
    public async Task Connection_AccessDuringInitialization_HandlesCorrectly()
    {
        // This test verifies behavior if Connection is accessed during initialization

        var initTask = _databaseService.InitializeAsync(_testDatabasePath);

        // Try to access connection immediately (before initialization completes)
        await Task.Delay(1); // Small delay to allow initialization to start

        try
        {
            var connection = _databaseService.Connection;
            Assert.That(connection, Is.Not.Null, "Connection should be available if initialization completed");
        }
        catch (InvalidOperationException ex)
        {
            Assert.That(ex.Message, Does.Contain("not initialized"),
                "Should throw proper exception if initialization not complete");
        }

        // Ensure initialization completes
        await initTask;

        // Connection should be available now
        var finalConnection = _databaseService.Connection;
        Assert.That(finalConnection, Is.Not.Null);
    }

    #endregion
}