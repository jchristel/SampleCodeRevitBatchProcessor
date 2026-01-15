using NUnit.Framework;
using SQLite;
using duHastNet.DocManager.Core.Services.Repositories;
using duHastNet.DocManager.Core.Models;
using System.IO;

namespace duHastNet.DocManager.Core.Tests.Services.Repositories;

[TestFixture]
public class RevisionRepositorySyncTests
{
    private SQLiteConnection _connection;
    private string _databasePath;
    private RevisionRepositorySync _repository;

    [SetUp]
    public void Setup()
    {
        // Create a temporary database file for testing
        _databasePath = Path.GetTempFileName();

        var connectionString = new SQLiteConnectionString(_databasePath,
            storeDateTimeAsTicks: false,
            openFlags: SQLiteOpenFlags.ReadWrite | SQLiteOpenFlags.Create,
            key: null);

        _connection = new SQLiteConnection(connectionString);

        // Create tables
        _connection.CreateTable<Revision>();

        _repository = new RevisionRepositorySync(_connection);
    }

    [TearDown]
    public void TearDown()
    {
        _connection?.Close();

        if (File.Exists(_databasePath))
        {
            File.Delete(_databasePath);
        }
    }

    #region GetRevisionsByDateRange Tests

    [Test]
    public void GetRevisionsByDateRange_WithRevisionsInRange_ReturnsFilteredRevisions()
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
            _repository.Insert(revision);
        }

        var startDate = new DateTime(2024, 2, 1);
        var endDate = new DateTime(2024, 2, 28);

        // Act
        var result = _repository.GetRevisionsByDateRange(startDate, endDate);

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
        Assert.That(result.All(r => r.RevisionDate >= startDate && r.RevisionDate <= endDate), Is.True);

        // Should be ordered by date descending (newest first)
        Assert.That(result[0].Description, Is.EqualTo("Late February"));
        Assert.That(result[1].Description, Is.EqualTo("February Release"));
    }

    [Test]
    public void GetRevisionsByDateRange_NoRevisionsInRange_ReturnsEmptyList()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 1, 15), "January Release");
        _repository.Insert(revision);

        var startDate = new DateTime(2024, 3, 1);
        var endDate = new DateTime(2024, 3, 31);

        // Act
        var result = _repository.GetRevisionsByDateRange(startDate, endDate);

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    [Test]
    public void GetRevisionsByDateRange_ExactBoundaryDates_IncludesBoundaryRevisions()
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
            _repository.Insert(revision);
        }

        // Act
        var result = _repository.GetRevisionsByDateRange(startDate, endDate);

        // Assert
        Assert.That(result, Has.Count.EqualTo(3));
        Assert.That(result.Any(r => r.Description == "Start Date Revision"), Is.True);
        Assert.That(result.Any(r => r.Description == "End Date Revision"), Is.True);
        Assert.That(result.Any(r => r.Description == "Middle Revision"), Is.True);
    }

    [Test]
    public void GetRevisionsByDateRange_OrdersByDateDescending()
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
            _repository.Insert(revision);
        }

        // Act
        var result = _repository.GetRevisionsByDateRange(
            new DateTime(2024, 2, 1),
            new DateTime(2024, 2, 28));

        // Assert - Should be ordered newest to oldest
        Assert.That(result, Has.Count.EqualTo(3));
        Assert.That(result[0].Description, Is.EqualTo("Latest"));
        Assert.That(result[1].Description, Is.EqualTo("Middle"));
        Assert.That(result[2].Description, Is.EqualTo("Earliest"));
    }

    #endregion

    #region GetLatestRevision Tests

    [Test]
    public void GetLatestRevision_WithMultipleRevisions_ReturnsNewestRevision()
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
            _repository.Insert(revision);
        }

        // Act
        var result = _repository.GetLatestRevision();

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result.Description, Is.EqualTo("Newest"));
        Assert.That(result.RevisionDate, Is.EqualTo(new DateTime(2024, 3, 5)));
    }

    [Test]
    public void GetLatestRevision_SameDateMultipleRevisions_ReturnsHighestId()
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
            _repository.Insert(revision);
        }

        // Act
        var result = _repository.GetLatestRevision();

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result.Description, Is.EqualTo("Third")); // Should be the last inserted (highest ID)
    }

    [Test]
    public void GetLatestRevision_NoRevisions_ReturnsNull()
    {
        // Act
        var result = _repository.GetLatestRevision();

        // Assert
        Assert.That(result, Is.Null);
    }

    #endregion

    #region GetRevisionsByDate Tests

    [Test]
    public void GetRevisionsByDate_WithRevisionsOnSpecificDate_ReturnsAllRevisionsForThatDate()
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
            _repository.Insert(revision);
        }

        // Act
        var result = _repository.GetRevisionsByDate(targetDate);

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
        Assert.That(result.All(r => r.RevisionDate.Date == targetDate.Date), Is.True);

        // Should be ordered by ID (insertion order)
        Assert.That(result[0].Description, Is.EqualTo("Morning Release"));
        Assert.That(result[1].Description, Is.EqualTo("Afternoon Release"));
    }

    [Test]
    public void GetRevisionsByDate_DateWithTime_IgnoresTimeComponent()
    {
        // Arrange
        var baseDate = new DateTime(2024, 2, 15);
        var dateWithTime = new DateTime(2024, 2, 15, 14, 30, 45); // 2:30:45 PM

        var revision = new Revision(baseDate, "Test Revision");
        _repository.Insert(revision);

        // Act - Search with time component should still find the revision
        var result = _repository.GetRevisionsByDate(dateWithTime);

        // Assert
        Assert.That(result, Has.Count.EqualTo(1));
        Assert.That(result[0].Description, Is.EqualTo("Test Revision"));
    }

    [Test]
    public void GetRevisionsByDate_NoRevisionsOnDate_ReturnsEmptyList()
    {
        // Arrange
        var existingDate = new DateTime(2024, 2, 15);
        var searchDate = new DateTime(2024, 2, 16);

        var revision = new Revision(existingDate, "Test Revision");
        _repository.Insert(revision);

        // Act
        var result = _repository.GetRevisionsByDate(searchDate);

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    [Test]
    public void GetRevisionsByDate_DateAtMidnight_HandlesCorrectly()
    {
        // Arrange
        var midnightDate = new DateTime(2024, 2, 15, 0, 0, 0); // Exactly midnight
        var revision = new Revision(midnightDate, "Midnight Revision");
        _repository.Insert(revision);

        // Act
        var result = _repository.GetRevisionsByDate(midnightDate);

        // Assert
        Assert.That(result, Has.Count.EqualTo(1));
        Assert.That(result[0].Description, Is.EqualTo("Midnight Revision"));
    }

    #endregion

    #region Document Management Tests - AddDocumentToRevision

    [Test]
    public void AddDocumentToRevision_WithValidIds_AddsDocumentSuccessfully()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        _repository.Insert(revision);
        var documentId = 123;

        // Act
        var result = _repository.AddDocumentToRevision(revision.Id, documentId);

        // Assert
        Assert.That(result, Is.EqualTo(1));
        
        var updated = _repository.GetById(revision.Id);
        Assert.That(updated.DocumentIds, Contains.Item(documentId));
    }

    [Test]
    public void AddDocumentToRevision_DuplicateDocument_DoesNotAddAgain()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        _repository.Insert(revision);
        var documentId = 123;
        
        _repository.AddDocumentToRevision(revision.Id, documentId);

        // Act - Try to add same document again
        var result = _repository.AddDocumentToRevision(revision.Id, documentId);

        // Assert
        Assert.That(result, Is.EqualTo(0)); // No change
        
        var updated = _repository.GetById(revision.Id);
        Assert.That(updated.DocumentIds, Has.Count.EqualTo(1));
    }

    [Test]
    public void AddDocumentToRevision_NonExistentRevision_ReturnsZero()
    {
        // Act
        var result = _repository.AddDocumentToRevision(99999, 123);

        // Assert
        Assert.That(result, Is.EqualTo(0));
    }

    #endregion

    #region Document Management Tests - RemoveDocumentFromRevision

    [Test]
    public void RemoveDocumentFromRevision_ExistingDocument_RemovesSuccessfully()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        _repository.Insert(revision);
        var documentId = 123;
        
        _repository.AddDocumentToRevision(revision.Id, documentId);

        // Act
        var result = _repository.RemoveDocumentFromRevision(revision.Id, documentId);

        // Assert
        Assert.That(result, Is.EqualTo(1));
        
        var updated = _repository.GetById(revision.Id);
        Assert.That(updated.DocumentIds, Does.Not.Contain(documentId));
    }

    [Test]
    public void RemoveDocumentFromRevision_NonExistentDocument_ReturnsZero()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        _repository.Insert(revision);

        // Act - Try to remove document that was never added
        var result = _repository.RemoveDocumentFromRevision(revision.Id, 123);

        // Assert
        Assert.That(result, Is.EqualTo(0));
    }

    [Test]
    public void RemoveDocumentFromRevision_NonExistentRevision_ReturnsZero()
    {
        // Act
        var result = _repository.RemoveDocumentFromRevision(99999, 123);

        // Assert
        Assert.That(result, Is.EqualTo(0));
    }

    #endregion

    #region Document Management Tests - AddDocumentsToRevision

    [Test]
    public void AddDocumentsToRevision_WithMultipleDocuments_AddsAllSuccessfully()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        _repository.Insert(revision);
        var documentIds = new[] { 100, 101, 102 };

        // Act
        var result = _repository.AddDocumentsToRevision(revision.Id, documentIds);

        // Assert
        Assert.That(result, Is.EqualTo(1));
        
        var updated = _repository.GetById(revision.Id);
        Assert.That(updated.DocumentIds, Has.Count.EqualTo(3));
        Assert.That(updated.DocumentIds, Is.EquivalentTo(documentIds));
    }

    [Test]
    public void AddDocumentsToRevision_WithSomeDuplicates_OnlyAddsNew()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        _repository.Insert(revision);
        
        _repository.AddDocumentToRevision(revision.Id, 100);
        var newDocumentIds = new[] { 100, 101, 102 }; // 100 already exists

        // Act
        var result = _repository.AddDocumentsToRevision(revision.Id, newDocumentIds);

        // Assert
        Assert.That(result, Is.EqualTo(1));
        
        var updated = _repository.GetById(revision.Id);
        Assert.That(updated.DocumentIds, Has.Count.EqualTo(3));
        Assert.That(updated.DocumentIds, Is.EquivalentTo(new[] { 100, 101, 102 }));
    }

    [Test]
    public void AddDocumentsToRevision_AllDuplicates_ReturnsZero()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        _repository.Insert(revision);
        var documentIds = new[] { 100, 101 };
        
        _repository.AddDocumentsToRevision(revision.Id, documentIds);

        // Act - Try to add same documents again
        var result = _repository.AddDocumentsToRevision(revision.Id, documentIds);

        // Assert
        Assert.That(result, Is.EqualTo(0));
    }

    #endregion

    #region Document Management Tests - RemoveDocumentsFromRevision

    [Test]
    public void RemoveDocumentsFromRevision_WithMultipleDocuments_RemovesAllSuccessfully()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        _repository.Insert(revision);
        var documentIds = new[] { 100, 101, 102, 103 };
        
        _repository.AddDocumentsToRevision(revision.Id, documentIds);

        // Act - Remove some documents
        var toRemove = new[] { 101, 103 };
        var result = _repository.RemoveDocumentsFromRevision(revision.Id, toRemove);

        // Assert
        Assert.That(result, Is.EqualTo(1));
        
        var updated = _repository.GetById(revision.Id);
        Assert.That(updated.DocumentIds, Has.Count.EqualTo(2));
        Assert.That(updated.DocumentIds, Is.EquivalentTo(new[] { 100, 102 }));
    }

    [Test]
    public void RemoveDocumentsFromRevision_NonExistentDocuments_ReturnsZero()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        _repository.Insert(revision);
        
        _repository.AddDocumentToRevision(revision.Id, 100);

        // Act - Try to remove documents that don't exist
        var result = _repository.RemoveDocumentsFromRevision(revision.Id, new[] { 200, 300 });

        // Assert
        Assert.That(result, Is.EqualTo(0));
    }

    #endregion

    #region Document Management Tests - SetRevisionDocuments

    [Test]
    public void SetRevisionDocuments_ReplacesExistingDocuments()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        _repository.Insert(revision);
        
        _repository.AddDocumentsToRevision(revision.Id, new[] { 100, 101, 102 });

        // Act - Replace with new list
        var newDocuments = new[] { 200, 201 };
        var result = _repository.SetRevisionDocuments(revision.Id, newDocuments);

        // Assert
        Assert.That(result, Is.EqualTo(1));
        
        var updated = _repository.GetById(revision.Id);
        Assert.That(updated.DocumentIds, Has.Count.EqualTo(2));
        Assert.That(updated.DocumentIds, Is.EquivalentTo(newDocuments));
    }

    [Test]
    public void SetRevisionDocuments_WithDuplicates_RemovesDuplicates()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        _repository.Insert(revision);

        // Act - Set with duplicates
        var documentsWithDuplicates = new[] { 100, 101, 100, 102, 101 };
        var result = _repository.SetRevisionDocuments(revision.Id, documentsWithDuplicates);

        // Assert
        Assert.That(result, Is.EqualTo(1));
        
        var updated = _repository.GetById(revision.Id);
        Assert.That(updated.DocumentIds, Has.Count.EqualTo(3));
        Assert.That(updated.DocumentIds, Is.EquivalentTo(new[] { 100, 101, 102 }));
    }

    [Test]
    public void SetRevisionDocuments_NonExistentRevision_ReturnsZero()
    {
        // Act
        var result = _repository.SetRevisionDocuments(99999, new[] { 100, 101 });

        // Assert
        Assert.That(result, Is.EqualTo(0));
    }

    #endregion

    #region Document Management Tests - GetRevisionsByDocumentId

    [Test]
    public void GetRevisionsByDocumentId_FindsAllRevisionsContainingDocument()
    {
        // Arrange
        var revision1 = new Revision(new DateTime(2024, 1, 15), "Revision 1");
        var revision2 = new Revision(new DateTime(2024, 2, 15), "Revision 2");
        var revision3 = new Revision(new DateTime(2024, 3, 15), "Revision 3");
        
        _repository.Insert(revision1);
        _repository.Insert(revision2);
        _repository.Insert(revision3);
        
        var documentId = 123;
        _repository.AddDocumentToRevision(revision1.Id, documentId);
        _repository.AddDocumentToRevision(revision2.Id, documentId);
        _repository.AddDocumentToRevision(revision3.Id, 456); // Different document

        // Act
        var result = _repository.GetRevisionsByDocumentId(documentId);

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
        Assert.That(result.All(r => r.DocumentIds.Contains(documentId)), Is.True);
        
        // Should be ordered by date descending
        Assert.That(result[0].Description, Is.EqualTo("Revision 2"));
        Assert.That(result[1].Description, Is.EqualTo("Revision 1"));
    }

    [Test]
    public void GetRevisionsByDocumentId_NoMatchingRevisions_ReturnsEmptyList()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        _repository.Insert(revision);
        _repository.AddDocumentToRevision(revision.Id, 100);

        // Act
        var result = _repository.GetRevisionsByDocumentId(999);

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    #endregion

    #region Document Management Tests - Helper Methods

    [Test]
    public void GetDocumentCount_ReturnsCorrectCount()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        _repository.Insert(revision);
        
        _repository.AddDocumentsToRevision(revision.Id, new[] { 100, 101, 102 });

        // Act
        var result = _repository.GetDocumentCount(revision.Id);

        // Assert
        Assert.That(result, Is.EqualTo(3));
    }

    [Test]
    public void GetDocumentCount_EmptyRevision_ReturnsZero()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        _repository.Insert(revision);

        // Act
        var result = _repository.GetDocumentCount(revision.Id);

        // Assert
        Assert.That(result, Is.EqualTo(0));
    }

    [Test]
    public void GetDocumentCount_NonExistentRevision_ReturnsZero()
    {
        // Act
        var result = _repository.GetDocumentCount(99999);

        // Assert
        Assert.That(result, Is.EqualTo(0));
    }

    [Test]
    public void RevisionContainsDocument_DocumentExists_ReturnsTrue()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        _repository.Insert(revision);
        var documentId = 123;
        
        _repository.AddDocumentToRevision(revision.Id, documentId);

        // Act
        var result = _repository.RevisionContainsDocument(revision.Id, documentId);

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public void RevisionContainsDocument_DocumentDoesNotExist_ReturnsFalse()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        _repository.Insert(revision);

        // Act
        var result = _repository.RevisionContainsDocument(revision.Id, 123);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public void RevisionContainsDocument_NonExistentRevision_ReturnsFalse()
    {
        // Act
        var result = _repository.RevisionContainsDocument(99999, 123);

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public void GetEmptyRevisions_ReturnsOnlyRevisionsWithNoDocuments()
    {
        // Arrange
        var emptyRevision1 = new Revision(new DateTime(2024, 1, 15), "Empty 1");
        var emptyRevision2 = new Revision(new DateTime(2024, 2, 15), "Empty 2");
        var fullRevision = new Revision(new DateTime(2024, 3, 15), "Full");
        
        _repository.Insert(emptyRevision1);
        _repository.Insert(emptyRevision2);
        _repository.Insert(fullRevision);
        
        _repository.AddDocumentToRevision(fullRevision.Id, 123);

        // Act
        var result = _repository.GetEmptyRevisions();

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
        Assert.That(result.All(r => r.DocumentIds.Count == 0), Is.True);
    }

    [Test]
    public void GetRevisionStatistics_ReturnsCorrectStatistics()
    {
        // Arrange
        var revision1 = new Revision(new DateTime(2024, 1, 15), "Revision 1");
        var revision2 = new Revision(new DateTime(2024, 2, 15), "Revision 2");
        var revision3 = new Revision(new DateTime(2024, 3, 15), "Revision 3");
        
        _repository.Insert(revision1);
        _repository.Insert(revision2);
        _repository.Insert(revision3);
        
        _repository.AddDocumentsToRevision(revision1.Id, new[] { 100, 101 }); // 2 documents
        _repository.AddDocumentsToRevision(revision2.Id, new[] { 200, 201, 202 }); // 3 documents
        // revision3 has no documents

        // Act
        var result = _repository.GetRevisionStatistics();

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

    #region Inherited BaseRepositorySync Method Tests

    [Test]
    public void InheritedMethods_WorkCorrectly()
    {
        // Test that inherited methods from BaseRepositorySync work correctly

        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");

        // Act & Assert - Insert
        var insertResult = _repository.Insert(revision);
        Assert.That(insertResult, Is.EqualTo(1));
        Assert.That(revision.Id, Is.GreaterThan(0));

        // Act & Assert - GetById
        var retrieved = _repository.GetById(revision.Id);
        Assert.That(retrieved, Is.Not.Null);
        Assert.That(retrieved.Description, Is.EqualTo("Test Revision"));

        // Act & Assert - Update
        retrieved.Description = "Updated Description";
        var updateResult = _repository.Update(retrieved);
        Assert.That(updateResult, Is.EqualTo(1));

        // Act & Assert - Find
        var found = _repository.Find(r => r.Description.Contains("Updated"));
        Assert.That(found, Has.Count.EqualTo(1));

        // Act & Assert - Count
        var count = _repository.Count();
        Assert.That(count, Is.EqualTo(1));

        // Act & Assert - Delete
        var deleteResult = _repository.Delete(revision.Id);
        Assert.That(deleteResult, Is.EqualTo(1));
    }

    #endregion

    #region Integration Tests

    [Test]
    public void IntegrationTest_CompleteRevisionLifecycle()
    {
        // Create revision
        var revision = new Revision(new DateTime(2024, 2, 15), "Initial Revision");
        _repository.Insert(revision);

        // Add documents
        var documentIds = new[] { 100, 101, 102 };
        _repository.AddDocumentsToRevision(revision.Id, documentIds);

        // Verify documents added
        Assert.That(_repository.GetDocumentCount(revision.Id), Is.EqualTo(3));

        // Remove one document
        _repository.RemoveDocumentFromRevision(revision.Id, 101);
        Assert.That(_repository.GetDocumentCount(revision.Id), Is.EqualTo(2));

        // Check if contains specific document
        Assert.That(_repository.RevisionContainsDocument(revision.Id, 100), Is.True);
        Assert.That(_repository.RevisionContainsDocument(revision.Id, 101), Is.False);

        // Replace all documents
        _repository.SetRevisionDocuments(revision.Id, new[] { 200, 201, 202, 203 });
        Assert.That(_repository.GetDocumentCount(revision.Id), Is.EqualTo(4));

        // Verify in revisions by document ID
        var revisionsContaining200 = _repository.GetRevisionsByDocumentId(200);
        Assert.That(revisionsContaining200, Has.Count.EqualTo(1));

        // Get statistics
        var stats = _repository.GetRevisionStatistics();
        Assert.That(stats["TotalRevisions"], Is.EqualTo(1));
        Assert.That(stats["RevisionsWithDocuments"], Is.EqualTo(1));
    }

    #endregion
}
