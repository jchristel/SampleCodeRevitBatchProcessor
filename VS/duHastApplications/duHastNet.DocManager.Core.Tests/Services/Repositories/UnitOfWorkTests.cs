using NUnit.Framework;
using SQLite;
using duHastNet.DocManager.Core.Services.Repositories;
using duHastNet.DocManager.Core.Models;
using System.IO;

namespace duHastNet.DocManager.Core.Tests.Services.Repositories;

[TestFixture]
public class UnitOfWorkTests
{
    private SQLiteAsyncConnection _connection;
    private string _databasePath;
    private UnitOfWork _unitOfWork;

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
        await _connection.CreateTableAsync<CustomProperty>();

        _unitOfWork = new UnitOfWork(_connection);
    }

    [TearDown]
    public async Task TearDown()
    {
        _unitOfWork?.Dispose();

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
    public void Constructor_InitializesAllRepositories()
    {
        Assert.Multiple(() =>
        {
            // Act & Assert
            Assert.That(_unitOfWork.Revisions, Is.Not.Null);
            Assert.That(_unitOfWork.Documents, Is.Not.Null);
            Assert.That(_unitOfWork.CustomProperties, Is.Not.Null);

            Assert.That(_unitOfWork.Revisions, Is.TypeOf<RevisionRepository>());
            Assert.That(_unitOfWork.Documents, Is.TypeOf<DocumentRepository>());
            Assert.That(_unitOfWork.CustomProperties, Is.TypeOf<CustomPropertyRepository>());
        });
    }

    [Test]
    public async Task SaveChangesAsync_WithSqliteNetPcl_ReturnsZero()
    {
        // With sqlite-net-pcl, changes are immediately persisted
        // This method exists for interface compatibility

        // Act
        var result = await _unitOfWork.SaveChangesAsync();

        // Assert
        Assert.That(result, Is.EqualTo(0));
    }

    [Test]
    public async Task BeginTransactionAsync_CompletesSuccessfully()
    {
        // With sqlite-net-pcl, transactions are handled by RunInTransactionAsync
        // This method exists for interface compatibility

        // Act & Assert - Should not throw
        await _unitOfWork.BeginTransactionAsync();
    }

    [Test]
    public async Task CommitTransactionAsync_CompletesSuccessfully()
    {
        // With sqlite-net-pcl, transactions are handled automatically
        // This method exists for interface compatibility

        // Act & Assert - Should not throw
        await _unitOfWork.CommitTransactionAsync();
    }

    [Test]
    public async Task RollbackTransactionAsync_CompletesSuccessfully()
    {
        // With sqlite-net-pcl, rollback is handled automatically if exception occurs
        // This method exists for interface compatibility

        // Act & Assert - Should not throw
        await _unitOfWork.RollbackTransactionAsync();
    }

    [Test]
    public async Task AllRepositories_ShareSameConnection()
    {
        // Create test data using different repositories

        // Arrange & Act
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        await _unitOfWork.Revisions.InsertAsync(revision);

        var document = new Document("A-101", "Floor Plan", "1", revision.Id);
        await _unitOfWork.Documents.InsertAsync(document);

        var customProperty = new CustomProperty(document.Id, "DisciplineCode", "ARCH");
        await _unitOfWork.CustomProperties.InsertAsync(customProperty);

        // Assert - All data should be accessible through any repository since they share the connection
        var retrievedRevision = await _unitOfWork.Revisions.GetByIdAsync(revision.Id);
        var retrievedDocument = await _unitOfWork.Documents.GetByIdAsync(document.Id);
        var retrievedProperty = await _unitOfWork.CustomProperties.GetByIdAsync(customProperty.Id);

        Assert.Multiple(() =>
        {
            Assert.That(retrievedRevision, Is.Not.Null);
            Assert.That(retrievedDocument, Is.Not.Null);
            Assert.That(retrievedProperty, Is.Not.Null);
        });
    }

    [Test]
    public async Task CrossRepositoryOperations_WorkCorrectly()
    {
        // Test operations that span multiple repositories

        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        await _unitOfWork.Revisions.InsertAsync(revision);

        var documents = new[]
        {
            new Document("A-101", "Floor Plan", "1", revision.Id),
            new Document("A-102", "Ceiling Plan", "1", revision.Id)
        };

        foreach (var doc in documents)
        {
            await _unitOfWork.Documents.InsertAsync(doc);
        }

        var properties = new[]
        {
            new CustomProperty(documents[0].Id, "DisciplineCode", "ARCH"),
            new CustomProperty(documents[0].Id, "ProjectPhase", "Construction"),
            new CustomProperty(documents[1].Id, "DisciplineCode", "ARCH")
        };

        foreach (var prop in properties)
        {
            await _unitOfWork.CustomProperties.InsertAsync(prop);
        }

        // Act - Complex query across repositories
        var documentsInRevision = await _unitOfWork.Documents.GetDocumentsByRevisionAsync(revision.Id);
        var archProperties = await _unitOfWork.CustomProperties.GetPropertiesByNameAndValueAsync("DisciplineCode", "ARCH");

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(documentsInRevision, Has.Count.EqualTo(2));
            Assert.That(archProperties, Has.Count.EqualTo(2));
        });

        // Verify relationships
        var documentIds = documentsInRevision.Select(d => d.Id).ToList();
        Assert.That(archProperties.All(p => documentIds.Contains(p.DocumentId)), Is.True);
    }

    [Test]
    public async Task RepositoryOperations_AreImmediatelyPersisted()
    {
        // With sqlite-net-pcl, operations are immediately persisted to the database
        // No explicit SaveChanges() is needed

        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");

        // Act
        await _unitOfWork.Revisions.InsertAsync(revision);

        // No SaveChanges() call needed with sqlite-net-pcl

        // Create a new UnitOfWork instance to verify persistence
        using var newUnitOfWork = new UnitOfWork(_connection);
        var retrievedRevision = await newUnitOfWork.Revisions.GetByIdAsync(revision.Id);

        // Assert
        Assert.That(retrievedRevision, Is.Not.Null);
        Assert.That(retrievedRevision.Description, Is.EqualTo("Test Revision"));
    }

    [Test]
    public void Dispose_DoesNotThrow()
    {
        // The UnitOfWork.Dispose() method doesn't manage the connection directly
        // Connection is managed by DatabaseService

        // Act & Assert - Should not throw
        Assert.DoesNotThrow(() => _unitOfWork.Dispose());
    }

    [Test]
    public async Task ConcurrentOperations_WorkCorrectly()
    {
        // Test that concurrent operations work correctly with the shared connection

        // Arrange
        var revision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        await _unitOfWork.Revisions.InsertAsync(revision);

        var tasks = new List<Task>();

        // Act - Create multiple documents concurrently
        for (int i = 0; i < 10; i++)
        {
            var docNumber = $"A-{i:000}";
            var docName = $"Document {i}";

            tasks.Add(Task.Run(async () =>
            {
                var document = new Document(docNumber, docName, "1", revision.Id);
                await _unitOfWork.Documents.InsertAsync(document);

                var property = new CustomProperty(document.Id, "Index", i.ToString());
                await _unitOfWork.CustomProperties.InsertAsync(property);
            }));
        }

        await Task.WhenAll(tasks);

        // Assert
        var allDocuments = await _unitOfWork.Documents.GetDocumentsByRevisionAsync(revision.Id);
        var allProperties = await _unitOfWork.CustomProperties.GetPropertiesByNameAsync("Index");

        Assert.Multiple(() =>
        {
            Assert.That(allDocuments, Has.Count.EqualTo(10));
            Assert.That(allProperties, Has.Count.EqualTo(10));
        });
    }

    [Test]
    public async Task RepositoryMethods_CanBeCalledMultipleTimes()
    {
        // Test that repository methods can be called multiple times without issues

        // Arrange
        var revision1 = new Revision(new DateTime(2024, 2, 15), "Revision 1");
        var revision2 = new Revision(new DateTime(2024, 2, 16), "Revision 2");

        // Act - Multiple operations on same repository
        await _unitOfWork.Revisions.InsertAsync(revision1);
        await _unitOfWork.Revisions.InsertAsync(revision2);

        var allRevisions1 = await _unitOfWork.Revisions.GetAllAsync();
        var allRevisions2 = await _unitOfWork.Revisions.GetAllAsync();

        var count1 = await _unitOfWork.Revisions.CountAsync();
        var count2 = await _unitOfWork.Revisions.CountAsync();

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
    public async Task ComplexWorkflow_WithAllRepositories_WorksCorrectly()
    {
        // Test a complete workflow using all repositories

        // Step 1: Create a revision
        var revision = new Revision(new DateTime(2024, 2, 15), "For Construction");
        await _unitOfWork.Revisions.InsertAsync(revision);

        // Step 2: Add documents to the revision
        var documents = new[]
        {
            new Document("A-101", "Architectural Floor Plan", "2", revision.Id),
            new Document("S-201", "Structural Foundation Plan", "1", revision.Id),
            new Document("M-301", "HVAC Plan", "1", revision.Id)
        };

        foreach (var doc in documents)
        {
            await _unitOfWork.Documents.InsertAsync(doc);
        }

        // Step 3: Add custom properties to documents
        var properties = new[]
        {
            new CustomProperty(documents[0].Id, "DisciplineCode", "ARCH"),
            new CustomProperty(documents[0].Id, "DrawingSize", "A1"),
            new CustomProperty(documents[1].Id, "DisciplineCode", "STRUCT"),
            new CustomProperty(documents[1].Id, "DrawingSize", "A3"),
            new CustomProperty(documents[2].Id, "DisciplineCode", "MECH"),
            new CustomProperty(documents[2].Id, "DrawingSize", "A1")
        };

        foreach (var prop in properties)
        {
            await _unitOfWork.CustomProperties.InsertAsync(prop);
        }

        // Step 4: Perform complex queries
        var revisionDocuments = await _unitOfWork.Documents.GetDocumentsByRevisionAsync(revision.Id);
        var a1Drawings = await _unitOfWork.CustomProperties.GetPropertiesByNameAndValueAsync("DrawingSize", "A1");
        var archDocuments = await _unitOfWork.CustomProperties.GetPropertiesByNameAndValueAsync("DisciplineCode", "ARCH");

        // Step 5: Verify results
        Assert.Multiple(() =>
        {
            Assert.That(revisionDocuments, Has.Count.EqualTo(3));
            Assert.That(a1Drawings, Has.Count.EqualTo(2)); // A-101 and M-301
            Assert.That(archDocuments, Has.Count.EqualTo(1)); // Only A-101
        });

        // Step 6: Update operations
        revision.Description = "For Construction - Updated";
        await _unitOfWork.Revisions.UpdateAsync(revision);

        documents[0].Name = "Architectural Floor Plan - Updated";
        await _unitOfWork.Documents.UpdateAsync(documents[0]);

        // Step 7: Verify updates
        var updatedRevision = await _unitOfWork.Revisions.GetByIdAsync(revision.Id);
        var updatedDocument = await _unitOfWork.Documents.GetByIdAsync(documents[0].Id);

        Assert.Multiple(() =>
        {
            Assert.That(updatedRevision.Description, Is.EqualTo("For Construction - Updated"));
            Assert.That(updatedDocument.Name, Is.EqualTo("Architectural Floor Plan - Updated"));
        });

        // Step 8: Cleanup operations
        await _unitOfWork.CustomProperties.DeletePropertiesByDocumentAsync(documents[0].Id);
        var remainingProperties = await _unitOfWork.CustomProperties.GetPropertiesByDocumentAsync(documents[0].Id);

        Assert.That(remainingProperties, Has.Count.EqualTo(0));
    }
}