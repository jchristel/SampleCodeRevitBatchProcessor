using NUnit.Framework;
using SQLite;
using duHastNet.DocManager.Core.Services.Repositories;
using duHastNet.DocManager.Core.Models;
using System.IO;
using duHastNet.DocManager.Core.Models.Database;

namespace duHastNet.DocManager.Core.Tests.Services.Repositories;

[TestFixture]
public class UnitOfWorkSyncTests
{
    private SQLiteConnection _connection;
    private string _databasePath;
    private UnitOfWorkSync _unitOfWorkSync;

    [SetUp]
    public void Setup()
    {
        _databasePath = Path.Combine(
            Path.GetTempPath(),
            "UnitOfWorkSyncTests",
            Guid.NewGuid().ToString(),
            "test.db");

        Directory.CreateDirectory(Path.GetDirectoryName(_databasePath)!);

        var connectionString = new SQLiteConnectionString(
            _databasePath,
            storeDateTimeAsTicks: false,
            openFlags: SQLiteOpenFlags.ReadWrite | SQLiteOpenFlags.Create,
            key: null);

        _connection = new SQLiteConnection(connectionString);

        _connection.CreateTable<Revision>();
        _connection.CreateTable<Document>();
        _connection.CreateTable<CustomFieldDefinition>();
        _connection.CreateTable<CustomProperty>();

        _unitOfWorkSync = new UnitOfWorkSync(_connection);
    }

    [TearDown]
    public void TearDown()
    {
        _unitOfWorkSync?.Dispose();
        _connection?.Close();

        var dir = Path.GetDirectoryName(_databasePath);
        if (Directory.Exists(dir))
            Directory.Delete(dir, true);
    }

    [Test]
    public void Constructor_InitializesAllRepositories()
    {
        Assert.Multiple(() =>
        {
            // Act & Assert
            Assert.That(_unitOfWorkSync.Revisions, Is.Not.Null);
            Assert.That(_unitOfWorkSync.Documents, Is.Not.Null);
            Assert.That(_unitOfWorkSync.CustomProperties, Is.Not.Null);
            Assert.That(_unitOfWorkSync.CustomFieldDefinitions, Is.Not.Null);

            Assert.That(_unitOfWorkSync.Revisions, Is.TypeOf<RevisionRepositorySync>());
            Assert.That(_unitOfWorkSync.Documents, Is.TypeOf<DocumentRepositorySync>());
            Assert.That(_unitOfWorkSync.CustomProperties, Is.TypeOf<CustomPropertyRepositorySync>());
            Assert.That(_unitOfWorkSync.CustomFieldDefinitions, Is.TypeOf<CustomFieldDefinitionRepositorySync>());
        });
    }

    [Test]
    public void SaveChanges_WithSqliteNetPcl_ReturnsZero()
    {
        // With sqlite-net-pcl, changes are immediately persisted
        // This method exists for interface compatibility

        // Act
        var result = _unitOfWorkSync.SaveChanges();

        // Assert
        Assert.That(result, Is.EqualTo(0));
    }

    [Test]
    public void AllRepositories_ShareSameConnection()
    {
        // Create test data using different repositories

        // Arrange & Act
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        _unitOfWorkSync.Revisions.Insert(revision);

        var document = new Document("A-101", "Floor Plan", "1", revision.Id);
        _unitOfWorkSync.Documents.Insert(document);

        var fieldDef = new CustomFieldDefinition("DisciplineCode", true);
        _unitOfWorkSync.CustomFieldDefinitions.Insert(fieldDef);

        var customProperty = new CustomProperty(document.Id, fieldDef.Id, "ARCH");
        _unitOfWorkSync.CustomProperties.Insert(customProperty);

        // Assert - All data should be accessible through any repository since they share the connection
        var retrievedRevision = _unitOfWorkSync.Revisions.GetById(revision.Id);
        var retrievedDocument = _unitOfWorkSync.Documents.GetById(document.Id);
        var retrievedFieldDef = _unitOfWorkSync.CustomFieldDefinitions.GetById(fieldDef.Id);
        var retrievedProperty = _unitOfWorkSync.CustomProperties.GetById(customProperty.Id);

        Assert.Multiple(() =>
        {
            Assert.That(retrievedRevision, Is.Not.Null);
            Assert.That(retrievedDocument, Is.Not.Null);
            Assert.That(retrievedFieldDef, Is.Not.Null);
            Assert.That(retrievedProperty, Is.Not.Null);
        });
    }

    [Test]
    public void CrossRepositoryOperations_WorkCorrectly()
    {
        // Test operations that span multiple repositories

        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        _unitOfWorkSync.Revisions.Insert(revision);

        var documents = new[]
        {
            new Document("A-101", "Floor Plan", "1", revision.Id),
            new Document("A-102", "Ceiling Plan", "1", revision.Id)
        };

        foreach (var doc in documents)
        {
            _unitOfWorkSync.Documents.Insert(doc);
        }

        var fieldDef = new CustomFieldDefinition("DisciplineCode", true);
        _unitOfWorkSync.CustomFieldDefinitions.Insert(fieldDef);

        var properties = new[]
        {
            new CustomProperty(documents[0].Id, fieldDef.Id, "ARCH"),
            new CustomProperty(documents[1].Id, fieldDef.Id, "ARCH")
        };

        foreach (var prop in properties)
        {
            _unitOfWorkSync.CustomProperties.Insert(prop);
        }

        // Act - Complex query across repositories
        var documentsInRevision = _unitOfWorkSync.Documents.GetDocumentsByRevision(revision.Id);
        var doc1Properties = _unitOfWorkSync.CustomProperties.GetPropertiesByDocument(documents[0].Id);
        var doc2Properties = _unitOfWorkSync.CustomProperties.GetPropertiesByDocument(documents[1].Id);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(documentsInRevision, Has.Count.EqualTo(2));
            Assert.That(doc1Properties, Has.Count.EqualTo(1));
            Assert.That(doc2Properties, Has.Count.EqualTo(1));
        });

        // Verify relationships
        var documentIds = documentsInRevision.Select(d => d.Id).ToList();
        Assert.That(doc1Properties.All(p => documentIds.Contains(p.DocumentId)), Is.True);
        Assert.That(doc2Properties.All(p => documentIds.Contains(p.DocumentId)), Is.True);
    }

    [Test]
    public void RepositoryOperations_AreImmediatelyPersisted()
    {
        // With sqlite-net-pcl, operations are immediately persisted to the database
        // No explicit SaveChanges() is needed

        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");

        // Act
        _unitOfWorkSync.Revisions.Insert(revision);

        // No SaveChanges() call needed with sqlite-net-pcl

        // Create a new UnitOfWorkSync instance to verify persistence
        using var newUnitOfWorkSync = new UnitOfWorkSync(_connection);
        var retrievedRevision = newUnitOfWorkSync.Revisions.GetById(revision.Id);

        // Assert
        Assert.That(retrievedRevision, Is.Not.Null);
        Assert.That(retrievedRevision.Description, Is.EqualTo("Test Revision"));
    }

    [Test]
    public void RunInTransaction_OnSuccess_CommitsAllWrites()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        _unitOfWorkSync.Revisions.Insert(revision);

        // Act
        _unitOfWorkSync.RunInTransaction(() =>
        {
            _unitOfWorkSync.Documents.Insert(new Document("A-101", "Floor Plan", "1", revision.Id));
            _unitOfWorkSync.Documents.Insert(new Document("A-102", "Ceiling Plan", "1", revision.Id));
        });

        // Assert - both documents written inside the transaction are visible
        var allDocs = _unitOfWorkSync.Documents.GetAll();
        Assert.That(allDocs, Has.Count.EqualTo(2));
    }

    [Test]
    public void RunInTransaction_OnException_RollsBackAllWrites()
    {
        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        _unitOfWorkSync.Revisions.Insert(revision);

        // Act - transaction throws part way through
        Assert.Throws<InvalidOperationException>(() =>
        {
            _unitOfWorkSync.RunInTransaction(() =>
            {
                _unitOfWorkSync.Documents.Insert(new Document("A-101", "Floor Plan", "1", revision.Id));
                throw new InvalidOperationException("Simulated failure");
            });
        });

        // Assert - no documents were committed
        var allDocs = _unitOfWorkSync.Documents.GetAll();
        Assert.That(allDocs, Has.Count.EqualTo(0));
    }

    [Test]
    public void Dispose_DoesNotThrow()
    {
        // The UnitOfWorkSync.Dispose() method doesn't manage the connection directly
        // Connection is managed by DatabaseService

        // Act & Assert - Should not throw
        Assert.DoesNotThrow(() => _unitOfWorkSync.Dispose());
    }

    [Test]
    public void RepositoryMethods_CanBeCalledMultipleTimes()
    {
        // Test that repository methods can be called multiple times without issues

        // Arrange
        var revision1 = new Revision(new DateTime(2024, 2, 15), "Revision 1");
        var revision2 = new Revision(new DateTime(2024, 2, 16), "Revision 2");

        // Act - Multiple operations on same repository
        _unitOfWorkSync.Revisions.Insert(revision1);
        _unitOfWorkSync.Revisions.Insert(revision2);

        var allRevisions1 = _unitOfWorkSync.Revisions.GetAll();
        var allRevisions2 = _unitOfWorkSync.Revisions.GetAll();

        var count1 = _unitOfWorkSync.Revisions.Count();
        var count2 = _unitOfWorkSync.Revisions.Count();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(allRevisions1, Has.Count.EqualTo(2));
            Assert.That(allRevisions2, Has.Count.EqualTo(2));
            Assert.That(count1, Is.EqualTo(2));
            Assert.That(count2, Is.EqualTo(2));
        });
    }

    [Test]
    public void ComplexWorkflow_WithAllRepositories_WorksCorrectly()
    {
        // Test a complete workflow using all repositories

        // Step 1: Create a revision
        var revision = new Revision(new DateTime(2024, 2, 15), "For Construction");
        _unitOfWorkSync.Revisions.Insert(revision);

        // Step 2: Add documents to the revision
        var documents = new[]
        {
            new Document("A-101", "Architectural Floor Plan", "2", revision.Id),
            new Document("S-201", "Structural Foundation Plan", "1", revision.Id),
            new Document("M-301", "HVAC Plan", "1", revision.Id)
        };

        foreach (var doc in documents)
        {
            _unitOfWorkSync.Documents.Insert(doc);
        }

        // Step 3: Create custom field definitions
        var disciplineField = new CustomFieldDefinition("DisciplineCode", true);
        var drawingSizeField = new CustomFieldDefinition("DrawingSize", true);
        _unitOfWorkSync.CustomFieldDefinitions.Insert(disciplineField);
        _unitOfWorkSync.CustomFieldDefinitions.Insert(drawingSizeField);

        // Step 4: Add custom properties to documents
        var properties = new[]
        {
            new CustomProperty(documents[0].Id, disciplineField.Id, "ARCH"),
            new CustomProperty(documents[0].Id, drawingSizeField.Id, "A1"),
            new CustomProperty(documents[1].Id, disciplineField.Id, "STRUCT"),
            new CustomProperty(documents[1].Id, drawingSizeField.Id, "A3"),
            new CustomProperty(documents[2].Id, disciplineField.Id, "MECH"),
            new CustomProperty(documents[2].Id, drawingSizeField.Id, "A1")
        };

        foreach (var prop in properties)
        {
            _unitOfWorkSync.CustomProperties.Insert(prop);
        }

        // Step 5: Perform complex queries
        var revisionDocuments = _unitOfWorkSync.Documents.GetDocumentsByRevision(revision.Id);
        var a1Drawings = _unitOfWorkSync.CustomProperties.Find(p => p.CustomFieldDefinitionId == drawingSizeField.Id && p.PropertyValue == "A1");
        var archDocuments = _unitOfWorkSync.CustomProperties.Find(p => p.CustomFieldDefinitionId == disciplineField.Id && p.PropertyValue == "ARCH");

        // Step 6: Verify results
        Assert.Multiple(() =>
        {
            Assert.That(revisionDocuments, Has.Count.EqualTo(3));
            Assert.That(a1Drawings, Has.Count.EqualTo(2)); // A-101 and M-301
            Assert.That(archDocuments, Has.Count.EqualTo(1)); // Only A-101
        });

        // Step 7: Update operations
        revision.Description = "For Construction - Updated";
        _unitOfWorkSync.Revisions.Update(revision);

        documents[0].Name = "Architectural Floor Plan - Updated";
        _unitOfWorkSync.Documents.Update(documents[0]);

        // Step 8: Verify updates
        var updatedRevision = _unitOfWorkSync.Revisions.GetById(revision.Id);
        var updatedDocument = _unitOfWorkSync.Documents.GetById(documents[0].Id);

        Assert.Multiple(() =>
        {
            Assert.That(updatedRevision.Description, Is.EqualTo("For Construction - Updated"));
            Assert.That(updatedDocument.Name, Is.EqualTo("Architectural Floor Plan - Updated"));
        });

        // Step 9: Delete operations using inherited Delete method
        var doc1Properties = _unitOfWorkSync.CustomProperties.GetPropertiesByDocument(documents[0].Id);
        foreach (var prop in doc1Properties)
        {
            _unitOfWorkSync.CustomProperties.Delete(prop.Id);
        }
        
        var remainingProperties = _unitOfWorkSync.CustomProperties.GetPropertiesByDocument(documents[0].Id);

        Assert.That(remainingProperties, Has.Count.EqualTo(0));
    }
}
