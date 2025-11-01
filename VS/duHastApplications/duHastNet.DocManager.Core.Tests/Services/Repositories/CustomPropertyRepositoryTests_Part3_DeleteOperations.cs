using NUnit.Framework;
using SQLite;
using duHastNet.DocManager.Core.Services.Repositories;
using duHastNet.DocManager.Core.Models;
using System.IO;

namespace duHastNet.DocManager.Core.Tests.Services.Repositories;

[TestFixture]
public class CustomPropertyRepositoryTests_Part3_DeleteOperations
{
    //private SQLiteAsyncConnection _connection;
    //private string _databasePath;
    //private CustomPropertyRepository _customPropertyRepository;
    //private DocumentRepository _documentRepository;
    //private RevisionRepository _revisionRepository;
    //private int _testDocumentId1;
    //private int _testDocumentId2;

    //[SetUp]
    //public async Task Setup()
    //{
    //    // Create a temporary database file for testing
    //    _databasePath = Path.GetTempFileName();

    //    var connectionString = new SQLiteConnectionString(_databasePath,
    //        storeDateTimeAsTicks: false,
    //        openFlags: SQLiteOpenFlags.ReadWrite | SQLiteOpenFlags.Create,
    //        key: null);

    //    _connection = new SQLiteAsyncConnection(connectionString);

    //    // Create tables
    //    await _connection.CreateTableAsync<Revision>();
    //    await _connection.CreateTableAsync<Document>();
    //    await _connection.CreateTableAsync<CustomProperty>();

    //    _customPropertyRepository = new CustomPropertyRepository(_connection);
    //    _documentRepository = new DocumentRepository(_connection);
    //    _revisionRepository = new RevisionRepository(_connection);

    //    // Create test data
    //    var testRevision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
    //    await _revisionRepository.InsertAsync(testRevision);

    //    var document1 = new Document("A-101", "Floor Plan", "1", testRevision.Id);
    //    var document2 = new Document("A-102", "Ceiling Plan", "1", testRevision.Id);

    //    await _documentRepository.InsertAsync(document1);
    //    await _documentRepository.InsertAsync(document2);

    //    _testDocumentId1 = document1.Id;
    //    _testDocumentId2 = document2.Id;
    //}

    //[TearDown]
    //public async Task TearDown()
    //{
    //    if (_connection != null)
    //    {
    //        await _connection.CloseAsync();
    //    }

    //    if (File.Exists(_databasePath))
    //    {
    //        File.Delete(_databasePath);
    //    }
    //}

    //[Test]
    //public async Task DeletePropertiesByDocumentAsync_WithPropertiesForDocument_DeletesAllPropertiesForDocument()
    //{
    //    // Arrange
    //    var properties = new[]
    //    {
    //        new CustomProperty(_testDocumentId1, "DisciplineCode", "ARCH"),
    //        new CustomProperty(_testDocumentId1, "ProjectPhase", "Construction"),
    //        new CustomProperty(_testDocumentId2, "DisciplineCode", "MECH")
    //    };

    //    foreach (var property in properties)
    //    {
    //        await _customPropertyRepository.InsertAsync(property);
    //    }

    //    // Act
    //    var result = await _customPropertyRepository.DeletePropertiesByDocumentAsync(_testDocumentId1);

    //    // Assert
    //    Assert.That(result, Is.EqualTo(2)); // Two properties deleted

    //    // Verify deletion
    //    var remainingProperties = await _customPropertyRepository.GetPropertiesByDocumentAsync(_testDocumentId1);
    //    Assert.That(remainingProperties, Has.Count.EqualTo(0));

    //    // Verify other document's properties remain
    //    var otherDocProperties = await _customPropertyRepository.GetPropertiesByDocumentAsync(_testDocumentId2);
    //    Assert.That(otherDocProperties, Has.Count.EqualTo(1));
    //}

    //[Test]
    //public async Task DeletePropertiesByDocumentAsync_NoPropertiesForDocument_ReturnsZero()
    //{
    //    // Arrange
    //    var property = new CustomProperty(_testDocumentId1, "DisciplineCode", "ARCH");
    //    await _customPropertyRepository.InsertAsync(property);

    //    // Act
    //    var result = await _customPropertyRepository.DeletePropertiesByDocumentAsync(_testDocumentId2);

    //    // Assert
    //    Assert.That(result, Is.EqualTo(0));

    //    // Verify original property still exists
    //    var originalProperty = await _customPropertyRepository.GetPropertiesByDocumentAsync(_testDocumentId1);
    //    Assert.That(originalProperty, Has.Count.EqualTo(1));
    //}

    //[Test]
    //public async Task DeletePropertiesByDocumentAsync_NonExistentDocument_ReturnsZero()
    //{
    //    // Arrange
    //    var property = new CustomProperty(_testDocumentId1, "DisciplineCode", "ARCH");
    //    await _customPropertyRepository.InsertAsync(property);

    //    // Act
    //    var result = await _customPropertyRepository.DeletePropertiesByDocumentAsync(999);

    //    // Assert
    //    Assert.That(result, Is.EqualTo(0));

    //    // Verify original property still exists
    //    var originalProperty = await _customPropertyRepository.GetPropertiesByDocumentAsync(_testDocumentId1);
    //    Assert.That(originalProperty, Has.Count.EqualTo(1));
    //}

    //[Test]
    //public async Task DeletePropertyAsync_ExistingProperty_DeletesSpecificProperty()
    //{
    //    // Arrange
    //    var properties = new[]
    //    {
    //        new CustomProperty(_testDocumentId1, "DisciplineCode", "ARCH"),
    //        new CustomProperty(_testDocumentId1, "ProjectPhase", "Construction")
    //    };

    //    foreach (var property in properties)
    //    {
    //        await _customPropertyRepository.InsertAsync(property);
    //    }

    //    // Act
    //    var result = await _customPropertyRepository.DeletePropertyAsync(_testDocumentId1, "DisciplineCode");

    //    // Assert
    //    Assert.That(result, Is.EqualTo(1));

    //    // Verify specific property deleted
    //    var deletedProperty = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "DisciplineCode");
    //    Assert.That(deletedProperty, Is.Null);

    //    // Verify other property remains
    //    var remainingProperty = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "ProjectPhase");
    //    Assert.That(remainingProperty, Is.Not.Null);
    //}

    //[Test]
    //public async Task DeletePropertyAsync_NonExistentProperty_ReturnsZero()
    //{
    //    // Arrange
    //    var property = new CustomProperty(_testDocumentId1, "DisciplineCode", "ARCH");
    //    await _customPropertyRepository.InsertAsync(property);

    //    // Act
    //    var result = await _customPropertyRepository.DeletePropertyAsync(_testDocumentId1, "NonExistent");

    //    // Assert
    //    Assert.That(result, Is.EqualTo(0));

    //    // Verify original property still exists
    //    var originalProperty = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "DisciplineCode");
    //    Assert.That(originalProperty, Is.Not.Null);
    //}

    //[Test]
    //public async Task DeletePropertyAsync_SamePropertyNameDifferentDocument_DeletesOnlySpecifiedDocument()
    //{
    //    // Arrange
    //    var properties = new[]
    //    {
    //        new CustomProperty(_testDocumentId1, "DisciplineCode", "ARCH"),
    //        new CustomProperty(_testDocumentId2, "DisciplineCode", "MECH")
    //    };

    //    foreach (var property in properties)
    //    {
    //        await _customPropertyRepository.InsertAsync(property);
    //    }

    //    // Act
    //    var result = await _customPropertyRepository.DeletePropertyAsync(_testDocumentId1, "DisciplineCode");

    //    // Assert
    //    Assert.That(result, Is.EqualTo(1));

    //    // Verify property deleted from document 1
    //    var doc1Property = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "DisciplineCode");
    //    Assert.That(doc1Property, Is.Null);

    //    // Verify property remains for document 2
    //    var doc2Property = await _customPropertyRepository.GetPropertyAsync(_testDocumentId2, "DisciplineCode");
    //    Assert.That(doc2Property, Is.Not.Null);
    //    Assert.That(doc2Property.PropertyValue, Is.EqualTo("MECH"));
    //}

}