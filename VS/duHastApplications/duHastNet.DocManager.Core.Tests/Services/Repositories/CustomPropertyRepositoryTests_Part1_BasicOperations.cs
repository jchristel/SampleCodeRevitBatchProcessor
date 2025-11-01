using NUnit.Framework;
using SQLite;
using duHastNet.DocManager.Core.Services.Repositories;
using duHastNet.DocManager.Core.Models;
using System.IO;

namespace duHastNet.DocManager.Core.Tests.Services.Repositories;

[TestFixture]
public class CustomPropertyRepositoryTests_Part1_BasicOperations
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
    //public async Task GetPropertiesByDocumentAsync_WithPropertiesForDocument_ReturnsPropertiesOrderedByName()
    //{
    //    // Arrange
    //    var properties = new[]
    //    {
    //        new CustomProperty(_testDocumentId1, "ZoneCode", "Zone A"),
    //        new CustomProperty(_testDocumentId1, "DisciplineCode", "ARCH"),
    //        new CustomProperty(_testDocumentId1, "ProjectPhase", "Construction"),
    //        new CustomProperty(_testDocumentId2, "DisciplineCode", "MECH") // Different document
    //    };

    //    foreach (var property in properties)
    //    {
    //        await _customPropertyRepository.InsertAsync(property);
    //    }

    //    // Act
    //    var result = await _customPropertyRepository.GetPropertiesByDocumentAsync(_testDocumentId1);

    //    // Assert
    //    Assert.That(result, Has.Count.EqualTo(3));
    //    Assert.That(result.All(p => p.DocumentId == _testDocumentId1), Is.True);
    //    // Should be ordered by PropertyName
    //    Assert.That(result[0].PropertyName, Is.EqualTo("DisciplineCode"));
    //    Assert.That(result[1].PropertyName, Is.EqualTo("ProjectPhase"));
    //    Assert.That(result[2].PropertyName, Is.EqualTo("ZoneCode"));
    //}

    //[Test]
    //public async Task GetPropertiesByDocumentAsync_NoPropertiesForDocument_ReturnsEmptyList()
    //{
    //    // Arrange
    //    var property = new CustomProperty(_testDocumentId1, "TestProperty", "TestValue");
    //    await _customPropertyRepository.InsertAsync(property);

    //    // Act
    //    var result = await _customPropertyRepository.GetPropertiesByDocumentAsync(_testDocumentId2);

    //    // Assert
    //    Assert.That(result, Is.Not.Null);
    //    Assert.That(result, Has.Count.EqualTo(0));
    //}

    //[Test]
    //public async Task GetPropertyAsync_ExistingProperty_ReturnsProperty()
    //{
    //    // Arrange
    //    var property = new CustomProperty(_testDocumentId1, "DisciplineCode", "ARCH");
    //    await _customPropertyRepository.InsertAsync(property);

    //    // Act
    //    var result = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "DisciplineCode");

    //    // Assert
    //    Assert.That(result, Is.Not.Null);
    //    Assert.That(result.DocumentId, Is.EqualTo(_testDocumentId1));
    //    Assert.That(result.PropertyName, Is.EqualTo("DisciplineCode"));
    //    Assert.That(result.PropertyValue, Is.EqualTo("ARCH"));
    //}

    //[Test]
    //public async Task GetPropertyAsync_NonExistentProperty_ReturnsNull()
    //{
    //    // Act
    //    var result = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "NonExistent");

    //    // Assert
    //    Assert.That(result, Is.Null);
    //}

    //[Test]
    //public async Task GetPropertyAsync_ExistingPropertyNameDifferentDocument_ReturnsNull()
    //{
    //    // Arrange
    //    var property = new CustomProperty(_testDocumentId1, "DisciplineCode", "ARCH");
    //    await _customPropertyRepository.InsertAsync(property);

    //    // Act
    //    var result = await _customPropertyRepository.GetPropertyAsync(_testDocumentId2, "DisciplineCode");

    //    // Assert
    //    Assert.That(result, Is.Null);
    //}

    //[Test]
    //public async Task InheritedMethods_WorkCorrectly()
    //{
    //    // Test that inherited methods from BaseRepository work correctly

    //    // Arrange
    //    var customProperty = new CustomProperty(_testDocumentId1, "TestProperty", "TestValue");

    //    // Act & Assert - Insert
    //    var insertResult = await _customPropertyRepository.InsertAsync(customProperty);
    //    Assert.That(insertResult, Is.EqualTo(1));
    //    Assert.That(customProperty.Id, Is.GreaterThan(0));

    //    // Act & Assert - GetById
    //    var retrieved = await _customPropertyRepository.GetByIdAsync(customProperty.Id);
    //    Assert.That(retrieved, Is.Not.Null);
    //    Assert.That(retrieved.PropertyName, Is.EqualTo("TestProperty"));

    //    // Act & Assert - Update
    //    retrieved.PropertyValue = "UpdatedValue";
    //    var updateResult = await _customPropertyRepository.UpdateAsync(retrieved);
    //    Assert.That(updateResult, Is.EqualTo(1));

    //    // Act & Assert - Find
    //    var found = await _customPropertyRepository.FindAsync(cp => cp.PropertyValue.Contains("Updated"));
    //    Assert.That(found, Has.Count.EqualTo(1));

    //    // Act & Assert - Count
    //    var count = await _customPropertyRepository.CountAsync();
    //    Assert.That(count, Is.EqualTo(1));

    //    // Act & Assert - Delete
    //    var deleteResult = await _customPropertyRepository.DeleteAsync(customProperty.Id);
    //    Assert.That(deleteResult, Is.EqualTo(1));
    //}

    //[Test]
    //public async Task BulkOperations_WorkCorrectly()
    //{
    //    // Test bulk operations inherited from BaseRepository

    //    // Arrange
    //    var properties = new[]
    //    {
    //        new CustomProperty(_testDocumentId1, "Property1", "Value1"),
    //        new CustomProperty(_testDocumentId1, "Property2", "Value2"),
    //        new CustomProperty(_testDocumentId2, "Property3", "Value3")
    //    };

    //    // Act & Assert - InsertAll
    //    var insertAllResult = await _customPropertyRepository.InsertAllAsync(properties);
    //    Assert.That(insertAllResult, Is.EqualTo(3));

    //    // Act & Assert - UpdateAll
    //    foreach (var prop in properties)
    //    {
    //        prop.PropertyValue = prop.PropertyValue + "_Updated";
    //    }
    //    var updateAllResult = await _customPropertyRepository.UpdateAllAsync(properties);
    //    Assert.That(updateAllResult, Is.EqualTo(3));

    //    // Verify updates
    //    var allProperties = await _customPropertyRepository.GetAllAsync();
    //    Assert.That(allProperties.All(p => p.PropertyValue.EndsWith("_Updated")), Is.True);

    //    // Act & Assert - DeleteAll
    //    var deleteAllResult = await _customPropertyRepository.DeleteAllAsync(properties);
    //    Assert.That(deleteAllResult, Is.EqualTo(3));

    //    // Verify deletion
    //    var finalCount = await _customPropertyRepository.CountAsync();
    //    Assert.That(finalCount, Is.EqualTo(0));
    //}

    //[Test]
    //public async Task ComplexQuery_UsingFindAsync_ReturnsCorrectResults()
    //{
    //    // Arrange
    //    var properties = new[]
    //    {
    //        new CustomProperty(_testDocumentId1, "DisciplineCode", "ARCH"),
    //        new CustomProperty(_testDocumentId1, "ProjectPhase", "Construction"),
    //        new CustomProperty(_testDocumentId2, "DisciplineCode", "MECH"),
    //        new CustomProperty(_testDocumentId2, "ProjectPhase", "Design")
    //    };

    //    foreach (var property in properties)
    //    {
    //        await _customPropertyRepository.InsertAsync(property);
    //    }

    //    // Act - Find all properties for document 1 with specific criteria
    //    var result = await _customPropertyRepository.FindAsync(
    //        cp => cp.DocumentId == _testDocumentId1 &&
    //              (cp.PropertyName == "DisciplineCode" || cp.PropertyValue.Contains("Construction")));

    //    // Assert
    //    Assert.That(result, Has.Count.EqualTo(2));
    //    Assert.That(result.All(p => p.DocumentId == _testDocumentId1), Is.True);
    //}
}