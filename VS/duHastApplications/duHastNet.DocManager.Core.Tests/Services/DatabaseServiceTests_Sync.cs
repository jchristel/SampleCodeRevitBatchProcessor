using NUnit.Framework;
using duHastNet.DocManager.Core.Services;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.Database;
using System.IO;

namespace duHastNet.DocManager.Core.Tests.Services;

[TestFixture]
public class DatabaseServiceTests_Sync
{
    private DatabaseService _databaseService;
    private string _testDatabasePath;
    private string _testDirectory;

    [SetUp]
    public void Setup()
    {
        _databaseService = new DatabaseService();
        _testDirectory = Path.Combine(
            Path.GetTempPath(),
            "DatabaseServiceTests_Sync",
            Guid.NewGuid().ToString());
        _testDatabasePath = Path.Combine(_testDirectory, "test.db");
    }

    [TearDown]
    public void TearDown()
    {
        _databaseService?.Close();
        _databaseService?.Dispose();

        if (Directory.Exists(_testDirectory))
            Directory.Delete(_testDirectory, true);
    }

    #region Initialize Tests

    [Test]
    public void Initialize_WithValidPath_InitializesSuccessfully()
    {
        // Act
        _databaseService.Initialize(_testDatabasePath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(_databaseService.IsInitialized, Is.True);
            Assert.That(_databaseService.DatabasePath, Is.EqualTo(_testDatabasePath));
            Assert.That(_databaseService.SyncConnection, Is.Not.Null);
            Assert.That(File.Exists(_testDatabasePath), Is.True);
        });
    }

    [Test]
    public void Initialize_WithNullPath_ThrowsArgumentNullException()
    {
        // Act & Assert
        Assert.Throws<ArgumentNullException>(() => _databaseService.Initialize(null!));
    }

    [Test]
    public void Initialize_WithEmptyPath_ThrowsArgumentException()
    {
        // Act & Assert
        Assert.Throws<ArgumentException>(() => _databaseService.Initialize(string.Empty));
    }

    [Test]
    public void Initialize_WithWhitespacePath_ThrowsArgumentException()
    {
        // Act & Assert
        Assert.Throws<ArgumentException>(() => _databaseService.Initialize("   "));
    }

    [Test]
    public void Initialize_ConfiguresBusyTimeout()
    {
        // Arrange & Act
        _databaseService.Initialize(_testDatabasePath);

        // Assert - BusyTimeout property is directly readable on SQLiteConnection
        Assert.That(_databaseService.SyncConnection.BusyTimeout,
            Is.EqualTo(TimeSpan.FromSeconds(5)));
    }

    [Test]
    public void Initialize_WithNonExistentDirectory_CreatesDirectory()
    {
        // Arrange
        var deepPath = Path.Combine(_testDirectory, "subdir1", "subdir2", "database.db");

        // Act
        _databaseService.Initialize(deepPath);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(_databaseService.IsInitialized, Is.True);
            Assert.That(File.Exists(deepPath), Is.True);
            Assert.That(Directory.Exists(Path.GetDirectoryName(deepPath)), Is.True);
        });
    }

    #endregion

    #region CreateTables Tests

    [Test]
    public void CreateTables_CreatesAllRequiredTables()
    {
        // Arrange
        _databaseService.Initialize(_testDatabasePath);

        // Act - CreateTables is called inside Initialize, but call again to confirm idempotency
        _databaseService.CreateTables();

        // Assert - verify all four tables exist by inserting into each using the ORM
        Assert.Multiple(() =>
        {
            Assert.DoesNotThrow(() =>
                _databaseService.SyncConnection.Insert(
                    new Revision(new DateTime(2024, 2, 15), "Table Check")));

            Assert.DoesNotThrow(() =>
                _databaseService.SyncConnection.Insert(
                    new Document("A-101", "Table Check", "1", 1)));

            Assert.DoesNotThrow(() =>
                _databaseService.SyncConnection.Insert(
                    new CustomFieldDefinition("TestField", true)));

            Assert.DoesNotThrow(() =>
                _databaseService.SyncConnection.Insert(
                    new CustomProperty(1, 1, "TestValue")));
        });
    }

    #endregion

    #region Close Tests

    [Test]
    public void Close_AfterInitialization_ClosesConnection()
    {
        // Arrange
        _databaseService.Initialize(_testDatabasePath);
        Assert.That(_databaseService.IsInitialized, Is.True);

        // Act
        _databaseService.Close();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(_databaseService.IsInitialized, Is.False);
            Assert.That(_databaseService.DatabasePath, Is.Null);
        });
    }

    [Test]
    public void Close_WithoutInitialization_DoesNotThrow()
    {
        // Act & Assert - closing an uninitialised service must not throw
        Assert.DoesNotThrow(() => _databaseService.Close());
    }

    #endregion

    #region CheckDatabaseIntegrity Tests

    [Test]
    public void CheckDatabaseIntegrity_AfterInitialization_ReturnsTrue()
    {
        // Arrange
        _databaseService.Initialize(_testDatabasePath);

        // Act
        var result = _databaseService.CheckDatabaseIntegrity();

        // Assert
        Assert.That(result, Is.True);
    }

    #endregion

    #region GetDataVersion Tests

    [Test]
    public void GetDataVersion_AfterInitialization_ReturnsNonNegativeValue()
    {
        // Arrange
        _databaseService.Initialize(_testDatabasePath);

        // Act
        var version = _databaseService.GetDataVersion();

        // Assert
        Assert.That(version, Is.GreaterThanOrEqualTo(0));
    }

    [Test]
    public void GetDataVersion_AfterWrite_ReturnsIncrementedValue()
    {
        // Arrange
        _databaseService.Initialize(_testDatabasePath);
        var versionBefore = _databaseService.GetDataVersion();

        // Act - write via a second connection; data_version increments when
        // another connection commits a write to the same database file
        var secondConnection = new SQLite.SQLiteConnection(_testDatabasePath);
        try
        {
            var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
            secondConnection.Insert(revision);
        }
        finally
        {
            secondConnection.Close();
        }

        var versionAfter = _databaseService.GetDataVersion();

        // Assert
        Assert.That(versionAfter, Is.GreaterThan(versionBefore));
    }

    [Test]
    public void GetDataVersion_AfterReadOnly_ReturnsSameValue()
    {
        // Arrange
        _databaseService.Initialize(_testDatabasePath);

        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        _databaseService.SyncConnection.Insert(revision);

        var versionBefore = _databaseService.GetDataVersion();

        // Act - read only operation
        _databaseService.SyncConnection.Table<Revision>().ToList();

        var versionAfter = _databaseService.GetDataVersion();

        // Assert
        Assert.That(versionAfter, Is.EqualTo(versionBefore));
    }

    #endregion
}
