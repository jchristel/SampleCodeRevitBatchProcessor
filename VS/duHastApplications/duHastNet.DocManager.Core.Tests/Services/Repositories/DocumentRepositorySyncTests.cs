using NUnit.Framework;
using SQLite;
using duHastNet.DocManager.Core.Services.Repositories;
using duHastNet.DocManager.Core.Models;
using System.IO;

namespace duHastNet.DocManager.Core.Tests.Services.Repositories;

[TestFixture]
public class DocumentRepositorySyncTests
{
    private SQLiteConnection _connection;
    private string _databasePath;
    private DocumentRepositorySync _documentRepository;
    private RevisionRepositorySync _revisionRepository;
    private int _testRevisionId;

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
        _connection.CreateTable<Document>();

        _documentRepository = new DocumentRepositorySync(_connection);
        _revisionRepository = new RevisionRepositorySync(_connection);

        // Create a test revision for documents to reference
        var testRevision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        _revisionRepository.Insert(testRevision);
        _testRevisionId = testRevision.Id;
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

    #region GetDocumentsByRevision Tests

    [Test]
    public void GetDocumentsByRevision_WithDocumentsInRevision_ReturnsDocumentsOrderedByNumber()
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
            _documentRepository.Insert(document);
        }

        // Act
        var result = _documentRepository.GetDocumentsByRevision(_testRevisionId);

        // Assert
        Assert.That(result, Has.Count.EqualTo(3));
        // Should be ordered by Number
        Assert.That(result[0].Number, Is.EqualTo("A-101"));
        Assert.That(result[1].Number, Is.EqualTo("M-301"));
        Assert.That(result[2].Number, Is.EqualTo("S-201"));
    }

    [Test]
    public void GetDocumentsByRevision_NoDocumentsInRevision_ReturnsEmptyList()
    {
        // Arrange - Create a second revision with no documents
        var emptyRevision = new Revision(new DateTime(2024, 3, 1), "Empty Revision");
        _revisionRepository.Insert(emptyRevision);

        // Act
        var result = _documentRepository.GetDocumentsByRevision(emptyRevision.Id);

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    [Test]
    public void GetDocumentsByRevision_OnlyReturnsActiveDocuments()
    {
        // Arrange
        var activeDoc = new Document("A-101", "Active Plan", "1", _testRevisionId);
        var inactiveDoc = new Document("A-102", "Inactive Plan", "1", _testRevisionId);
        
        _documentRepository.Insert(activeDoc);
        _documentRepository.Insert(inactiveDoc);
        
        // Make one inactive
        _documentRepository.UpdateActiveStatus(inactiveDoc.Id, false);

        // Act
        var result = _documentRepository.GetDocumentsByRevision(_testRevisionId);

        // Assert
        Assert.That(result, Has.Count.EqualTo(1));
        Assert.That(result[0].Number, Is.EqualTo("A-101"));
    }

    #endregion

    #region GetDocumentsByNumber Tests

    [Test]
    public void GetDocumentsByNumber_WithMultipleRevisions_ReturnsAllRevisionsOrderedByNewest()
    {
        // Arrange
        var doc1 = new Document("A-101", "Floor Plan", "1", _testRevisionId);
        _documentRepository.Insert(doc1);

        // Create second revision
        var revision2 = new Revision(new DateTime(2024, 3, 1), "Revision 2");
        _revisionRepository.Insert(revision2);
        var doc2 = new Document("A-101", "Floor Plan", "2", revision2.Id);
        _documentRepository.Insert(doc2);

        // Act
        var result = _documentRepository.GetDocumentsByNumber("A-101");

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
        Assert.That(result[0].Revision, Is.EqualTo("2")); // Most recent first
        Assert.That(result[1].Revision, Is.EqualTo("1"));
    }

    [Test]
    public void GetDocumentsByNumber_NoMatchingDocuments_ReturnsEmptyList()
    {
        // Arrange
        var doc = new Document("A-101", "Floor Plan", "1", _testRevisionId);
        _documentRepository.Insert(doc);

        // Act
        var result = _documentRepository.GetDocumentsByNumber("B-202");

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    [Test]
    public void GetDocumentsByNumber_OnlyReturnsActiveDocuments()
    {
        // Arrange
        var activeDoc = new Document("A-101", "Plan Rev 1", "1", _testRevisionId);
        var inactiveDoc = new Document("A-101", "Plan Rev 2", "2", _testRevisionId);
        
        _documentRepository.Insert(activeDoc);
        _documentRepository.Insert(inactiveDoc);
        
        _documentRepository.UpdateActiveStatus(inactiveDoc.Id, false);

        // Act
        var result = _documentRepository.GetDocumentsByNumber("A-101");

        // Assert
        Assert.That(result, Has.Count.EqualTo(1));
        Assert.That(result[0].Revision, Is.EqualTo("1"));
    }

    #endregion

    #region GetLatestDocumentRevision Tests

    [Test]
    public void GetLatestDocumentRevision_WithMultipleRevisions_ReturnsNewest()
    {
        // Arrange
        var doc1 = new Document("A-101", "Floor Plan", "1", _testRevisionId);
        _documentRepository.Insert(doc1);

        var revision2 = new Revision(new DateTime(2024, 3, 1), "Revision 2");
        _revisionRepository.Insert(revision2);
        var doc2 = new Document("A-101", "Floor Plan Updated", "2", revision2.Id);
        _documentRepository.Insert(doc2);

        // Act
        var result = _documentRepository.GetLatestDocumentRevision("A-101");

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Is.Not.Null);
            Assert.That(result.Revision, Is.EqualTo("2"));
            Assert.That(result.Name, Is.EqualTo("Floor Plan Updated"));
        });
    }

    [Test]
    public void GetLatestDocumentRevision_NoMatchingDocuments_ReturnsNull()
    {
        // Arrange
        var doc = new Document("A-101", "Floor Plan", "1", _testRevisionId);
        _documentRepository.Insert(doc);

        // Act
        var result = _documentRepository.GetLatestDocumentRevision("B-202");

        // Assert
        Assert.That(result, Is.Null);
    }

    [Test]
    public void GetLatestDocumentRevision_OnlyReturnsActiveDocument()
    {
        // Arrange
        var oldDoc = new Document("A-101", "Old Version", "1", _testRevisionId);
        var newDoc = new Document("A-101", "New Version", "2", _testRevisionId);
        
        _documentRepository.Insert(oldDoc);
        _documentRepository.Insert(newDoc);
        
        // Make the newer one inactive
        _documentRepository.UpdateActiveStatus(newDoc.Id, false);

        // Act
        var result = _documentRepository.GetLatestDocumentRevision("A-101");

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Is.Not.Null);
            Assert.That(result.Revision, Is.EqualTo("1")); // Should return older active one
        });
    }

    #endregion

    #region GetDistinctDocumentNumbers Tests

    [Test]
    public void GetDistinctDocumentNumbers_WithMultipleDocuments_ReturnsUniqueNumbersOrdered()
    {
        // Arrange
        var documents = new[]
        {
            new Document("S-201", "Structural", "1", _testRevisionId),
            new Document("A-101", "Architectural", "1", _testRevisionId),
            new Document("A-101", "Architectural", "2", _testRevisionId),
            new Document("M-301", "Mechanical", "1", _testRevisionId)
        };

        foreach (var doc in documents)
        {
            _documentRepository.Insert(doc);
        }

        // Act
        var result = _documentRepository.GetDistinctDocumentNumbers();

        // Assert
        Assert.That(result, Has.Count.EqualTo(3));
        Assert.That(result, Is.EqualTo(new[] { "A-101", "M-301", "S-201" })); // Ordered
    }

    [Test]
    public void GetDistinctDocumentNumbers_NoDocuments_ReturnsEmptyList()
    {
        // Act
        var result = _documentRepository.GetDistinctDocumentNumbers();

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    [Test]
    public void GetDistinctDocumentNumbers_OnlyReturnsActiveDocuments()
    {
        // Arrange
        var activeDoc1 = new Document("A-101", "Active 1", "1", _testRevisionId);
        var activeDoc2 = new Document("A-102", "Active 2", "1", _testRevisionId);
        var inactiveDoc = new Document("A-103", "Inactive", "1", _testRevisionId);
        
        _documentRepository.Insert(activeDoc1);
        _documentRepository.Insert(activeDoc2);
        _documentRepository.Insert(inactiveDoc);
        
        _documentRepository.UpdateActiveStatus(inactiveDoc.Id, false);

        // Act
        var result = _documentRepository.GetDistinctDocumentNumbers();

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
        Assert.That(result, Does.Not.Contain("A-103"));
    }

    #endregion

    #region SearchDocuments Tests

    [Test]
    public void SearchDocuments_ByNumber_ReturnsMatchingDocuments()
    {
        // Arrange
        var documents = new[]
        {
            new Document("A-101", "Floor Plan", "1", _testRevisionId),
            new Document("A-102", "Ceiling Plan", "1", _testRevisionId),
            new Document("S-201", "Structural", "1", _testRevisionId)
        };

        foreach (var doc in documents)
        {
            _documentRepository.Insert(doc);
        }

        // Act
        var result = _documentRepository.SearchDocuments("A-10");

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
        Assert.That(result.All(d => d.Number.StartsWith("A-10")), Is.True);
    }

    [Test]
    public void SearchDocuments_ByName_ReturnsMatchingDocuments()
    {
        // Arrange
        var documents = new[]
        {
            new Document("A-101", "Floor Plan", "1", _testRevisionId),
            new Document("A-102", "Ceiling Plan", "1", _testRevisionId),
            new Document("S-201", "Structural Plan", "1", _testRevisionId)
        };

        foreach (var doc in documents)
        {
            _documentRepository.Insert(doc);
        }

        // Act
        var result = _documentRepository.SearchDocuments("plan");

        // Assert
        Assert.That(result, Has.Count.EqualTo(3));
    }

    [Test]
    public void SearchDocuments_IsCaseInsensitive()
    {
        // Arrange
        var doc = new Document("A-101", "Floor Plan", "1", _testRevisionId);
        _documentRepository.Insert(doc);

        // Act
        var result1 = _documentRepository.SearchDocuments("FLOOR");
        var result2 = _documentRepository.SearchDocuments("floor");
        var result3 = _documentRepository.SearchDocuments("FlOoR");

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result1, Has.Count.EqualTo(1));
            Assert.That(result2, Has.Count.EqualTo(1));
            Assert.That(result3, Has.Count.EqualTo(1));
        });
    }

    [Test]
    public void SearchDocuments_OnlyReturnsActiveDocuments()
    {
        // Arrange
        var activeDoc = new Document("A-101", "Active Floor Plan", "1", _testRevisionId);
        var inactiveDoc = new Document("A-102", "Inactive Floor Plan", "1", _testRevisionId);
        
        _documentRepository.Insert(activeDoc);
        _documentRepository.Insert(inactiveDoc);
        
        _documentRepository.UpdateActiveStatus(inactiveDoc.Id, false);

        // Act
        var result = _documentRepository.SearchDocuments("Floor");

        // Assert
        Assert.That(result, Has.Count.EqualTo(1));
        Assert.That(result[0].Number, Is.EqualTo("A-101"));
    }

    #endregion
    #region DocumentExists Tests

    [Test]
    public void DocumentExists_WithExistingDocument_ReturnsTrue()
    {
        // Arrange
        var doc = new Document("A-101", "Floor Plan", "1", _testRevisionId);
        _documentRepository.Insert(doc);

        // Act
        var result = _documentRepository.DocumentExists("A-101", "1");

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public void DocumentExists_WithNonExistentDocument_ReturnsFalse()
    {
        // Arrange
        var doc = new Document("A-101", "Floor Plan", "1", _testRevisionId);
        _documentRepository.Insert(doc);

        // Act
        var result = _documentRepository.DocumentExists("A-102", "1");

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public void DocumentExists_OnlyChecksActiveDocuments()
    {
        // Arrange
        var doc = new Document("A-101", "Floor Plan", "1", _testRevisionId);
        _documentRepository.Insert(doc);
        _documentRepository.UpdateActiveStatus(doc.Id, false);

        // Act
        var result = _documentRepository.DocumentExists("A-101", "1");

        // Assert
        Assert.That(result, Is.False); // Should not find inactive document
    }

    #endregion

    #region GetActiveDocuments Tests

    [Test]
    public void GetActiveDocuments_ReturnsOnlyActiveDocuments()
    {
        // Arrange
        var active1 = new Document("A-101", "Active 1", "1", _testRevisionId);
        var active2 = new Document("A-102", "Active 2", "1", _testRevisionId);
        var inactive = new Document("A-103", "Inactive", "1", _testRevisionId);
        
        _documentRepository.Insert(active1);
        _documentRepository.Insert(active2);
        _documentRepository.Insert(inactive);
        
        _documentRepository.UpdateActiveStatus(inactive.Id, false);

        // Act
        var result = _documentRepository.GetActiveDocuments();

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
        Assert.That(result.All(d => d.IsActive), Is.True);
    }

    [Test]
    public void GetActiveDocuments_OrderedByNumber()
    {
        // Arrange
        var documents = new[]
        {
            new Document("S-201", "Structural", "1", _testRevisionId),
            new Document("A-101", "Architectural", "1", _testRevisionId),
            new Document("M-301", "Mechanical", "1", _testRevisionId)
        };

        foreach (var doc in documents)
        {
            _documentRepository.Insert(doc);
        }

        // Act
        var result = _documentRepository.GetActiveDocuments();

        // Assert
        Assert.That(result[0].Number, Is.EqualTo("A-101"));
        Assert.That(result[1].Number, Is.EqualTo("M-301"));
        Assert.That(result[2].Number, Is.EqualTo("S-201"));
    }

    #endregion

    #region GetInactiveDocuments Tests

    [Test]
    public void GetInactiveDocuments_ReturnsOnlyInactiveDocuments()
    {
        // Arrange
        var active = new Document("A-101", "Active", "1", _testRevisionId);
        var inactive1 = new Document("A-102", "Inactive 1", "1", _testRevisionId);
        var inactive2 = new Document("A-103", "Inactive 2", "1", _testRevisionId);
        
        _documentRepository.Insert(active);
        _documentRepository.Insert(inactive1);
        _documentRepository.Insert(inactive2);
        
        _documentRepository.UpdateActiveStatus(inactive1.Id, false);
        _documentRepository.UpdateActiveStatus(inactive2.Id, false);

        // Act
        var result = _documentRepository.GetInactiveDocuments();

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
        Assert.That(result.All(d => !d.IsActive), Is.True);
    }

    [Test]
    public void GetInactiveDocuments_OrderedByNumber()
    {
        // Arrange
        var documents = new[]
        {
            new Document("S-201", "Structural", "1", _testRevisionId),
            new Document("A-101", "Architectural", "1", _testRevisionId),
            new Document("M-301", "Mechanical", "1", _testRevisionId)
        };

        foreach (var doc in documents)
        {
            _documentRepository.Insert(doc);
            _documentRepository.UpdateActiveStatus(doc.Id, false);
        }

        // Act
        var result = _documentRepository.GetInactiveDocuments();

        // Assert
        Assert.That(result[0].Number, Is.EqualTo("A-101"));
        Assert.That(result[1].Number, Is.EqualTo("M-301"));
        Assert.That(result[2].Number, Is.EqualTo("S-201"));
    }

    #endregion

    #region UpdateActiveStatus Tests

    [Test]
    public void UpdateActiveStatus_TogglesStatus()
    {
        // Arrange
        var doc = new Document("A-101", "Floor Plan", "1", _testRevisionId);
        _documentRepository.Insert(doc);

        // Act - Set to inactive
        var result1 = _documentRepository.UpdateActiveStatus(doc.Id, false);
        var afterInactive = _documentRepository.GetById(doc.Id);

        // Act - Set back to active
        var result2 = _documentRepository.UpdateActiveStatus(doc.Id, true);
        var afterActive = _documentRepository.GetById(doc.Id);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result1, Is.EqualTo(1));
            Assert.That(afterInactive.IsActive, Is.False);
            Assert.That(result2, Is.EqualTo(1));
            Assert.That(afterActive.IsActive, Is.True);
        });
    }

    [Test]
    public void UpdateActiveStatus_WithNonExistentId_ReturnsZero()
    {
        // Act
        var result = _documentRepository.UpdateActiveStatus(99999, false);

        // Assert
        Assert.That(result, Is.EqualTo(0));
    }

    #endregion

    #region GetDocumentsByHistoryNumber Tests

    [Test]
    public void GetDocumentsByHistoryNumber_FindsDocumentWithNumberInHistory()
    {
        // Arrange
        var doc = new Document("A-101-NEW", "Floor Plan", "1", _testRevisionId);
        doc.AddToHistory("A-101-OLD");
        _documentRepository.Insert(doc);

        // Act
        var result = _documentRepository.GetDocumentsByHistoryNumber("A-101-OLD");

        // Assert
        Assert.That(result, Has.Count.EqualTo(1));
        Assert.That(result[0].Number, Is.EqualTo("A-101-NEW"));
    }

    [Test]
    public void GetDocumentsByHistoryNumber_NoMatchingHistory_ReturnsEmptyList()
    {
        // Arrange
        var doc = new Document("A-101", "Floor Plan", "1", _testRevisionId);
        _documentRepository.Insert(doc);

        // Act
        var result = _documentRepository.GetDocumentsByHistoryNumber("A-999");

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    #endregion

    #region DocumentNumberExistsAnywhere Tests

    [Test]
    public void DocumentNumberExistsAnywhere_InCurrentNumber_ReturnsTrue()
    {
        // Arrange
        var doc = new Document("A-101", "Floor Plan", "1", _testRevisionId);
        _documentRepository.Insert(doc);

        // Act
        var result = _documentRepository.DocumentNumberExistsAnywhere("A-101");

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public void DocumentNumberExistsAnywhere_InHistory_ReturnsTrue()
    {
        // Arrange
        var doc = new Document("A-101-NEW", "Floor Plan", "1", _testRevisionId);
        doc.AddToHistory("A-101-OLD");
        _documentRepository.Insert(doc);

        // Act
        var result = _documentRepository.DocumentNumberExistsAnywhere("A-101-OLD");

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public void DocumentNumberExistsAnywhere_NotFound_ReturnsFalse()
    {
        // Arrange
        var doc = new Document("A-101", "Floor Plan", "1", _testRevisionId);
        _documentRepository.Insert(doc);

        // Act
        var result = _documentRepository.DocumentNumberExistsAnywhere("A-999");

        // Assert
        Assert.That(result, Is.False);
    }

    #endregion

    #region GetAllDocumentNumbersEverUsed Tests

    [Test]
    public void GetAllDocumentNumbersEverUsed_ReturnsCurrentAndHistoricalNumbers()
    {
        // Arrange
        var doc1 = new Document("A-101-V3", "Floor Plan", "1", _testRevisionId);
        doc1.AddToHistory("A-101-V1");
        doc1.AddToHistory("A-101-V2");
        _documentRepository.Insert(doc1);

        var doc2 = new Document("A-102", "Ceiling Plan", "1", _testRevisionId);
        _documentRepository.Insert(doc2);

        // Act
        var result = _documentRepository.GetAllDocumentNumbersEverUsed();

        // Assert
        Assert.That(result, Has.Count.EqualTo(4));
        Assert.That(result, Does.Contain("A-101-V1"));
        Assert.That(result, Does.Contain("A-101-V2"));
        Assert.That(result, Does.Contain("A-101-V3"));
        Assert.That(result, Does.Contain("A-102"));
    }

    #endregion

    #region GetAllDocumentsByRevision Tests

    [Test]
    public void GetAllDocumentsByRevision_ReturnsActiveAndInactiveDocuments()
    {
        // Arrange
        var active = new Document("A-101", "Active", "1", _testRevisionId);
        var inactive = new Document("A-102", "Inactive", "1", _testRevisionId);
        
        _documentRepository.Insert(active);
        _documentRepository.Insert(inactive);
        
        _documentRepository.UpdateActiveStatus(inactive.Id, false);

        // Act
        var result = _documentRepository.GetAllDocumentsByRevision(_testRevisionId);

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
    }

    #endregion

    #region GetAllDocumentsByNumber Tests

    [Test]
    public void GetAllDocumentsByNumber_ReturnsActiveAndInactiveDocuments()
    {
        // Arrange
        var active = new Document("A-101", "Rev 1", "1", _testRevisionId);
        var inactive = new Document("A-101", "Rev 2", "2", _testRevisionId);
        
        _documentRepository.Insert(active);
        _documentRepository.Insert(inactive);
        
        _documentRepository.UpdateActiveStatus(inactive.Id, false);

        // Act
        var result = _documentRepository.GetAllDocumentsByNumber("A-101");

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
    }

    #endregion

    #region AnyDocumentExists Tests

    [Test]
    public void AnyDocumentExists_FindsActiveAndInactiveDocuments()
    {
        // Arrange
        var doc = new Document("A-101", "Floor Plan", "1", _testRevisionId);
        _documentRepository.Insert(doc);
        _documentRepository.UpdateActiveStatus(doc.Id, false);

        // Act
        var result = _documentRepository.AnyDocumentExists("A-101", "1");

        // Assert
        Assert.That(result, Is.True);
    }

    #endregion

    #region Integration Tests

    [Test]
    public void IntegrationTest_CompleteDocumentLifecycle()
    {
        // Create
        var doc = new Document("A-101", "Floor Plan", "1", _testRevisionId);
        _documentRepository.Insert(doc);

        // Read
        var retrieved = _documentRepository.GetLatestDocumentRevision("A-101");
        Assert.That(retrieved, Is.Not.Null);

        // Update
        doc.Name = "Updated Floor Plan";
        _documentRepository.Update(doc);
        var updated = _documentRepository.GetById(doc.Id);
        Assert.That(updated.Name, Is.EqualTo("Updated Floor Plan"));

        // Toggle active status
        _documentRepository.UpdateActiveStatus(doc.Id, false);
        var inactive = _documentRepository.GetById(doc.Id);
        Assert.That(inactive.IsActive, Is.False);

        // Verify in inactive list
        var inactiveList = _documentRepository.GetInactiveDocuments();
        Assert.That(inactiveList, Has.Count.EqualTo(1));

        // Toggle back to active
        _documentRepository.UpdateActiveStatus(doc.Id, true);
        var activeAgain = _documentRepository.GetById(doc.Id);
        Assert.That(activeAgain.IsActive, Is.True);
    }

    #endregion
}
