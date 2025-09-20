using NUnit.Framework;
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.DocManager.Core.Models.Config;
using System.IO;

namespace duHastNet.DocManager.Core.Tests.Services.Api;

[TestFixture]
public class DocManagerApiTests_SetupOperations
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

        // Give some time for any remaining database connections to be released
        await Task.Delay(50);

        if (Directory.Exists(_testDirectory))
        {
            try
            {
                Directory.Delete(_testDirectory, true);
            }
            catch (IOException)
            {
                // If files are still locked, try again after a short delay
                await Task.Delay(100);
                try
                {
                    Directory.Delete(_testDirectory, true);
                }
                catch (IOException)
                {
                    // If still locked, force garbage collection and try once more
                    GC.Collect();
                    GC.WaitForPendingFinalizers();
                    await Task.Delay(100);

                    try
                    {
                        Directory.Delete(_testDirectory, true);
                    }
                    catch (IOException ex)
                    {
                        // Log the issue but don't fail the test
                        Console.WriteLine($"Warning: Could not delete test directory {_testDirectory}: {ex.Message}");
                    }
                }
            }
        }
    }

    #region SetupDatabaseAsync(DatabaseSetupConfig) Tests

    [Test]
    public async Task SetupDatabaseAsync_WithValidConfig_CreatesSuccessfulResult()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "test.db");
        var config = new DatabaseSetupConfig
        {
            DatabasePath = databasePath,
            CustomPropertyNames = new List<string> { "DisciplineCode", "ProjectPhase" },
            OverwriteExisting = false
        };

        // Act
        var result = await _api.SetupDatabaseAsync(config);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsSetupSuccessful, Is.True);
            Assert.That(result.DatabasePath, Is.EqualTo(databasePath));
            Assert.That(result.HasErrors, Is.False);
            Assert.That(File.Exists(databasePath), Is.True);
            Assert.That(_api.IsDatabaseReady(), Is.True);
        });
    }

    [Test]
    public async Task SetupDatabaseAsync_WithEmptyPath_ReturnsFailureResult()
    {
        // Arrange
        var config = new DatabaseSetupConfig
        {
            DatabasePath = "",
            CustomPropertyNames = new List<string>(),
            OverwriteExisting = false
        };

        // Act
        var result = await _api.SetupDatabaseAsync(config);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsSetupSuccessful, Is.False);
            Assert.That(result.HasErrors, Is.True);
            Assert.That(result.Errors, Has.Count.EqualTo(1));
            Assert.That(result.Errors[0], Does.Contain("Database path is required"));
            Assert.That(_api.IsDatabaseReady(), Is.False);
        });
    }

    [Test]
    public async Task SetupDatabaseAsync_ExistingFileWithoutOverwrite_ReturnsFailureResult()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "existing.db");
        File.WriteAllText(databasePath, "dummy content");

        var config = new DatabaseSetupConfig
        {
            DatabasePath = databasePath,
            CustomPropertyNames = new List<string>(),
            OverwriteExisting = false
        };

        // Act
        var result = await _api.SetupDatabaseAsync(config);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsSetupSuccessful, Is.False);
            Assert.That(result.HasErrors, Is.True);
            Assert.That(result.Errors[0], Does.Contain("Database file already exists"));
            Assert.That(_api.IsDatabaseReady(), Is.False);
        });
    }

    [Test]
    public async Task SetupDatabaseAsync_ExistingFileWithOverwrite_SucceedsAndReplacesFile()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "overwrite.db");
        File.WriteAllText(databasePath, "original content");
        var originalModifyTime = File.GetLastWriteTime(databasePath);

        await Task.Delay(10); // Ensure time difference

        var config = new DatabaseSetupConfig
        {
            DatabasePath = databasePath,
            CustomPropertyNames = new List<string> { "TestProperty" },
            OverwriteExisting = true
        };

        // Act
        var result = await _api.SetupDatabaseAsync(config);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsSetupSuccessful, Is.True);
            Assert.That(result.DatabasePath, Is.EqualTo(databasePath));
            Assert.That(File.Exists(databasePath), Is.True);
            Assert.That(File.GetLastWriteTime(databasePath), Is.GreaterThan(originalModifyTime));
            Assert.That(_api.IsDatabaseReady(), Is.True);
        });
    }

    [Test]
    public async Task SetupDatabaseAsync_WithCustomProperties_IncludesWarningsForInvalidNames()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "test.db");
        var config = new DatabaseSetupConfig
        {
            DatabasePath = databasePath,
            CustomPropertyNames = new List<string>
            {
                "ValidProperty",
                "", // Empty
                "Property\"WithQuotes", // Problematic characters
                new string('A', 150), // Too long
                "Property;WithSemicolon", // Problematic character
                "AnotherValidProperty"
            },
            OverwriteExisting = false
        };

        // Act
        var result = await _api.SetupDatabaseAsync(config);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsSetupSuccessful, Is.True);
            Assert.That(result.HasWarnings, Is.True);
            Assert.That(result.Warnings, Has.Count.EqualTo(4)); // Empty, quotes, too long, semicolon
            Assert.That(result.Warnings.Any(w => w.Contains("[empty/whitespace]")), Is.True);
            Assert.That(result.Warnings.Any(w => w.Contains("too long")), Is.True);
            Assert.That(result.Warnings.Any(w => w.Contains("problematic characters")), Is.True);
        });
    }

    [Test]
    public async Task SetupDatabaseAsync_WithInvalidPath_ReturnsFailureResult()
    {
        // Arrange - Use empty path to guarantee failure
        var config = new DatabaseSetupConfig
        {
            DatabasePath = "", // Empty path should fail
            CustomPropertyNames = new List<string>(),
            OverwriteExisting = false
        };

        // Act
        var result = await _api.SetupDatabaseAsync(config);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsSetupSuccessful, Is.False);
            Assert.That(result.HasErrors, Is.True);
            Assert.That(result.Errors[0], Does.Contain("Database path is required"));
            Assert.That(_api.IsDatabaseReady(), Is.False);
        });
    }

    [Test]
    public async Task SetupDatabaseAsync_WithNullConfig_ReturnsFailureResult()
    {
        // Act
        var result = await _api.SetupDatabaseAsync((DatabaseSetupConfig)null!);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsSetupSuccessful, Is.False);
            Assert.That(result.HasErrors, Is.True);
            Assert.That(_api.IsDatabaseReady(), Is.False);
        });
    }

    [Test]
    public async Task SetupDatabaseAsync_CreatesNonExistentDirectories()
    {
        // Arrange
        var deepPath = Path.Combine(_testDirectory, "level1", "level2", "level3", "database.db");
        var config = new DatabaseSetupConfig
        {
            DatabasePath = deepPath,
            CustomPropertyNames = new List<string>(),
            OverwriteExisting = false
        };

        // Act
        var result = await _api.SetupDatabaseAsync(config);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsSetupSuccessful, Is.True);
            Assert.That(File.Exists(deepPath), Is.True);
            Assert.That(Directory.Exists(Path.GetDirectoryName(deepPath)), Is.True);
            Assert.That(_api.IsDatabaseReady(), Is.True);
        });
    }

    #endregion

    #region SetupDatabaseAsync(string, List<string>, bool) Tests

    [Test]
    public async Task SetupDatabaseAsync_SimpleOverload_WithValidParameters_CreatesSuccessfulResult()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "simple.db");
        var customProperties = new List<string> { "Property1", "Property2" };

        // Act
        var result = await _api.SetupDatabaseAsync(databasePath, customProperties, false);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsSetupSuccessful, Is.True);
            Assert.That(result.DatabasePath, Is.EqualTo(databasePath));
            Assert.That(File.Exists(databasePath), Is.True);
            Assert.That(_api.IsDatabaseReady(), Is.True);
        });
    }

    [Test]
    public async Task SetupDatabaseAsync_SimpleOverload_WithNullCustomProperties_UsesEmptyList()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "simple_null.db");

        // Act
        var result = await _api.SetupDatabaseAsync(databasePath, null, false);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsSetupSuccessful, Is.True);
            Assert.That(result.DatabasePath, Is.EqualTo(databasePath));
            Assert.That(File.Exists(databasePath), Is.True);
            Assert.That(_api.IsDatabaseReady(), Is.True);
        });
    }

    [Test]
    public async Task SetupDatabaseAsync_SimpleOverload_WithDefaultParameters_CreatesSuccessfulResult()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "default_params.db");

        // Act
        var result = await _api.SetupDatabaseAsync(databasePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsSetupSuccessful, Is.True);
            Assert.That(result.DatabasePath, Is.EqualTo(databasePath));
            Assert.That(File.Exists(databasePath), Is.True);
            Assert.That(_api.IsDatabaseReady(), Is.True);
        });
    }

    [Test]
    public async Task SetupDatabaseAsync_SimpleOverload_InvalidPath_ReturnsFailureResult()
    {
        // Arrange - Use empty path to guarantee failure
        var invalidPath = "";

        // Act
        var result = await _api.SetupDatabaseAsync(invalidPath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsSetupSuccessful, Is.False);
            Assert.That(result.HasErrors, Is.True);
            Assert.That(_api.IsDatabaseReady(), Is.False);
        });
    }

    [Test]
    public async Task SetupDatabaseAsync_SimpleOverload_OverwriteEnabled_ReplacesExistingFile()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "overwrite_simple.db");
        File.WriteAllText(databasePath, "existing content");

        // Act
        var result = await _api.SetupDatabaseAsync(databasePath, null, true);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsSetupSuccessful, Is.True);
            Assert.That(File.Exists(databasePath), Is.True);
            Assert.That(_api.IsDatabaseReady(), Is.True);
        });
    }

    [Test]
    public async Task SetupDatabaseAsync_SimpleOverload_ExistingFileWithoutOverwrite_ReturnsFailure()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "existing_simple.db");
        File.WriteAllText(databasePath, "existing content");

        // Act
        var result = await _api.SetupDatabaseAsync(databasePath, null, false);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsSetupSuccessful, Is.False);
            Assert.That(result.HasErrors, Is.True);
            Assert.That(_api.IsDatabaseReady(), Is.False);
        });
    }

    [Test]
    public async Task SetupDatabaseAsync_SimpleOverload_WithLargeCustomPropertyList_HandlesCorrectly()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "large_props.db");
        var customProperties = Enumerable.Range(1, 100)
            .Select(i => $"Property{i}")
            .ToList();

        // Act
        var result = await _api.SetupDatabaseAsync(databasePath, customProperties, false);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsSetupSuccessful, Is.True);
            Assert.That(result.Message, Does.Contain("100 custom property types"));
            Assert.That(_api.IsDatabaseReady(), Is.True);
        });
    }

    [Test]
    public async Task SetupDatabaseAsync_SimpleOverload_EmptyCustomPropertyList_HandlesCorrectly()
    {
        // Arrange
        var databasePath = Path.Combine(_testDirectory, "empty_props.db");
        var customProperties = new List<string>();

        // Act
        var result = await _api.SetupDatabaseAsync(databasePath, customProperties, false);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result.IsSetupSuccessful, Is.True);
            Assert.That(result.Message, Does.Not.Contain("custom property types"));
            Assert.That(_api.IsDatabaseReady(), Is.True);
        });
    }

    #endregion

    #region Multiple Setup Calls Tests

    [Test]
    public async Task SetupDatabaseAsync_MultipleCalls_ReplacesConnection()
    {
        // Arrange
        var firstPath = Path.Combine(_testDirectory, "first.db");
        var secondPath = Path.Combine(_testDirectory, "second.db");

        // Act
        var firstResult = await _api.SetupDatabaseAsync(firstPath);
        var firstDbPath = _api.GetDatabasePath();

        var secondResult = await _api.SetupDatabaseAsync(secondPath);
        var secondDbPath = _api.GetDatabasePath();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(firstResult.IsSetupSuccessful, Is.True);
            Assert.That(secondResult.IsSetupSuccessful, Is.True);
            Assert.That(firstDbPath, Is.EqualTo(firstPath));
            Assert.That(secondDbPath, Is.EqualTo(secondPath));
            Assert.That(_api.IsDatabaseReady(), Is.True);
            Assert.That(File.Exists(firstPath), Is.True);
            Assert.That(File.Exists(secondPath), Is.True);
        });
    }

    [Test]
    public async Task SetupDatabaseAsync_AfterPreviousFailure_CanSucceed()
    {
        // Arrange - Use an empty path to guarantee failure
        var invalidPath = "";
        var validPath = Path.Combine(_testDirectory, "valid.db");

        // Act
        var failureResult = await _api.SetupDatabaseAsync(invalidPath);
        var successResult = await _api.SetupDatabaseAsync(validPath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(failureResult.IsSetupSuccessful, Is.False,
                "Expected setup to fail with empty path");
            Assert.That(successResult.IsSetupSuccessful, Is.True,
                "Expected setup to succeed with valid path after previous failure");
            Assert.That(_api.IsDatabaseReady(), Is.True);
            Assert.That(_api.GetDatabasePath(), Is.EqualTo(validPath));
        });
    }

    [Test]
    public async Task SetupDatabaseAsync_ConcurrentCalls_HandlesCorrectly()
    {
        // Arrange
        var paths = Enumerable.Range(1, 5)
            .Select(i => Path.Combine(_testDirectory, $"concurrent_{i}.db"))
            .ToList();

        // Act
        var tasks = paths.Select(path => _api.SetupDatabaseAsync(path));
        var results = await Task.WhenAll(tasks);

        // Ensure the API is properly closed before checking results
        await _api.CloseAsync();

        // Assert
        // Only the last setup should be active
        Assert.Multiple(() =>
        {
            Assert.That(results.All(r => r.IsSetupSuccessful), Is.True);
            Assert.That(_api.IsDatabaseReady(), Is.False); // Should be false after CloseAsync
            Assert.That(paths.All(File.Exists), Is.True);
        });
    }

    #endregion
}