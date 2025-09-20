using NUnit.Framework;
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.DocManager.Core.Models.Config;
using System.IO;

namespace duHastNet.DocManager.Core.Tests.Services.Api;

[TestFixture]
public class DocManagerApiTests_StateOperations
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

    #region IsDatabaseReady() Tests

    [Test]
    public void IsDatabaseReady_BeforeSetup_ReturnsFalse()
    {
        // Act
        var result = _api.IsDatabaseReady();

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public async Task IsDatabaseReady_AfterSuccessfulSetup_ReturnsTrue()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "ready_test.db");

        // Act
        var setupResult = await _api.SetupDatabaseAsync(databasePath);
        var result = _api.IsDatabaseReady();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(setupResult.IsSetupSuccessful, Is.True);
            Assert.That(result, Is.True);
        });
    }

    [Test]
    public async Task IsDatabaseReady_AfterClose_ReturnsFalse()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "close_test.db");
        await _api.SetupDatabaseAsync(databasePath);

        // Act
        await _api.CloseAsync();
        var result = _api.IsDatabaseReady();

        // Assert
        Assert.That(result, Is.False);
    }

    #endregion

    #region GetDatabasePath() Tests

    [Test]
    public void GetDatabasePath_BeforeSetup_ReturnsNull()
    {
        // Act
        var result = _api.GetDatabasePath();

        // Assert
        Assert.That(result, Is.Null);
    }

    [Test]
    public async Task GetDatabasePath_AfterSuccessfulSetup_ReturnsCorrectPath()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "path_test.db");

        // Act
        await _api.SetupDatabaseAsync(databasePath);
        var result = _api.GetDatabasePath();

        // Assert
        Assert.That(result, Is.EqualTo(databasePath));
    }

    [Test]
    public async Task GetDatabasePath_AfterClose_ReturnsNull()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "close_path_test.db");
        await _api.SetupDatabaseAsync(databasePath);

        // Act
        await _api.CloseAsync();
        var result = _api.GetDatabasePath();

        // Assert
        Assert.That(result, Is.Null);
    }
}
    #endregion