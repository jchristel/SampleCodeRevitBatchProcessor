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

    #region Document Management Tests - AddDocumentToRevision

    [Test]
    public async Task AddDocumentToRevisionAsync_WithValidIds_AddsDocumentSuccessfully()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        await _repository.InsertAsync(revision);
        var documentId = 123;

        // Act
        var result = await _repository.AddDocumentToRevisionAsync(revision.Id, documentId);

        // Assert
        Assert.That(result, Is.EqualTo(1));

        var updated = await _repository.GetByIdAsync(revision.Id);
        Assert.That(updated.DocumentIds, Contains.Item(documentId));
    }

    [Test]
    public async Task AddDocumentToRevisionAsync_DuplicateDocument_DoesNotAddAgain()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        await _repository.InsertAsync(revision);
        var documentId = 123;

        await _repository.AddDocumentToRevisionAsync(revision.Id, documentId);

        // Act - Try to add same document again
        var result = await _repository.AddDocumentToRevisionAsync(revision.Id, documentId);

        // Assert
        Assert.That(result, Is.EqualTo(0)); // No change

        var updated = await _repository.GetByIdAsync(revision.Id);
        Assert.That(updated.DocumentIds, Has.Count.EqualTo(1));
    }

    [Test]
    public async Task AddDocumentToRevisionAsync_NonExistentRevision_ReturnsZero()
    {
        // Act
        var result = await _repository.AddDocumentToRevisionAsync(99999, 123);

        // Assert
        Assert.That(result, Is.EqualTo(0));
    }

    #endregion

    #region Document Management Tests - RemoveDocumentFromRevision

    [Test]
    public async Task RemoveDocumentFromRevisionAsync_ExistingDocument_RemovesSuccessfully()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        await _repository.InsertAsync(revision);
        var documentId = 123;

        await _repository.AddDocumentToRevisionAsync(revision.Id, documentId);

        // Act
        var result = await _repository.RemoveDocumentFromRevisionAsync(revision.Id, documentId);

        // Assert
        Assert.That(result, Is.EqualTo(1));

        var updated = await _repository.GetByIdAsync(revision.Id);
        Assert.That(updated.DocumentIds, Does.Not.Contain(documentId));
    }

    [Test]
    public async Task RemoveDocumentFromRevisionAsync_NonExistentDocument_ReturnsZero()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        await _repository.InsertAsync(revision);

        // Act - Try to remove a document that was never added
        var result = await _repository.RemoveDocumentFromRevisionAsync(revision.Id, 123);

        // Assert
        Assert.That(result, Is.EqualTo(0));
    }

    [Test]
    public async Task RemoveDocumentFromRevisionAsync_NonExistentRevision_ReturnsZero()
    {
        // Act
        var result = await _repository.RemoveDocumentFromRevisionAsync(99999, 123);

        // Assert
        Assert.That(result, Is.EqualTo(0));
    }

    #endregion

    #region Document Management Tests - AddDocumentsToRevision

    [Test]
    public async Task AddDocumentsToRevisionAsync_WithMultipleDocuments_AddsAllSuccessfully()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        await _repository.InsertAsync(revision);
        var documentIds = new[] { 100, 101, 102 };

        // Act
        var result = await _repository.AddDocumentsToRevisionAsync(revision.Id, documentIds);

        // Assert
        Assert.That(result, Is.EqualTo(1));

        var updated = await _repository.GetByIdAsync(revision.Id);
        Assert.Multiple(() =>
        {
            Assert.That(updated.DocumentIds, Has.Count.EqualTo(3));
            Assert.That(updated.DocumentIds, Is.EquivalentTo(documentIds));
        });
    }

    [Test]
    public async Task AddDocumentsToRevisionAsync_WithSomeDuplicates_OnlyAddsNew()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        await _repository.InsertAsync(revision);

        await _repository.AddDocumentToRevisionAsync(revision.Id, 100);
        var newDocumentIds = new[] { 100, 101, 102 }; // 100 already exists

        // Act
        var result = await _repository.AddDocumentsToRevisionAsync(revision.Id, newDocumentIds);

        // Assert
        Assert.That(result, Is.EqualTo(1));

        var updated = await _repository.GetByIdAsync(revision.Id);
        Assert.Multiple(() =>
        {
            Assert.That(updated.DocumentIds, Has.Count.EqualTo(3));
            Assert.That(updated.DocumentIds, Is.EquivalentTo(new[] { 100, 101, 102 }));
        });
    }

    [Test]
    public async Task AddDocumentsToRevisionAsync_AllDuplicates_ReturnsZero()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        await _repository.InsertAsync(revision);
        var documentIds = new[] { 100, 101 };

        await _repository.AddDocumentsToRevisionAsync(revision.Id, documentIds);

        // Act - Try to add the same documents again
        var result = await _repository.AddDocumentsToRevisionAsync(revision.Id, documentIds);

        // Assert
        Assert.That(result, Is.EqualTo(0));
    }

    #endregion

    #region Document Management Tests - RemoveDocumentsFromRevision

    [Test]
    public async Task RemoveDocumentsFromRevisionAsync_WithMultipleDocuments_RemovesAllSuccessfully()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        await _repository.InsertAsync(revision);
        var documentIds = new[] { 100, 101, 102, 103 };

        await _repository.AddDocumentsToRevisionAsync(revision.Id, documentIds);

        // Act - Remove a subset
        var toRemove = new[] { 101, 103 };
        var result = await _repository.RemoveDocumentsFromRevisionAsync(revision.Id, toRemove);

        // Assert
        Assert.That(result, Is.EqualTo(1));

        var updated = await _repository.GetByIdAsync(revision.Id);
        Assert.Multiple(() =>
        {
            Assert.That(updated.DocumentIds, Has.Count.EqualTo(2));
            Assert.That(updated.DocumentIds, Is.EquivalentTo(new[] { 100, 102 }));
        });
    }

    [Test]
    public async Task RemoveDocumentsFromRevisionAsync_NonExistentDocuments_ReturnsZero()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        await _repository.InsertAsync(revision);

        await _repository.AddDocumentToRevisionAsync(revision.Id, 100);

        // Act - Try to remove documents that are not in this revision
        var result = await _repository.RemoveDocumentsFromRevisionAsync(revision.Id, new[] { 200, 300 });

        // Assert
        Assert.That(result, Is.EqualTo(0));
    }

    #endregion

    #region Document Management Tests - SetRevisionDocuments

    [Test]
    public async Task SetRevisionDocumentsAsync_ReplacesExistingDocuments()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        await _repository.InsertAsync(revision);

        await _repository.AddDocumentsToRevisionAsync(revision.Id, new[] { 100, 101, 102 });

        // Act - Replace with a completely different list
        var newDocuments = new[] { 200, 201 };
        var result = await _repository.SetRevisionDocumentsAsync(revision.Id, newDocuments);

        // Assert
        Assert.That(result, Is.EqualTo(1));

        var updated = await _repository.GetByIdAsync(revision.Id);
        Assert.Multiple(() =>
        {
            Assert.That(updated.DocumentIds, Has.Count.EqualTo(2));
            Assert.That(updated.DocumentIds, Is.EquivalentTo(newDocuments));
        });
    }

    [Test]
    public async Task SetRevisionDocumentsAsync_WithDuplicates_RemovesDuplicates()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        await _repository.InsertAsync(revision);

        // Act - Set with duplicates in the input list
        var documentsWithDuplicates = new[] { 100, 101, 100, 102, 101 };
        var result = await _repository.SetRevisionDocumentsAsync(revision.Id, documentsWithDuplicates);

        // Assert
        Assert.That(result, Is.EqualTo(1));

        var updated = await _repository.GetByIdAsync(revision.Id);
        Assert.Multiple(() =>
        {
            Assert.That(updated.DocumentIds, Has.Count.EqualTo(3));
            Assert.That(updated.DocumentIds, Is.EquivalentTo(new[] { 100, 101, 102 }));
        });
    }

    [Test]
    public async Task SetRevisionDocumentsAsync_NonExistentRevision_ReturnsZero()
    {
        // Act
        var result = await _repository.SetRevisionDocumentsAsync(99999, new[] { 100, 101 });

        // Assert
        Assert.That(result, Is.EqualTo(0));
    }

    #endregion

    #region Document Management Tests - GetRevisionsByDocumentId

    [Test]
    public async Task GetRevisionsByDocumentIdAsync_FindsAllRevisionsContainingDocument()
    {
        // Arrange
        var revision1 = new Revision(new DateTime(2024, 1, 15), "Revision 1");
        var revision2 = new Revision(new DateTime(2024, 2, 15), "Revision 2");
        var revision3 = new Revision(new DateTime(2024, 3, 15), "Revision 3");

        await _repository.InsertAsync(revision1);
        await _repository.InsertAsync(revision2);
        await _repository.InsertAsync(revision3);

        var documentId = 123;
        await _repository.AddDocumentToRevisionAsync(revision1.Id, documentId);
        await _repository.AddDocumentToRevisionAsync(revision2.Id, documentId);
        await _repository.AddDocumentToRevisionAsync(revision3.Id, 456); // Different document

        // Act
        var result = await _repository.GetRevisionsByDocumentIdAsync(documentId);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Has.Count.EqualTo(2));
            Assert.That(result.All(r => r.DocumentIds.Contains(documentId)), Is.True);

            // Should be ordered by date descending
            Assert.That(result[0].Description, Is.EqualTo("Revision 2"));
            Assert.That(result[1].Description, Is.EqualTo("Revision 1"));
        });
    }

    [Test]
    public async Task GetRevisionsByDocumentIdAsync_NoMatchingRevisions_ReturnsEmptyList()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        await _repository.InsertAsync(revision);
        await _repository.AddDocumentToRevisionAsync(revision.Id, 100);

        // Act
        var result = await _repository.GetRevisionsByDocumentIdAsync(999);

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    #endregion

    #region Document Management Tests - Helper Methods

    [Test]
    public async Task GetDocumentCountAsync_ReturnsCorrectCount()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        await _repository.InsertAsync(revision);

        await _repository.AddDocumentsToRevisionAsync(revision.Id, new[] { 100, 101, 102 });

        // Act
        var result = await _repository.GetDocumentCountAsync(revision.Id);

        // Assert
        Assert.That(result, Is.EqualTo(3));
    }

    [Test]
    public async Task GetDocumentCountAsync_EmptyRevision_ReturnsZero()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        await _repository.InsertAsync(revision);

        // Act
        var result = await _repository.GetDocumentCountAsync(revision.Id);

        // Assert
        Assert.That(result, Is.EqualTo(0));
    }

    [Test]
    public async Task GetDocumentCountAsync_NonExistentRevision_ReturnsZero()
    {
        // Act
        var result = await _repository.GetDocumentCountAsync(99999);

        // Assert
        Assert.That(result, Is.EqualTo(0));
    }

    [Test]
    public async Task RevisionContainsDocumentAsync_DocumentExists_ReturnsTrue()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        await _repository.InsertAsync(revision);
        var documentId = 123;

        await _repository.AddDocumentToRevisionAsync(revision.Id, documentId);

        // Act
        var result = await _repository.RevisionContainsDocumentAsync(revision.Id, documentId);

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public async Task RevisionContainsDocumentAsync_DocumentDoesNotExist_ReturnsFalse()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        await _repository.InsertAsync(revision);

        // Act
        var result = await _repository.RevisionContainsDocumentAsync(revision.Id, 123);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public async Task RevisionContainsDocumentAsync_NonExistentRevision_ReturnsFalse()
    {
        // Act
        var result = await _repository.RevisionContainsDocumentAsync(99999, 123);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public async Task GetEmptyRevisionsAsync_ReturnsOnlyRevisionsWithNoDocuments()
    {
        // Arrange
        var emptyRevision1 = new Revision(new DateTime(2024, 1, 15), "Empty 1");
        var emptyRevision2 = new Revision(new DateTime(2024, 2, 15), "Empty 2");
        var fullRevision = new Revision(new DateTime(2024, 3, 15), "Full");

        await _repository.InsertAsync(emptyRevision1);
        await _repository.InsertAsync(emptyRevision2);
        await _repository.InsertAsync(fullRevision);

        await _repository.AddDocumentToRevisionAsync(fullRevision.Id, 123);

        // Act
        var result = await _repository.GetEmptyRevisionsAsync();

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
        Assert.That(result.All(r => r.DocumentIds.Count == 0), Is.True);
    }

    [Test]
    public async Task GetRevisionStatisticsAsync_ReturnsCorrectStatistics()
    {
        // Arrange
        var revision1 = new Revision(new DateTime(2024, 1, 15), "Revision 1");
        var revision2 = new Revision(new DateTime(2024, 2, 15), "Revision 2");
        var revision3 = new Revision(new DateTime(2024, 3, 15), "Revision 3");

        await _repository.InsertAsync(revision1);
        await _repository.InsertAsync(revision2);
        await _repository.InsertAsync(revision3);

        await _repository.AddDocumentsToRevisionAsync(revision1.Id, new[] { 100, 101 });       // 2 documents
        await _repository.AddDocumentsToRevisionAsync(revision2.Id, new[] { 200, 201, 202 });  // 3 documents
        // revision3 has no documents

        // Act
        var result = await _repository.GetRevisionStatisticsAsync();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result["TotalRevisions"], Is.EqualTo(3));
            Assert.That(result["EmptyRevisions"], Is.EqualTo(1));
            Assert.That(result["RevisionsWithDocuments"], Is.EqualTo(2));
            Assert.That(result["TotalDocumentReferences"], Is.EqualTo(5));
            Assert.That(result["MaxDocumentsInRevision"], Is.EqualTo(3));
            Assert.That(result["MinDocumentsInRevision"], Is.EqualTo(0));
        });
    }

    #endregion

    #region Integration Tests

    [Test]
    public async Task IntegrationTest_CompleteRevisionLifecycle()
    {
        // Create revision
        var revision = new Revision(new DateTime(2024, 2, 15), "Initial Revision");
        await _repository.InsertAsync(revision);

        // Add documents
        var documentIds = new[] { 100, 101, 102 };
        await _repository.AddDocumentsToRevisionAsync(revision.Id, documentIds);

        // Verify documents added
        Assert.That(await _repository.GetDocumentCountAsync(revision.Id), Is.EqualTo(3));

        // Remove one document
        await _repository.RemoveDocumentFromRevisionAsync(revision.Id, 101);
        Assert.That(await _repository.GetDocumentCountAsync(revision.Id), Is.EqualTo(2));

        // Check membership
        Assert.That(await _repository.RevisionContainsDocumentAsync(revision.Id, 100), Is.True);
        Assert.That(await _repository.RevisionContainsDocumentAsync(revision.Id, 101), Is.False);

        // Replace all documents
        await _repository.SetRevisionDocumentsAsync(revision.Id, new[] { 200, 201, 202, 203 });
        Assert.That(await _repository.GetDocumentCountAsync(revision.Id), Is.EqualTo(4));

        // Verify lookup by document ID
        var revisionsContaining200 = await _repository.GetRevisionsByDocumentIdAsync(200);
        Assert.That(revisionsContaining200, Has.Count.EqualTo(1));

        // Get statistics
        var stats = await _repository.GetRevisionStatisticsAsync();
        Assert.Multiple(() =>
        {
            Assert.That(stats["TotalRevisions"], Is.EqualTo(1));
            Assert.That(stats["RevisionsWithDocuments"], Is.EqualTo(1));
        });
    }

    #endregion
}