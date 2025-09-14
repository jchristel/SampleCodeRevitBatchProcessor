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

    [Test]
    public async Task CheckDatabaseIntegrityAsync_DiagnosticTest_DocumentActualBehavior()
    {
        // This test documents what CheckDatabaseIntegrityAsync actually does

        // Test 1: Uninitialized
        var uninitializedResult = await _databaseService.CheckDatabaseIntegrityAsync();
        Console.WriteLine($"Uninitialized database integrity: {uninitializedResult}");

        // Test 2: Initialized but no tables
        await _databaseService.InitializeAsync(_testDatabasePath);
        var noTablesResult = await _databaseService.CheckDatabaseIntegrityAsync();
        Console.WriteLine($"Initialized, no tables integrity: {noTablesResult}");

        // Test 3: With tables created
        await _databaseService.CreateTablesAsync();
        var withTablesResult = await _databaseService.CheckDatabaseIntegrityAsync();
        Console.WriteLine($"With tables integrity: {withTablesResult}");

        // Test 4: With data
        var revision = new Revision(DateTime.Now, "Test");
        await _databaseService.Connection.InsertAsync(revision);
        var withDataResult = await _databaseService.CheckDatabaseIntegrityAsync();
        Console.WriteLine($"With data integrity: {withDataResult}");

        // Test 5: Manual integrity check query
        try
        {
            var manualCheck = await _databaseService.Connection.QueryAsync<dynamic>(
                "SELECT name FROM sqlite_master LIMIT 1");
            Console.WriteLine($"Manual integrity query returned {manualCheck.Count} results");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Manual integrity query failed: {ex.Message}");
        }

        // Document the actual behavior pattern
        Assert.Multiple(() =>
        {
            // Document what we observe
            Assert.That(uninitializedResult, Is.False, "Uninitialized should return false");

            // The other assertions depend on what we actually observe
            Console.WriteLine("=== ACTUAL BEHAVIOR PATTERN ===");
            Console.WriteLine($"Uninitialized: {uninitializedResult}");
            Console.WriteLine($"No tables: {noTablesResult}");
            Console.WriteLine($"With tables: {withTablesResult}");
            Console.WriteLine($"With data: {withDataResult}");
        });

        // For now, just pass this diagnostic test - we'll use the output to write proper tests
        Assert.Pass("Diagnostic test - check console output for actual behavior");
    }

    [Test]
    public void CheckDatabaseIntegrityAsync_WithoutInitialization_ReturnsFalse()
    {
        // This should consistently return false
        // Act
        var result = _databaseService.CheckDatabaseIntegrityAsync().Result;

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public async Task CheckDatabaseIntegrityAsync_AfterClose_ReturnsFalse()
    {
        // This should consistently return false
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CloseAsync();

        // Act
        var result = await _databaseService.CheckDatabaseIntegrityAsync();

        // Assert
        Assert.That(result, Is.False);
    }
}