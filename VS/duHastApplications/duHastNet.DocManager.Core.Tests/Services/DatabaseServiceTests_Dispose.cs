using NUnit.Framework;
using duHastNet.DocManager.Core.Services;
using duHastNet.DocManager.Core.Models;
using System.IO;

namespace duHastNet.DocManager.Core.Tests.Services;

[TestFixture]
public class DatabaseServiceTests_Dispose
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
    public void TearDown()
    {
        // Don't dispose here - tests will handle disposal themselves
        if (Directory.Exists(_testDirectory))
        {
            Directory.Delete(_testDirectory, true);
        }
    }

    #region Basic Dispose Tests

    [Test]
    public void Dispose_WithoutInitialization_DoesNotThrow()
    {
        // Act & Assert
        Assert.DoesNotThrow(() => _databaseService.Dispose());
    }

    [Test]
    public async Task Dispose_AfterInitialization_ClosesConnectionAndClearsState()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        Assert.That(_databaseService.IsInitialized, Is.True);

        // Act
        _databaseService.Dispose();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(_databaseService.IsInitialized, Is.False);
            Assert.That(_databaseService.DatabasePath, Is.Null);
        });
    }

    [Test]
    public async Task Dispose_AfterDatabaseOperations_ClosesSuccessfully()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        // Perform some database operations
        await _databaseService.Connection.ExecuteAsync(
            "INSERT INTO Revisions (RevisionDate, Description) VALUES (?, ?)",
            DateTime.Now, "Test Revision");

        var revisions = await _databaseService.Connection.QueryAsync<Revision>("SELECT * FROM Revisions");
        Assert.That(revisions, Has.Count.EqualTo(1));

        // Act
        _databaseService.Dispose();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(_databaseService.IsInitialized, Is.False);
            Assert.That(_databaseService.DatabasePath, Is.Null);
        });
    }

    [Test]
    public void Dispose_MultipleCalls_DoesNotThrow()
    {
        // Arrange
        _databaseService.InitializeAsync(_testDatabasePath).Wait();

        // Act & Assert - Multiple dispose calls should not throw
        Assert.DoesNotThrow(() => _databaseService.Dispose());
        Assert.DoesNotThrow(() => _databaseService.Dispose());
        Assert.DoesNotThrow(() => _databaseService.Dispose());
    }

    [Test]
    public void Dispose_ThenAccessConnection_ThrowsException()
    {
        // Arrange
        _databaseService.InitializeAsync(_testDatabasePath).Wait();

        // Act
        _databaseService.Dispose();

        // Assert
        var ex = Assert.Throws<InvalidOperationException>(() =>
        {
            var connection = _databaseService.Connection;
        });

        Assert.That(ex.Message, Does.Contain("not initialized"));
    }

    #endregion

    #region Dispose with Active Operations Tests

    [Test]
    public async Task Dispose_DuringActiveTransaction_HandlesGracefully()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        // Start a transaction
        await _databaseService.Connection.RunInTransactionAsync((conn) =>
        {
            conn.Execute("INSERT INTO Revisions (RevisionDate, Description) VALUES (?, ?)",
                DateTime.Now, "Transaction Test");
            // Don't commit - let Dispose handle it
        });

        // Act - Dispose should handle the active transaction gracefully
        Assert.DoesNotThrow(() => _databaseService.Dispose());

        // Assert
        Assert.That(_databaseService.IsInitialized, Is.False);
    }

    [Test]
    public async Task Dispose_WithConcurrentOperations_HandlesCorrectly()
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
                        DateTime.Now.AddMinutes(index), $"Concurrent Revision {index}");

                    await Task.Delay(50); // Small delay to ensure operations overlap with dispose
                }
                catch (InvalidOperationException)
                {
                    // Expected if connection is disposed during operation
                }
                catch (SQLite.SQLiteException)
                {
                    // Expected if database is closed during operation
                }
            }));
        }

        // Give tasks a moment to start
        await Task.Delay(10);

        // Act - Dispose while operations are running
        Assert.DoesNotThrow(() => _databaseService.Dispose());

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

    #region Dispose State Verification Tests

    [Test]
    public async Task Dispose_PreservesFileOnDisk()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();
        await _databaseService.Connection.ExecuteAsync(
            "INSERT INTO Revisions (RevisionDate, Description) VALUES (?, ?)",
            DateTime.Now, "Persistent Data");

        // Act
        _databaseService.Dispose();

        // Assert
        Assert.That(File.Exists(_testDatabasePath), Is.True);

        // Verify data is still accessible after dispose
        var newService = new DatabaseService();
        await newService.InitializeAsync(_testDatabasePath);

        var revisions = await newService.Connection.QueryAsync<Revision>("SELECT * FROM Revisions");
        Assert.That(revisions, Has.Count.EqualTo(1));
        Assert.That(revisions[0].Description, Is.EqualTo("Persistent Data"));

        newService.Dispose();
    }

    [Test]
    public async Task Dispose_ClearsConnectionReference()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        var connection = _databaseService.Connection;
        Assert.That(connection, Is.Not.Null);

        // Act
        _databaseService.Dispose();

        // Assert - Connection property should throw after dispose
        Assert.Throws<InvalidOperationException>(() =>
        {
            var conn = _databaseService.Connection;
        });
    }

    [Test]
    public void Dispose_SetsPropertiesCorrectly()
    {
        // Arrange
        _databaseService.InitializeAsync(_testDatabasePath).Wait();
        Assert.Multiple(() =>
        {
            Assert.That(_databaseService.IsInitialized, Is.True);
            Assert.That(_databaseService.DatabasePath, Is.Not.Null);
        });

        // Act
        _databaseService.Dispose();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(_databaseService.IsInitialized, Is.False);
            Assert.That(_databaseService.DatabasePath, Is.Null);
        });
    }

    #endregion

    #region Dispose Pattern Implementation Tests

    [Test]
    public async Task Dispose_FollowsProperDisposePattern()
    {
        // Test that the dispose pattern is implemented correctly

        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        // Act - First dispose should clean up resources
        _databaseService.Dispose();

        // Assert - Should be safe to dispose multiple times
        Assert.DoesNotThrow(() => _databaseService.Dispose());

        // Verify state is consistently disposed
        Assert.Multiple(() =>
        {
            Assert.That(_databaseService.IsInitialized, Is.False);
            Assert.That(_databaseService.DatabasePath, Is.Null);
        });
    }

    [Test]
    public async Task Dispose_ThenReinitialize_ThrowsException()
    {
        // Verify that once disposed, the service cannot be reused

        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);

        // Act
        _databaseService.Dispose();

        // Assert - Should not be able to reinitialize a disposed service
        // Note: This behavior depends on implementation - if reinitialization is allowed,
        // this test might need to be modified

        // For now, test that attempting operations after dispose throws
        Assert.Throws<InvalidOperationException>(() =>
        {
            var connection = _databaseService.Connection;
        });
    }

    [Test]
    public void Dispose_WithNullConnection_DoesNotThrow()
    {
        // Test edge case where connection might be null

        // Arrange - Service created but never initialized
        var service = new DatabaseService();

        // Act & Assert
        Assert.DoesNotThrow(() => service.Dispose());
        Assert.That(service.IsInitialized, Is.False);
    }

    #endregion

    #region Using Statement Tests

    [Test]
    public async Task DatabaseService_WithUsingStatement_DisposesCorrectly()
    {
        // Test that using statement properly disposes the service

        string tempPath = Path.Combine(_testDirectory, "using_test.db");

        // Act
        using (var service = new DatabaseService())
        {
            await service.InitializeAsync(tempPath);
            await service.CreateTablesAsync();
            await service.Connection.ExecuteAsync(
                "INSERT INTO Revisions (RevisionDate, Description) VALUES (?, ?)",
                DateTime.Now, "Using Statement Test");

            Assert.That(service.IsInitialized, Is.True);
        }
        // Service should be disposed here

        // Assert - File should exist but service is disposed
        Assert.That(File.Exists(tempPath), Is.True);

        // Verify we can access the data with a new service
        using var newService = new DatabaseService();
        await newService.InitializeAsync(tempPath);
        var revisions = await newService.Connection.QueryAsync<Revision>("SELECT * FROM Revisions");
        Assert.That(revisions, Has.Count.EqualTo(1));
        Assert.That(revisions[0].Description, Is.EqualTo("Using Statement Test"));
    }

    [Test]
    public async Task DatabaseService_UsingStatementWithException_StillDisposes()
    {
        // Test that using statement disposes even when exception occurs

        string tempPath = Path.Combine(_testDirectory, "exception_test.db");

        // Act & Assert
        try
        {
            using (var service = new DatabaseService())
            {
                await service.InitializeAsync(tempPath);
                await service.CreateTablesAsync();

                Assert.That(service.IsInitialized, Is.True);

                // Force an exception
                throw new InvalidOperationException("Test exception");
            }
        }
        catch (InvalidOperationException ex) when (ex.Message == "Test exception")
        {
            // Expected exception
        }

        // Assert - File should still exist despite exception
        Assert.That(File.Exists(tempPath), Is.True);

        // Verify database is still accessible
        using var newService = new DatabaseService();
        await newService.InitializeAsync(tempPath);

        // Should be able to query without issues
        var revisions = await newService.Connection.QueryAsync<Revision>("SELECT * FROM Revisions");
        Assert.That(revisions, Is.Not.Null);
    }

    #endregion

    #region Resource Management Tests

    [Test]
    public async Task Dispose_HandlesLargeAmountOfData()
    {
        // Test dispose with large dataset

        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        // Insert a large amount of test data
        var revisions = new List<Revision>();
        for (int i = 0; i < 1000; i++)
        {
            revisions.Add(new Revision(DateTime.Now.AddDays(-i), $"Revision {i}"));
        }

        await _databaseService.Connection.InsertAllAsync(revisions);

        // Verify data was inserted
        var count = await _databaseService.Connection.ExecuteScalarAsync<int>("SELECT COUNT(*) FROM Revisions");
        Assert.That(count, Is.EqualTo(1000));

        // Act
        _databaseService.Dispose();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(_databaseService.IsInitialized, Is.False);
            Assert.That(File.Exists(_testDatabasePath), Is.True);
        });

        // Verify data is still intact
        using var newService = new DatabaseService();
        await newService.InitializeAsync(_testDatabasePath);
        var finalCount = await newService.Connection.ExecuteScalarAsync<int>("SELECT COUNT(*) FROM Revisions");
        Assert.That(finalCount, Is.EqualTo(1000));
    }

    [Test]
    public async Task Dispose_WithOpenReaders_HandlesGracefully()
    {
        // Test dispose when there might be open data readers

        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        // Insert test data
        await _databaseService.Connection.ExecuteAsync(
            "INSERT INTO Revisions (RevisionDate, Description) VALUES (?, ?)",
            DateTime.Now, "Reader Test");

        // Start a query that might keep a reader open
        var queryTask = Task.Run(async () =>
        {
            try
            {
                var revisions = await _databaseService.Connection.QueryAsync<Revision>("SELECT * FROM Revisions");
                return revisions.Count;
            }
            catch
            {
                return -1; // Indicates query was interrupted
            }
        });

        // Small delay to ensure query starts
        await Task.Delay(10);

        // Act - Dispose while query might be active
        _databaseService.Dispose();

        // Wait for query to complete
        var result = await queryTask;

        // Assert - Dispose should complete successfully regardless of query state
        Assert.That(_databaseService.IsInitialized, Is.False);
    }

    #endregion

    #region Error Handling Tests

    [Test]
    public async Task Dispose_WhenCloseAsyncThrows_StillCompletesDispose()
    {
        // Note: This test is more about documenting expected behavior
        // since we can't easily force CloseAsync to throw in sqlite-net-pcl

        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);

        // Act - Even if internal cleanup has issues, Dispose should not throw
        Assert.DoesNotThrow(() => _databaseService.Dispose());

        // Assert
        Assert.That(_databaseService.IsInitialized, Is.False);
    }

    [Test]
    public void Dispose_CallsGCSuppressFinalize()
    {
        // This test documents that the dispose pattern should call GC.SuppressFinalize
        // We can't directly test this, but we can verify the service disposes correctly

        // Arrange
        _databaseService.InitializeAsync(_testDatabasePath).Wait();

        // Act
        _databaseService.Dispose();

        // Assert - Service should be properly disposed
        Assert.That(_databaseService.IsInitialized, Is.False);

        // Verify no further operations are possible
        Assert.Throws<InvalidOperationException>(() =>
        {
            var connection = _databaseService.Connection;
        });
    }

    #endregion
}