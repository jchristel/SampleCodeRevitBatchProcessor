using NUnit.Framework;
using SQLite;
using duHastNet.DocManager.Core.Services.Repositories;
using duHastNet.DocManager.Core.Models;
using System.IO;

namespace duHastNet.DocManager.Core.Tests.Services.Repositories;

[TestFixture]
public class DocumentRepositoryTests
{
    private SQLiteAsyncConnection _connection;
    private string _databasePath;
    private DocumentRepository _documentRepository;
    private RevisionRepository _revisionRepository;
    private int _testRevisionId;

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
        await _connection.CreateTableAsync<Document>();

        _documentRepository = new DocumentRepository(_connection);
        _revisionRepository = new RevisionRepository(_connection);

        // Create a test revision for documents to reference
        var testRevision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        await _revisionRepository.InsertAsync(testRevision);
        _testRevisionId = testRevision.Id;
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
    public async Task GetDocumentsByRevisionAsync_WithDocumentsInRevision_ReturnsDocumentsOrderedByNumber()
    {
        // Arrange
        var documents = new[]
        {
            new Document("S-201", "Structural Plan", "2", _testRevisionId),
            new Document("A-101", "Architectural Plan", "1", _testRevisionId),
            new Document("M-301", "Mechanical Plan", "1", _testRevisionId)
        };

        foreach (var document in documents)
        {
            await _documentRepository.InsertAsync(document);
        }

        // Act
        var result = await _documentRepository.GetDocumentsByRevisionAsync(_testRevisionId);

        // Assert
        Assert.That(result, Has.Count.EqualTo(3));
        // Should be ordered by Number
        Assert.That(result[0].Number, Is.EqualTo("A-101"));
        Assert.That(result[1].Number, Is.EqualTo("M-301"));
        Assert.That(result[2].Number, Is.EqualTo("S-201"));
    }

    [Test]
    public async Task GetDocumentsByRevisionAsync_NoDocumentsInRevision_ReturnsEmptyList()
    {
        // Arrange - Create a second revision with no documents
        var emptyRevision = new Revision(new DateTime(2024, 3, 1), "Empty Revision");
        await _revisionRepository.InsertAsync(emptyRevision);

        // Act
        var result = await _documentRepository.GetDocumentsByRevisionAsync(emptyRevision.Id);

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    [Test]
    public async Task GetDocumentsByNumberAsync_WithMultipleRevisions_ReturnsAllRevisionsOrderedByIdDescending()
    {
        // Arrange
        var secondRevision = new Revision(new DateTime(2024, 3, 1), "Second Revision");
        await _revisionRepository.InsertAsync(secondRevision);

        var documents = new[]
        {
            new Document("A-101", "Floor Plan Rev 1", "1", _testRevisionId),
            new Document("A-101", "Floor Plan Rev 2", "2", secondRevision.Id),
            new Document("A-101", "Floor Plan Rev 3", "3", secondRevision.Id)
        };

        foreach (var document in documents)
        {
            await _documentRepository.InsertAsync(document);
        }

        // Act
        var result = await _documentRepository.GetDocumentsByNumberAsync("A-101");

        // Assert
        Assert.That(result, Has.Count.EqualTo(3));
        // Should be ordered by Id descending (most recent first)
        Assert.That(result[0].Revision, Is.EqualTo("3"));
        Assert.That(result[1].Revision, Is.EqualTo("2"));
        Assert.That(result[2].Revision, Is.EqualTo("1"));
    }

    [Test]
    public async Task GetDocumentsByNumberAsync_NonExistentNumber_ReturnsEmptyList()
    {
        // Arrange
        var document = new Document("A-101", "Floor Plan", "1", _testRevisionId);
        await _documentRepository.InsertAsync(document);

        // Act
        var result = await _documentRepository.GetDocumentsByNumberAsync("B-999");

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    [Test]
    public async Task GetLatestDocumentRevisionAsync_WithMultipleRevisions_ReturnsLatestRevision()
    {
        // Arrange
        var secondRevision = new Revision(new DateTime(2024, 3, 1), "Second Revision");
        await _revisionRepository.InsertAsync(secondRevision);

        var documents = new[]
        {
            new Document("A-101", "Floor Plan Rev 1", "1", _testRevisionId),
            new Document("A-101", "Floor Plan Rev 2", "2", secondRevision.Id),
            new Document("A-101", "Floor Plan Rev 3", "3", secondRevision.Id)
        };

        foreach (var document in documents)
        {
            await _documentRepository.InsertAsync(document);
        }

        // Act
        var result = await _documentRepository.GetLatestDocumentRevisionAsync("A-101");

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result.Revision, Is.EqualTo("3"));
        Assert.That(result.Name, Is.EqualTo("Floor Plan Rev 3"));
    }

    [Test]
    public async Task GetLatestDocumentRevisionAsync_NonExistentDocument_ReturnsNull()
    {
        // Act
        var result = await _documentRepository.GetLatestDocumentRevisionAsync("NonExistent");

        // Assert
        Assert.That(result, Is.Null);
    }

    [Test]
    public async Task GetDistinctDocumentNumbersAsync_WithMultipleDocuments_ReturnsUniqueNumbersOrderedAlphabetically()
    {
        // Arrange
        var documents = new[]
        {
            new Document("S-201", "Structural Plan", "1", _testRevisionId),
            new Document("A-101", "Architectural Plan Rev 1", "1", _testRevisionId),
            new Document("A-101", "Architectural Plan Rev 2", "2", _testRevisionId), // Duplicate number
            new Document("M-301", "Mechanical Plan", "1", _testRevisionId),
            new Document("A-102", "Ceiling Plan", "1", _testRevisionId)
        };

        foreach (var document in documents)
        {
            await _documentRepository.InsertAsync(document);
        }

        // Act
        var result = await _documentRepository.GetDistinctDocumentNumbersAsync();

        // Assert
        Assert.That(result, Has.Count.EqualTo(4)); // Should be unique
        Assert.That(result, Is.EqualTo(new[] { "A-101", "A-102", "M-301", "S-201" })); // Alphabetically ordered
    }

    [Test]
    public async Task GetDistinctDocumentNumbersAsync_NoDocuments_ReturnsEmptyList()
    {
        // Act
        var result = await _documentRepository.GetDistinctDocumentNumbersAsync();

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    [Test]
    public async Task SearchDocumentsAsync_SearchByNumber_ReturnsMatchingDocuments()
    {
        // Arrange
        var documents = new[]
        {
            new Document("A-101", "Architectural Floor Plan", "1", _testRevisionId),
            new Document("A-102", "Architectural Ceiling Plan", "1", _testRevisionId),
            new Document("S-201", "Structural Plan", "1", _testRevisionId)
        };

        foreach (var document in documents)
        {
            await _documentRepository.InsertAsync(document);
        }

        // Act
        var result = await _documentRepository.SearchDocumentsAsync("A-1");

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
        Assert.That(result.All(d => d.Number.Contains("A-1")), Is.True);
    }

    [Test]
    public async Task SearchDocumentsAsync_SearchByName_ReturnsMatchingDocuments()
    {
        // Arrange
        var documents = new[]
        {
            new Document("A-101", "Floor Plan - Level 1", "1", _testRevisionId),
            new Document("A-102", "Floor Plan - Level 2", "1", _testRevisionId),
            new Document("S-201", "Structural Foundation Plan", "1", _testRevisionId)
        };

        foreach (var document in documents)
        {
            await _documentRepository.InsertAsync(document);
        }

        // Act
        var result = await _documentRepository.SearchDocumentsAsync("floor");

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
        Assert.That(result.All(d => d.Name.ToLower().Contains("floor")), Is.True);
    }

    [Test]
    public async Task SearchDocumentsAsync_SearchByRevision_ReturnsMatchingDocuments()
    {
        // Arrange
        var documents = new[]
        {
            new Document("A-101", "Floor Plan", "2B", _testRevisionId),
            new Document("A-102", "Ceiling Plan", "1", _testRevisionId),
            new Document("S-201", "Structural Plan", "2B", _testRevisionId)
        };

        foreach (var document in documents)
        {
            await _documentRepository.InsertAsync(document);
        }

        // Act
        var result = await _documentRepository.SearchDocumentsAsync("2B");

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
        Assert.That(result.All(d => d.Revision.Contains("2B")), Is.True);
    }

    [Test]
    public async Task SearchDocumentsAsync_CaseInsensitiveSearch_ReturnsMatchingDocuments()
    {
        // Arrange
        var document = new Document("A-101", "FLOOR PLAN", "1", _testRevisionId);
        await _documentRepository.InsertAsync(document);

        // Act
        var result = await _documentRepository.SearchDocumentsAsync("floor");

        // Assert
        Assert.That(result, Has.Count.EqualTo(1));
        Assert.That(result[0].Name, Is.EqualTo("FLOOR PLAN"));
    }

    [Test]
    public async Task SearchDocumentsAsync_NoMatches_ReturnsEmptyList()
    {
        // Arrange
        var document = new Document("A-101", "Floor Plan", "1", _testRevisionId);
        await _documentRepository.InsertAsync(document);

        // Act
        var result = await _documentRepository.SearchDocumentsAsync("xyz");

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    [Test]
    public async Task SearchDocumentsAsync_OrdersByNumberThenByIdDescending()
    {
        // Arrange
        var secondRevision = new Revision(new DateTime(2024, 3, 1), "Second Revision");
        await _revisionRepository.InsertAsync(secondRevision);

        // Insert documents in a specific order to ensure predictable IDs
        // Insert the older revisions first, then the newer revisions
        var document1 = new Document("A-101", "Plan A Rev 1", "1", _testRevisionId);
        await _documentRepository.InsertAsync(document1);

        var document2 = new Document("B-101", "Plan B Rev 1", "1", _testRevisionId);
        await _documentRepository.InsertAsync(document2);

        var document3 = new Document("A-101", "Plan A Rev 2", "2", secondRevision.Id);
        await _documentRepository.InsertAsync(document3);

        var document4 = new Document("B-101", "Plan B Rev 2", "2", secondRevision.Id);
        await _documentRepository.InsertAsync(document4);

        // Act
        var result = await _documentRepository.SearchDocumentsAsync("Plan");

        // Assert
        Assert.That(result, Has.Count.EqualTo(4));

        // Should be ordered by Number first, then by Id descending (newest first for same number)
        // Since we inserted in chronological order, higher IDs should represent newer revisions

        // Group by Number to verify ordering
        var aDocuments = result.Where(d => d.Number == "A-101").ToList();
        var bDocuments = result.Where(d => d.Number == "B-101").ToList();

        Assert.That(aDocuments, Has.Count.EqualTo(2));
        Assert.That(bDocuments, Has.Count.EqualTo(2));

        // Within each number group, documents should be ordered by ID descending
        Assert.That(aDocuments[0].Id, Is.GreaterThan(aDocuments[1].Id), "First A-101 document should have higher ID");
        Assert.That(bDocuments[0].Id, Is.GreaterThan(bDocuments[1].Id), "First B-101 document should have higher ID");

        // Verify the overall ordering: A-101 documents first, then B-101 documents
        Assert.That(result[0].Number, Is.EqualTo("A-101"));
        Assert.That(result[1].Number, Is.EqualTo("A-101"));
        Assert.That(result[2].Number, Is.EqualTo("B-101"));
        Assert.That(result[3].Number, Is.EqualTo("B-101"));

        // Verify that within each number group, higher ID (newer) comes first
        Assert.That(result[0].Id, Is.EqualTo(document3.Id), "First A-101 should be Rev 2 (higher ID)");
        Assert.That(result[1].Id, Is.EqualTo(document1.Id), "Second A-101 should be Rev 1 (lower ID)");
        Assert.That(result[2].Id, Is.EqualTo(document4.Id), "First B-101 should be Rev 2 (higher ID)");
        Assert.That(result[3].Id, Is.EqualTo(document2.Id), "Second B-101 should be Rev 1 (lower ID)");
    }

    [Test]
    public async Task DocumentExistsAsync_ExistingDocument_ReturnsTrue()
    {
        // Arrange
        var document = new Document("A-101", "Floor Plan", "2", _testRevisionId);
        await _documentRepository.InsertAsync(document);

        // Act
        var result = await _documentRepository.DocumentExistsAsync("A-101", "2");

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public async Task DocumentExistsAsync_NonExistentDocument_ReturnsFalse()
    {
        // Arrange
        var document = new Document("A-101", "Floor Plan", "1", _testRevisionId);
        await _documentRepository.InsertAsync(document);

        // Act
        var result = await _documentRepository.DocumentExistsAsync("A-101", "2");

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public async Task DocumentExistsAsync_ExistingNumberDifferentRevision_ReturnsFalse()
    {
        // Arrange
        var document = new Document("A-101", "Floor Plan", "1", _testRevisionId);
        await _documentRepository.InsertAsync(document);

        // Act
        var result = await _documentRepository.DocumentExistsAsync("A-101", "3");

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public async Task DocumentExistsAsync_DifferentNumberSameRevision_ReturnsFalse()
    {
        // Arrange
        var document = new Document("A-101", "Floor Plan", "1", _testRevisionId);
        await _documentRepository.InsertAsync(document);

        // Act
        var result = await _documentRepository.DocumentExistsAsync("A-102", "1");

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public async Task InheritedMethods_WorkCorrectly()
    {
        // Test that inherited methods from BaseRepository work correctly

        // Arrange
        var document = new Document("A-101", "Floor Plan", "1", _testRevisionId);

        // Act & Assert - Insert
        var insertResult = await _documentRepository.InsertAsync(document);
        Assert.That(insertResult, Is.EqualTo(1));
        Assert.That(document.Id, Is.GreaterThan(0));

        // Act & Assert - GetById
        var retrieved = await _documentRepository.GetByIdAsync(document.Id);
        Assert.That(retrieved, Is.Not.Null);
        Assert.That(retrieved.Number, Is.EqualTo("A-101"));

        // Act & Assert - Update
        retrieved.Name = "Updated Floor Plan";
        var updateResult = await _documentRepository.UpdateAsync(retrieved);
        Assert.That(updateResult, Is.EqualTo(1));

        // Act & Assert - Find
        var found = await _documentRepository.FindAsync(d => d.Name.Contains("Updated"));
        Assert.That(found, Has.Count.EqualTo(1));

        // Act & Assert - Count
        var count = await _documentRepository.CountAsync();
        Assert.That(count, Is.EqualTo(1));

        // Act & Assert - Delete
        var deleteResult = await _documentRepository.DeleteAsync(document.Id);
        Assert.That(deleteResult, Is.EqualTo(1));
    }

    [Test]
    public async Task GetDocumentsByRevisionAsync_WithDocumentsFromDifferentRevisions_OnlyReturnsCorrectRevision()
    {
        // Arrange
        var secondRevision = new Revision(new DateTime(2024, 3, 1), "Second Revision");
        await _revisionRepository.InsertAsync(secondRevision);

        var documents = new[]
        {
            new Document("A-101", "Plan from Revision 1", "1", _testRevisionId),
            new Document("A-102", "Plan from Revision 1", "1", _testRevisionId),
            new Document("B-101", "Plan from Revision 2", "1", secondRevision.Id)
        };

        foreach (var document in documents)
        {
            await _documentRepository.InsertAsync(document);
        }

        // Act
        var result = await _documentRepository.GetDocumentsByRevisionAsync(_testRevisionId);

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
        Assert.That(result.All(d => d.RevisionId == _testRevisionId), Is.True);
        Assert.That(result.All(d => d.Name.Contains("Revision 1")), Is.True);
    }
}