using NUnit.Framework;
using duHastNet.DocManager.Core.Services;
using duHastNet.DocManager.Core.Models;
using System.IO;

namespace duHastNet.DocManager.Core.Tests.Services;

[TestFixture]
public class DatabaseServiceTests_SqlOperations
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
    public async Task Connection_OrmOperations_WorkCorrectly()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        // Act - Use ORM methods for all operations
        var revision = new Revision(DateTime.Now, "ORM Test Revision");
        var insertResult = await _databaseService.Connection.InsertAsync(revision);

        var retrievedRevision = await _databaseService.Connection.GetAsync<Revision>(revision.Id);

        // Update using ORM
        retrievedRevision.Description = "Updated ORM Revision";
        var updateResult = await _databaseService.Connection.UpdateAsync(retrievedRevision);

        // Query using ORM LINQ
        var revisions = await _databaseService.Connection.Table<Revision>()
            .Where(r => r.Description.Contains("Updated"))
            .ToListAsync();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(insertResult, Is.EqualTo(1));
            Assert.That(updateResult, Is.EqualTo(1));
            Assert.That(retrievedRevision.Description, Is.EqualTo("Updated ORM Revision"));
            Assert.That(revisions, Has.Count.EqualTo(1));
            Assert.That(revisions[0].Description, Is.EqualTo("Updated ORM Revision"));
        });
    }

    [Test]
    public async Task Connection_ComplexOrmQueries_WorkCorrectly()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        // Create test data using ORM batch operations with actual dates
        var twoDaysAgo = DateTime.Now.AddDays(-2);
        var oneDayAgo = DateTime.Now.AddDays(-1);
        var today = DateTime.Now;

        var revisions = new List<Revision>
        {
            new Revision(twoDaysAgo, "Design Phase"),
            new Revision(oneDayAgo, "Construction Phase"),
            new Revision(today, "Final Phase")
        };
        await _databaseService.Connection.InsertAllAsync(revisions);

        // Act - Use ORM LINQ queries for complex operations
        var phaseCount = await _databaseService.Connection.Table<Revision>()
            .CountAsync(r => r.Description.Contains("Phase"));

        // Use a fixed date for comparison instead of DateTime.Now.AddDays() in LINQ
        var cutoffDate = DateTime.Now.AddDays(-3);
        var recentRevisions = await _databaseService.Connection.Table<Revision>()
            .Where(r => r.RevisionDate >= cutoffDate)
            .OrderByDescending(r => r.RevisionDate)
            .ToListAsync();

        var hasConstructionPhase = await _databaseService.Connection.Table<Revision>()
            .Where(r => r.Description == "Construction Phase")
            .CountAsync() > 0;

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(phaseCount, Is.EqualTo(3));
            Assert.That(recentRevisions, Has.Count.EqualTo(3));
            Assert.That(recentRevisions[0].Description, Is.EqualTo("Final Phase")); // Most recent first
            Assert.That(hasConstructionPhase, Is.True);
        });
    }

    [Test]
    public async Task Connection_TransactionWithOrm_WorksCorrectly()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        await _databaseService.CreateTablesAsync();

        // Act - Use ORM within sqlite-net-pcl transaction
        await _databaseService.Connection.RunInTransactionAsync((conn) =>
        {
            // All ORM operations within transaction
            var revision = new Revision(DateTime.Now, "Transaction Test");
            conn.Insert(revision);

            var document = new Document("TXN-001", "Transaction Document", "1", revision.Id);
            conn.Insert(document);

            //var customProperty = new CustomProperty(document.Id, "Status", "InTransaction");
            //conn.Insert(customProperty);
        });

        // Verify using ORM queries
        var revisions = await _databaseService.Connection.Table<Revision>()
            .Where(r => r.Description == "Transaction Test")
            .ToListAsync();

        var documents = await _databaseService.Connection.Table<Document>()
            .Where(d => d.Number == "TXN-001")
            .ToListAsync();

        //var properties = await _databaseService.Connection.Table<CustomProperty>()
        //    .Where(cp => cp.PropertyValue == "InTransaction")
        //    .ToListAsync();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(revisions, Has.Count.EqualTo(1));
            Assert.That(documents, Has.Count.EqualTo(1));
            //Assert.That(properties, Has.Count.EqualTo(1));

            // Verify relationships work
            Assert.That(documents[0].RevisionId, Is.EqualTo(revisions[0].Id));
            //Assert.That(properties[0].DocumentId, Is.EqualTo(documents[0].Id));
        });
    }

    #region GetDataVersionAsync Tests

    [Test]
    public async Task GetDataVersionAsync_AfterInitialization_ReturnsNonNegativeValue()
    {
        // Arrange & Act
        await _databaseService.InitializeAsync(_testDatabasePath);
        var version = await _databaseService.GetDataVersionAsync();

        // Assert
        Assert.That(version, Is.GreaterThanOrEqualTo(0));
    }

    [Test]
    public async Task GetDataVersionAsync_AfterWrite_ReturnsIncrementedValue()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);
        var versionBefore = await _databaseService.GetDataVersionAsync();

        // Act - SQLiteAsyncConnection pools connections by path, so a second
        // SQLiteAsyncConnection to the same file reuses the same underlying
        // connection and does not increment data_version. A sync SQLiteConnection
        // bypasses the pool and creates a genuinely separate connection.
        var secondConnection = new SQLite.SQLiteConnection(_testDatabasePath);
        try
        {
            secondConnection.CreateTable<Revision>();
            var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
            secondConnection.Insert(revision);
        }
        finally
        {
            secondConnection.Close();
        }

        var versionAfter = await _databaseService.GetDataVersionAsync();

        // Assert
        Assert.That(versionAfter, Is.GreaterThan(versionBefore));
    }

    [Test]
    public async Task GetDataVersionAsync_AfterReadOnly_ReturnsSameValue()
    {
        // Arrange
        await _databaseService.InitializeAsync(_testDatabasePath);

        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        await _databaseService.Connection.InsertAsync(revision);

        var versionBefore = await _databaseService.GetDataVersionAsync();

        // Act - read only operation
        await _databaseService.Connection.Table<Revision>().ToListAsync();

        var versionAfter = await _databaseService.GetDataVersionAsync();

        // Assert
        Assert.That(versionAfter, Is.EqualTo(versionBefore));
    }

    #endregion
}