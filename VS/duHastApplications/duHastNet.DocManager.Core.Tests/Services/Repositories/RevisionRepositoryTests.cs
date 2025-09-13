using NUnit.Framework;
using SQLite;
using duHastNet.DocManager.Core.Services.Repositories;
using duHastNet.DocManager.Core.Models;
using System.IO;

namespace duHastNet.DocManager.Core.Tests.Services.Repositories;


[TestFixture]
public class RevisionRepositoryTests
{
    private SQLiteAsyncConnection _connection;
    private string _databasePath;
    private RevisionRepository _repository;

    [SetUp]
    public async Task Setup()
    {
        // Create a temporary database file for testing
        _databasePath = Path.GetTempFileName();

        var connectionString = new SQLiteConnectionString(_databasePath,
            storeDateTimeAsTicks: false,
            openFlags: SQLiteOpenFlags.ReadWrite | SQLiteOpenFlags.Create,
            key: null);

        _connection = new SQLiteAsyncConnection(connectionString);

        // Create tables
        await _connection.CreateTableAsync<Revision>();

        _repository = new RevisionRepository(_connection);
    }

    [TearDown]
    public async Task TearDown()
    {
        if (_connection != null)
        {
            await _connection.CloseAsync();
        }

        if (File.Exists(_databasePath))
        {
            File.Delete(_databasePath);
        }
    }

    [Test]
    public async Task GetRevisionsByDateRangeAsync_WithRevisionsInRange_ReturnsFilteredRevisions()
    {
        // Arrange
        var revisions = new[]
        {
            new Revision(new DateTime(2024, 1, 15), "January Release"),
            new Revision(new DateTime(2024, 2, 10), "February Release"),
            new Revision(new DateTime(2024, 2, 25), "Late February"),
            new Revision(new DateTime(2024, 3, 5), "March Release")
        };

        foreach (var revision in revisions)
        {
            await _repository.InsertAsync(revision);
        }

        var startDate = new DateTime(2024, 2, 1);
        var endDate = new DateTime(2024, 2, 28);

        // Act
        var result = await _repository.GetRevisionsByDateRangeAsync(startDate, endDate);

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
        Assert.That(result.All(r => r.RevisionDate >= startDate && r.RevisionDate <= endDate), Is.True);

        // Should be ordered by date descending (newest first)
        Assert.That(result[0].Description, Is.EqualTo("Late February"));
        Assert.That(result[1].Description, Is.EqualTo("February Release"));
    }

    [Test]
    public async Task GetRevisionsByDateRangeAsync_NoRevisionsInRange_ReturnsEmptyList()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 1, 15), "January Release");
        await _repository.InsertAsync(revision);

        var startDate = new DateTime(2024, 3, 1);
        var endDate = new DateTime(2024, 3, 31);

        // Act
        var result = await _repository.GetRevisionsByDateRangeAsync(startDate, endDate);

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    [Test]
    public async Task GetRevisionsByDateRangeAsync_ExactBoundaryDates_IncludesBoundaryRevisions()
    {
        // Arrange
        var startDate = new DateTime(2024, 2, 1);
        var endDate = new DateTime(2024, 2, 28);

        var revisions = new[]
        {
            new Revision(startDate, "Start Date Revision"),
            new Revision(endDate, "End Date Revision"),
            new Revision(new DateTime(2024, 2, 15), "Middle Revision")
        };

        foreach (var revision in revisions)
        {
            await _repository.InsertAsync(revision);
        }

        // Act
        var result = await _repository.GetRevisionsByDateRangeAsync(startDate, endDate);

        // Assert
        Assert.That(result, Has.Count.EqualTo(3));
        Assert.That(result.Any(r => r.Description == "Start Date Revision"), Is.True);
        Assert.That(result.Any(r => r.Description == "End Date Revision"), Is.True);
        Assert.That(result.Any(r => r.Description == "Middle Revision"), Is.True);
    }

    [Test]
    public async Task GetLatestRevisionAsync_WithMultipleRevisions_ReturnsNewestRevision()
    {
        // Arrange
        var revisions = new[]
        {
            new Revision(new DateTime(2024, 1, 15), "Oldest"),
            new Revision(new DateTime(2024, 3, 5), "Newest"),
            new Revision(new DateTime(2024, 2, 10), "Middle")
        };

        foreach (var revision in revisions)
        {
            await _repository.InsertAsync(revision);
        }

        // Act
        var result = await _repository.GetLatestRevisionAsync();

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result.Description, Is.EqualTo("Newest"));
        Assert.That(result.RevisionDate, Is.EqualTo(new DateTime(2024, 3, 5)));
    }

    [Test]
    public async Task GetLatestRevisionAsync_SameDateMultipleRevisions_ReturnsHighestId()
    {
        // Arrange
        var sameDate = new DateTime(2024, 2, 15);
        var revisions = new[]
        {
            new Revision(sameDate, "First"),
            new Revision(sameDate, "Second"),
            new Revision(sameDate, "Third")
        };

        foreach (var revision in revisions)
        {
            await _repository.InsertAsync(revision);
        }

        // Act
        var result = await _repository.GetLatestRevisionAsync();

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result.Description, Is.EqualTo("Third")); // Should be the last inserted (highest ID)
    }

    [Test]
    public async Task GetLatestRevisionAsync_NoRevisions_ReturnsNull()
    {
        // Act
        var result = await _repository.GetLatestRevisionAsync();

        // Assert
        Assert.That(result, Is.Null);
    }

    [Test]
    public async Task GetRevisionsByDateAsync_WithRevisionsOnSpecificDate_ReturnsAllRevisionsForThatDate()
    {
        // Arrange
        var targetDate = new DateTime(2024, 2, 15);
        var otherDate = new DateTime(2024, 2, 16);

        var revisions = new[]
        {
            new Revision(targetDate, "Morning Release"),
            new Revision(targetDate, "Afternoon Release"),
            new Revision(otherDate, "Other Day Release")
        };

        foreach (var revision in revisions)
        {
            await _repository.InsertAsync(revision);
        }

        // Act
        var result = await _repository.GetRevisionsByDateAsync(targetDate);

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
        Assert.That(result.All(r => r.RevisionDate.Date == targetDate.Date), Is.True);

        // Should be ordered by ID (insertion order)
        Assert.That(result[0].Description, Is.EqualTo("Morning Release"));
        Assert.That(result[1].Description, Is.EqualTo("Afternoon Release"));
    }

    [Test]
    public async Task GetRevisionsByDateAsync_DateWithTime_IgnoresTimeComponent()
    {
        // Arrange
        var baseDate = new DateTime(2024, 2, 15);
        var dateWithTime = new DateTime(2024, 2, 15, 14, 30, 45); // 2:30:45 PM

        var revision = new Revision(baseDate, "Test Revision");
        await _repository.InsertAsync(revision);

        // Act - Search with time component should still find the revision
        var result = await _repository.GetRevisionsByDateAsync(dateWithTime);

        // Assert
        Assert.That(result, Has.Count.EqualTo(1));
        Assert.That(result[0].Description, Is.EqualTo("Test Revision"));
    }

    [Test]
    public async Task GetRevisionsByDateAsync_NoRevisionsOnDate_ReturnsEmptyList()
    {
        // Arrange
        var existingDate = new DateTime(2024, 2, 15);
        var searchDate = new DateTime(2024, 2, 16);

        var revision = new Revision(existingDate, "Test Revision");
        await _repository.InsertAsync(revision);

        // Act
        var result = await _repository.GetRevisionsByDateAsync(searchDate);

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    [Test]
    public async Task GetRevisionsByDateAsync_DateAtMidnight_HandlesCorrectly()
    {
        // Arrange
        var midnightDate = new DateTime(2024, 2, 15, 0, 0, 0); // Exactly midnight
        var revision = new Revision(midnightDate, "Midnight Revision");
        await _repository.InsertAsync(revision);

        // Act
        var result = await _repository.GetRevisionsByDateAsync(midnightDate);

        // Assert
        Assert.That(result, Has.Count.EqualTo(1));
        Assert.That(result[0].Description, Is.EqualTo("Midnight Revision"));
    }

    [Test]
    public async Task InheritedMethods_WorkCorrectly()
    {
        // Test that inherited methods from BaseRepository work correctly

        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");

        // Act & Assert - Insert
        var insertResult = await _repository.InsertAsync(revision);
        Assert.That(insertResult, Is.EqualTo(1));
        Assert.That(revision.Id, Is.GreaterThan(0));

        // Act & Assert - GetById
        var retrieved = await _repository.GetByIdAsync(revision.Id);
        Assert.That(retrieved, Is.Not.Null);
        Assert.That(retrieved.Description, Is.EqualTo("Test Revision"));

        // Act & Assert - Update
        retrieved.Description = "Updated Description";
        var updateResult = await _repository.UpdateAsync(retrieved);
        Assert.That(updateResult, Is.EqualTo(1));

        // Act & Assert - Find
        var found = await _repository.FindAsync(r => r.Description.Contains("Updated"));
        Assert.That(found, Has.Count.EqualTo(1));

        // Act & Assert - Count
        var count = await _repository.CountAsync();
        Assert.That(count, Is.EqualTo(1));

        // Act & Assert - Delete
        var deleteResult = await _repository.DeleteAsync(revision.Id);
        Assert.That(deleteResult, Is.EqualTo(1));
    }

    [Test]
    public async Task GetRevisionsByDateRangeAsync_OrdersByDateDescending()
    {
        // Arrange - Insert revisions in random order
        var revisions = new[]
        {
            new Revision(new DateTime(2024, 2, 10), "Middle"),
            new Revision(new DateTime(2024, 2, 20), "Latest"),
            new Revision(new DateTime(2024, 2, 5), "Earliest")
        };

        foreach (var revision in revisions)
        {
            await _repository.InsertAsync(revision);
        }

        // Act
        var result = await _repository.GetRevisionsByDateRangeAsync(
            new DateTime(2024, 2, 1),
            new DateTime(2024, 2, 28));

        // Assert - Should be ordered newest to oldest
        Assert.That(result, Has.Count.EqualTo(3));
        Assert.That(result[0].Description, Is.EqualTo("Latest"));
        Assert.That(result[1].Description, Is.EqualTo("Middle"));
        Assert.That(result[2].Description, Is.EqualTo("Earliest"));
    }
}