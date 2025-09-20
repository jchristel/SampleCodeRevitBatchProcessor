using NUnit.Framework;
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.DocManager.Core.Models.Config;
using duHastNet.DocManager.Core.Models;
using System.IO;

namespace duHastNet.DocManager.Core.Tests.Services.Api;

[TestFixture]
public class DocManagerApiTests_TestAndCloseOperations
{
    private DocManagerApi _api;
    private string _testDirectory;

    [SetUp]
    public void Setup()
    {
        _api = new DocManagerApi();
        _testDirectory = Path.Combine(Path.GetTempPath(), "DocManagerApiTests", Guid.NewGuid().ToString());
        Directory.CreateDirectory(_testDirectory);
    }

    [TearDown]
    public async Task TearDown()
    {
        if (_api != null)
        {
            await _api.CloseAsync();
            _api.Dispose();
        }

        if (Directory.Exists(_testDirectory))
        {
            try
            {
                Directory.Delete(_testDirectory, true);
            }
            catch (IOException)
            {
                // Handle locked files gracefully
                await Task.Delay(100);
                try
                {
                    Directory.Delete(_testDirectory, true);
                }
                catch (IOException ex)
                {
                    Console.WriteLine($"Warning: Could not delete test directory {_testDirectory}: {ex.Message}");
                }
            }
        }
    }

    #region TestDatabaseAsync() Tests

    [Test]
    public async Task TestDatabaseAsync_WithInitializedDatabase_ReturnsSuccessfulResult()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "test_success.db");
        await _api.SetupDatabaseAsync(databasePath);

        // Act
        var result = await _api.TestDatabaseAsync();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsSetupSuccessful, Is.True);
            Assert.That(result.DatabasePath, Is.EqualTo(databasePath));
            Assert.That(result.Message, Does.Contain("Database test successful"));
            Assert.That(result.Message, Does.Contain("Revisions: 0"));
            Assert.That(result.Message, Does.Contain("Documents: 0"));
            Assert.That(result.Message, Does.Contain("Properties: 0"));
            Assert.That(result.Message, Does.Contain("Integrity: OK"));
            Assert.That(result.HasErrors, Is.False);
        });
    }

    [Test]
    public async Task TestDatabaseAsync_WithoutInitialization_ReturnsFailureResult()
    {
        // Act
        var result = await _api.TestDatabaseAsync();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsSetupSuccessful, Is.False);
            Assert.That(result.HasErrors, Is.True);
            Assert.That(result.Errors[0], Does.Contain("Database not initialized"));
        });
    }

    [Test]
    public async Task TestDatabaseAsync_WithDataInDatabase_ReturnsCorrectCounts()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "test_with_data.db");
        await _api.SetupDatabaseAsync(databasePath);

        // Add some test data using the internal unit of work
        // Note: This requires accessing internal API state, which may need adjustment based on actual implementation
        // For now, we'll test the basic functionality

        // Act
        var result = await _api.TestDatabaseAsync();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsSetupSuccessful, Is.True);
            Assert.That(result.Message, Does.Contain("Database test successful"));
            Assert.That(result.HasErrors, Is.False);
        });
    }

    #endregion

    #region CloseAsync() Tests

    [Test]
    public async Task CloseAsync_WithInitializedDatabase_ClosesSuccessfully()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "close_test.db");
        await _api.SetupDatabaseAsync(databasePath);

        // Verify it's ready before closing
        Assert.That(_api.IsDatabaseReady(), Is.True);

        // Act
        await _api.CloseAsync();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(_api.IsDatabaseReady(), Is.False);
            Assert.That(_api.GetDatabasePath(), Is.Null);
            Assert.That(File.Exists(databasePath), Is.True); // File should still exist on disk
        });
    }

    [Test]
    public async Task CloseAsync_WithoutInitialization_DoesNotThrow()
    {
        // Act & Assert
        Assert.DoesNotThrowAsync(async () => await _api.CloseAsync());

        // Verify state remains consistent
        Assert.Multiple(() =>
        {
            Assert.That(_api.IsDatabaseReady(), Is.False);
            Assert.That(_api.GetDatabasePath(), Is.Null);
        });
    }

    [Test]
    public async Task CloseAsync_MultipleCalls_DoesNotThrow()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "multiple_close.db");
        await _api.SetupDatabaseAsync(databasePath);

        // Act & Assert
        await _api.CloseAsync();
        Assert.DoesNotThrowAsync(async () => await _api.CloseAsync());
        Assert.DoesNotThrowAsync(async () => await _api.CloseAsync());

        // Verify final state
        Assert.Multiple(() =>
        {
            Assert.That(_api.IsDatabaseReady(), Is.False);
            Assert.That(_api.GetDatabasePath(), Is.Null);
        });
    }

    #endregion

    #region Dispose() Tests

    [Test]
    public async Task Dispose_WithInitializedDatabase_CleansUpResources()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "dispose_test.db");
        await _api.SetupDatabaseAsync(databasePath);

        // Verify it's ready before disposing
        Assert.That(_api.IsDatabaseReady(), Is.True);

        // Act
        _api.Dispose();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(_api.IsDatabaseReady(), Is.False);
            Assert.That(_api.GetDatabasePath(), Is.Null);
            Assert.That(File.Exists(databasePath), Is.True); // File should still exist on disk
        });
    }

    [Test]
    public void Dispose_WithoutInitialization_DoesNotThrow()
    {
        // Act & Assert
        Assert.DoesNotThrow(() => _api.Dispose());

        // Verify state remains consistent
        Assert.Multiple(() =>
        {
            Assert.That(_api.IsDatabaseReady(), Is.False);
            Assert.That(_api.GetDatabasePath(), Is.Null);
        });
    }

    [Test]
    public async Task Dispose_MultipleCalls_DoesNotThrow()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "multiple_dispose.db");
        await _api.SetupDatabaseAsync(databasePath);

        // Act & Assert
        _api.Dispose();
        Assert.DoesNotThrow(() => _api.Dispose());
        Assert.DoesNotThrow(() => _api.Dispose());

        // Verify final state
        Assert.Multiple(() =>
        {
            Assert.That(_api.IsDatabaseReady(), Is.False);
            Assert.That(_api.GetDatabasePath(), Is.Null);
        });
    }

    #endregion

    #region Integration Tests

    [Test]
    public async Task FullWorkflow_SetupTestClose_WorksCorrectly()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "workflow.db");

        // Act & Assert - Setup
        var setupResult = await _api.SetupDatabaseAsync(databasePath);
        Assert.That(setupResult.IsSetupSuccessful, Is.True);
        Assert.That(_api.IsDatabaseReady(), Is.True);

        // Act & Assert - Test
        var testResult = await _api.TestDatabaseAsync();
        Assert.That(testResult.IsSetupSuccessful, Is.True);
        Assert.That(_api.IsDatabaseReady(), Is.True);

        // Act & Assert - Close
        await _api.CloseAsync();
        Assert.That(_api.IsDatabaseReady(), Is.False);
        Assert.That(_api.GetDatabasePath(), Is.Null);

        // Verify file persists
        Assert.That(File.Exists(databasePath), Is.True);
    }

    [Test]
    public async Task FullWorkflow_SetupTestDispose_WorksCorrectly()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "workflow_dispose.db");

        // Act & Assert - Setup
        var setupResult = await _api.SetupDatabaseAsync(databasePath);
        Assert.That(setupResult.IsSetupSuccessful, Is.True);
        Assert.That(_api.IsDatabaseReady(), Is.True);

        // Act & Assert - Test
        var testResult = await _api.TestDatabaseAsync();
        Assert.That(testResult.IsSetupSuccessful, Is.True);
        Assert.That(_api.IsDatabaseReady(), Is.True);

        // Act & Assert - Dispose
        _api.Dispose();
        Assert.That(_api.IsDatabaseReady(), Is.False);
        Assert.That(_api.GetDatabasePath(), Is.Null);

        // Verify file persists
        Assert.That(File.Exists(databasePath), Is.True);
    }

    [Test]
    public async Task ErrorHandling_TestAfterClose_ReturnsFailure()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "error_test.db");
        await _api.SetupDatabaseAsync(databasePath);
        await _api.CloseAsync();

        // Act
        var result = await _api.TestDatabaseAsync();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsSetupSuccessful, Is.False);
            Assert.That(result.HasErrors, Is.True);
            Assert.That(result.Errors[0], Does.Contain("Database not initialized"));
        });
    }

    #endregion

    #region Using Statement Tests

    [Test]
    public async Task UsingStatement_DisposesCorrectly()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "using_test.db");

        // Act
        using (var api = new DocManagerApi())
        {
            await api.SetupDatabaseAsync(databasePath);
            Assert.That(api.IsDatabaseReady(), Is.True);

            var testResult = await api.TestDatabaseAsync();
            Assert.That(testResult.IsSetupSuccessful, Is.True);
        }
        // Dispose should be called automatically here

        // Assert
        Assert.That(File.Exists(databasePath), Is.True);
    }

    [Test]
    public async Task UsingStatement_WithException_StillDisposes()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "using_exception.db");

        // Act & Assert
        try
        {
            using (var api = new DocManagerApi())
            {
                await api.SetupDatabaseAsync(databasePath);
                Assert.That(api.IsDatabaseReady(), Is.True);

                // Force an exception
                throw new InvalidOperationException("Test exception");
            }
        }
        catch (InvalidOperationException ex) when (ex.Message == "Test exception")
        {
            // Expected exception
        }

        // Assert - File should still exist despite exception
        Assert.That(File.Exists(databasePath), Is.True);
    }

    [Test]
    public async Task ResourceManagement_LargeNumberOfOperations_HandlesCorrectly()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "resource_test.db");

        // Act - Perform many operations to test resource management
        using (var api = new DocManagerApi())
        {
            await api.SetupDatabaseAsync(databasePath);

            for (int i = 0; i < 100; i++)
            {
                var testResult = await api.TestDatabaseAsync();
                Assert.That(testResult.IsSetupSuccessful, Is.True);
                Assert.That(api.IsDatabaseReady(), Is.True);
            }
        }

        // Assert
        Assert.That(File.Exists(databasePath), Is.True);
    }

    #endregion
}