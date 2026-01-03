using NUnit.Framework;
using SQLite;
using duHastNet.DocManager.Core.Services.Repositories;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.Database;
using System.IO;

namespace duHastNet.DocManager.Core.Tests.Services.Repositories;

[TestFixture]
public class CustomPropertyRepositoryTests
{
    private SQLiteAsyncConnection _connection;
    private string _databasePath;
    private CustomPropertyRepository _customPropertyRepository;
    private CustomFieldDefinitionRepository _customFieldDefinitionRepository;
    private DocumentRepository _documentRepository;
    private RevisionRepository _revisionRepository;
    private int _testDocumentId1;
    private int _testDocumentId2;
    private int _fieldDefId1; // DisciplineCode
    private int _fieldDefId2; // ProjectPhase
    private int _fieldDefId3; // ZoneCode

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
        await _connection.CreateTableAsync<CustomFieldDefinition>();
        await _connection.CreateTableAsync<CustomProperty>();

        _customPropertyRepository = new CustomPropertyRepository(_connection);
        _customFieldDefinitionRepository = new CustomFieldDefinitionRepository(_connection);
        _documentRepository = new DocumentRepository(_connection);
        _revisionRepository = new RevisionRepository(_connection);

        // Create test data - Revision
        var testRevision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        await _revisionRepository.InsertAsync(testRevision);

        // Create test data - Documents
        var document1 = new Document("A-101", "Floor Plan", "1", testRevision.Id);
        var document2 = new Document("A-102", "Ceiling Plan", "1", testRevision.Id);

        await _documentRepository.InsertAsync(document1);
        await _documentRepository.InsertAsync(document2);

        _testDocumentId1 = document1.Id;
        _testDocumentId2 = document2.Id;

        // Create test data - CustomFieldDefinitions
        var fieldDef1 = new CustomFieldDefinition("DisciplineCode", true);
        var fieldDef2 = new CustomFieldDefinition("ProjectPhase", true);
        var fieldDef3 = new CustomFieldDefinition("ZoneCode", true);

        await _customFieldDefinitionRepository.InsertAsync(fieldDef1);
        await _customFieldDefinitionRepository.InsertAsync(fieldDef2);
        await _customFieldDefinitionRepository.InsertAsync(fieldDef3);

        _fieldDefId1 = fieldDef1.Id;
        _fieldDefId2 = fieldDef2.Id;
        _fieldDefId3 = fieldDef3.Id;
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

    #region GetPropertiesByDocumentAsync Tests

    [Test]
    public async Task GetPropertiesByDocumentAsync_WithPropertiesForDocument_ReturnsPropertiesOrderedByFieldDefinitionId()
    {
        // Arrange - Create properties in non-sequential order
        var properties = new[]
        {
            new CustomProperty(_testDocumentId1, _fieldDefId3, "Zone A"),      // ZoneCode (fieldDefId3)
            new CustomProperty(_testDocumentId1, _fieldDefId1, "ARCH"),        // DisciplineCode (fieldDefId1)
            new CustomProperty(_testDocumentId1, _fieldDefId2, "Construction"), // ProjectPhase (fieldDefId2)
            new CustomProperty(_testDocumentId2, _fieldDefId1, "MECH")         // Different document
        };

        foreach (var property in properties)
        {
            await _customPropertyRepository.InsertAsync(property);
        }

        // Act
        var result = await _customPropertyRepository.GetPropertiesByDocumentAsync(_testDocumentId1);

        // Assert
        Assert.That(result, Has.Count.EqualTo(3));
        Assert.That(result.All(p => p.DocumentId == _testDocumentId1), Is.True);
        
        // Should be ordered by CustomFieldDefinitionId
        Assert.That(result[0].CustomFieldDefinitionId, Is.EqualTo(_fieldDefId1));
        Assert.That(result[1].CustomFieldDefinitionId, Is.EqualTo(_fieldDefId2));
        Assert.That(result[2].CustomFieldDefinitionId, Is.EqualTo(_fieldDefId3));
        
        // Verify values
        Assert.That(result[0].PropertyValue, Is.EqualTo("ARCH"));
        Assert.That(result[1].PropertyValue, Is.EqualTo("Construction"));
        Assert.That(result[2].PropertyValue, Is.EqualTo("Zone A"));
    }

    [Test]
    public async Task GetPropertiesByDocumentAsync_NoPropertiesForDocument_ReturnsEmptyList()
    {
        // Arrange - Add property only to document 1
        var property = new CustomProperty(_testDocumentId1, _fieldDefId1, "TestValue");
        await _customPropertyRepository.InsertAsync(property);

        // Act - Query document 2 which has no properties
        var result = await _customPropertyRepository.GetPropertiesByDocumentAsync(_testDocumentId2);

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    [Test]
    public async Task GetPropertiesByDocumentAsync_NonExistentDocument_ReturnsEmptyList()
    {
        // Arrange
        var property = new CustomProperty(_testDocumentId1, _fieldDefId1, "TestValue");
        await _customPropertyRepository.InsertAsync(property);

        // Act
        var result = await _customPropertyRepository.GetPropertiesByDocumentAsync(999);

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    [Test]
    public async Task GetPropertiesByDocumentAsync_WithMultipleDocuments_ReturnsOnlyRequestedDocument()
    {
        // Arrange
        var properties = new[]
        {
            new CustomProperty(_testDocumentId1, _fieldDefId1, "ARCH"),
            new CustomProperty(_testDocumentId1, _fieldDefId2, "Construction"),
            new CustomProperty(_testDocumentId2, _fieldDefId1, "MECH"),
            new CustomProperty(_testDocumentId2, _fieldDefId2, "Design")
        };

        foreach (var property in properties)
        {
            await _customPropertyRepository.InsertAsync(property);
        }

        // Act
        var result = await _customPropertyRepository.GetPropertiesByDocumentAsync(_testDocumentId1);

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
        Assert.That(result.All(p => p.DocumentId == _testDocumentId1), Is.True);
        Assert.That(result[0].PropertyValue, Is.EqualTo("ARCH"));
        Assert.That(result[1].PropertyValue, Is.EqualTo("Construction"));
    }

    #endregion

    #region GetDistinctPropertyNamesAsync Tests

    [Test]
    public async Task GetDistinctPropertyNamesAsync_WithMultipleFieldDefinitions_ReturnsAllNamesOrderedAlphabetically()
    {
        // Arrange - Field definitions already created in Setup:
        // DisciplineCode, ProjectPhase, ZoneCode

        // Act
        var result = await _customPropertyRepository.GetDistinctPropertyNamesAsync();

        // Assert
        Assert.That(result, Has.Count.EqualTo(3));
        Assert.That(result, Is.EqualTo(new[] { "DisciplineCode", "ProjectPhase", "ZoneCode" })); // Alphabetically ordered
    }

    [Test]
    public async Task GetDistinctPropertyNamesAsync_NoFieldDefinitions_ReturnsEmptyList()
    {
        // Arrange - Delete all field definitions
        await _connection.ExecuteAsync("DELETE FROM CustomFieldDefinitions");

        // Act
        var result = await _customPropertyRepository.GetDistinctPropertyNamesAsync();

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    [Test]
    public async Task GetDistinctPropertyNamesAsync_WithActiveAndInactiveFields_ReturnsBothActiveAndInactive()
    {
        // Arrange - Add an inactive field definition
        var inactiveField = new CustomFieldDefinition("InactiveField", false);
        await _customFieldDefinitionRepository.InsertAsync(inactiveField);

        // Act
        var result = await _customPropertyRepository.GetDistinctPropertyNamesAsync();

        // Assert
        Assert.That(result, Has.Count.EqualTo(4));
        Assert.That(result, Does.Contain("InactiveField"));
        Assert.That(result, Does.Contain("DisciplineCode"));
        Assert.That(result, Does.Contain("ProjectPhase"));
        Assert.That(result, Does.Contain("ZoneCode"));
    }

    [Test]
    public async Task GetDistinctPropertyNamesAsync_ReturnsNamesRegardlessOfCustomPropertyUsage()
    {
        // This test verifies that GetDistinctPropertyNamesAsync returns all field definitions
        // even if no CustomProperty entries exist for them

        // Arrange - Don't create any CustomProperty entries, only field definitions exist
        
        // Act
        var result = await _customPropertyRepository.GetDistinctPropertyNamesAsync();

        // Assert - Should still return all field definitions
        Assert.That(result, Has.Count.EqualTo(3));
        Assert.That(result, Does.Contain("DisciplineCode"));
        Assert.That(result, Does.Contain("ProjectPhase"));
        Assert.That(result, Does.Contain("ZoneCode"));
    }

    [Test]
    public async Task GetDistinctPropertyNamesAsync_OrderingIsCaseInsensitiveAlphabetical()
    {
        // Arrange - Add fields with mixed case to verify alphabetical ordering
        await _connection.ExecuteAsync("DELETE FROM CustomFieldDefinitions");
        
        var fields = new[]
        {
            new CustomFieldDefinition("zulu", true),
            new CustomFieldDefinition("Alpha", true),
            new CustomFieldDefinition("bravo", true),
            new CustomFieldDefinition("Charlie", true)
        };

        foreach (var field in fields)
        {
            await _customFieldDefinitionRepository.InsertAsync(field);
        }

        // Act
        var result = await _customPropertyRepository.GetDistinctPropertyNamesAsync();

        // Assert - SQLite orders case-sensitively (uppercase before lowercase)
        Assert.That(result, Has.Count.EqualTo(4));
        Assert.That(result[0], Is.EqualTo("Alpha"));
        Assert.That(result[1], Is.EqualTo("Charlie"));
        Assert.That(result[2], Is.EqualTo("bravo"));
        Assert.That(result[3], Is.EqualTo("zulu"));
    }

    #endregion

    #region Inherited BaseRepository Methods Tests

    [Test]
    public async Task InheritedMethods_InsertAndGetById_WorkCorrectly()
    {
        // Arrange
        var customProperty = new CustomProperty(_testDocumentId1, _fieldDefId1, "TestValue");

        // Act - Insert
        var insertResult = await _customPropertyRepository.InsertAsync(customProperty);
        
        // Assert - Insert
        Assert.That(insertResult, Is.EqualTo(1));
        Assert.That(customProperty.Id, Is.GreaterThan(0));

        // Act - GetById
        var retrieved = await _customPropertyRepository.GetByIdAsync(customProperty.Id);
        
        // Assert - GetById
        Assert.That(retrieved, Is.Not.Null);
        Assert.That(retrieved.DocumentId, Is.EqualTo(_testDocumentId1));
        Assert.That(retrieved.CustomFieldDefinitionId, Is.EqualTo(_fieldDefId1));
        Assert.That(retrieved.PropertyValue, Is.EqualTo("TestValue"));
    }

    [Test]
    public async Task InheritedMethods_Update_WorksCorrectly()
    {
        // Arrange
        var customProperty = new CustomProperty(_testDocumentId1, _fieldDefId1, "OriginalValue");
        await _customPropertyRepository.InsertAsync(customProperty);

        // Act - Update
        customProperty.PropertyValue = "UpdatedValue";
        var updateResult = await _customPropertyRepository.UpdateAsync(customProperty);

        // Assert
        Assert.That(updateResult, Is.EqualTo(1));

        // Verify update
        var retrieved = await _customPropertyRepository.GetByIdAsync(customProperty.Id);
        Assert.That(retrieved.PropertyValue, Is.EqualTo("UpdatedValue"));
    }

    [Test]
    public async Task InheritedMethods_Delete_WorksCorrectly()
    {
        // Arrange
        var customProperty = new CustomProperty(_testDocumentId1, _fieldDefId1, "TestValue");
        await _customPropertyRepository.InsertAsync(customProperty);
        var propertyId = customProperty.Id;

        // Act - Delete
        var deleteResult = await _customPropertyRepository.DeleteAsync(propertyId);

        // Assert
        Assert.That(deleteResult, Is.EqualTo(1));

        // Verify deletion
        var retrieved = await _customPropertyRepository.GetByIdAsync(propertyId);
        Assert.That(retrieved, Is.Null);
    }

    [Test]
    public async Task InheritedMethods_Find_WorksCorrectly()
    {
        // Arrange
        var properties = new[]
        {
            new CustomProperty(_testDocumentId1, _fieldDefId1, "ARCH"),
            new CustomProperty(_testDocumentId1, _fieldDefId2, "Construction"),
            new CustomProperty(_testDocumentId2, _fieldDefId1, "MECH")
        };

        foreach (var property in properties)
        {
            await _customPropertyRepository.InsertAsync(property);
        }

        // Act - Find properties with value containing "ARCH"
        var found = await _customPropertyRepository.FindAsync(cp => cp.PropertyValue.Contains("ARCH"));

        // Assert
        Assert.That(found, Has.Count.EqualTo(1));
        Assert.That(found[0].PropertyValue, Is.EqualTo("ARCH"));
    }

    [Test]
    public async Task InheritedMethods_Count_WorksCorrectly()
    {
        // Arrange
        var properties = new[]
        {
            new CustomProperty(_testDocumentId1, _fieldDefId1, "Value1"),
            new CustomProperty(_testDocumentId1, _fieldDefId2, "Value2"),
            new CustomProperty(_testDocumentId2, _fieldDefId1, "Value3")
        };

        foreach (var property in properties)
        {
            await _customPropertyRepository.InsertAsync(property);
        }

        // Act
        var count = await _customPropertyRepository.CountAsync();

        // Assert
        Assert.That(count, Is.EqualTo(3));
    }

    [Test]
    public async Task InheritedMethods_GetAll_WorksCorrectly()
    {
        // Arrange
        var properties = new[]
        {
            new CustomProperty(_testDocumentId1, _fieldDefId1, "Value1"),
            new CustomProperty(_testDocumentId1, _fieldDefId2, "Value2"),
            new CustomProperty(_testDocumentId2, _fieldDefId1, "Value3")
        };

        foreach (var property in properties)
        {
            await _customPropertyRepository.InsertAsync(property);
        }

        // Act
        var allProperties = await _customPropertyRepository.GetAllAsync();

        // Assert
        Assert.That(allProperties, Has.Count.EqualTo(3));
    }

    #endregion

    #region Bulk Operations Tests

    [Test]
    public async Task BulkOperations_InsertAll_WorksCorrectly()
    {
        // Arrange
        var properties = new[]
        {
            new CustomProperty(_testDocumentId1, _fieldDefId1, "Value1"),
            new CustomProperty(_testDocumentId1, _fieldDefId2, "Value2"),
            new CustomProperty(_testDocumentId2, _fieldDefId1, "Value3")
        };

        // Act
        var insertAllResult = await _customPropertyRepository.InsertAllAsync(properties);

        // Assert
        Assert.That(insertAllResult, Is.EqualTo(3));

        // Verify all were inserted
        var count = await _customPropertyRepository.CountAsync();
        Assert.That(count, Is.EqualTo(3));
    }

    [Test]
    public async Task BulkOperations_UpdateAll_WorksCorrectly()
    {
        // Arrange
        var properties = new[]
        {
            new CustomProperty(_testDocumentId1, _fieldDefId1, "Value1"),
            new CustomProperty(_testDocumentId1, _fieldDefId2, "Value2"),
            new CustomProperty(_testDocumentId2, _fieldDefId1, "Value3")
        };

        await _customPropertyRepository.InsertAllAsync(properties);

        // Act - Update all
        foreach (var prop in properties)
        {
            prop.PropertyValue = prop.PropertyValue + "_Updated";
        }
        var updateAllResult = await _customPropertyRepository.UpdateAllAsync(properties);

        // Assert
        Assert.That(updateAllResult, Is.EqualTo(3));

        // Verify updates
        var allProperties = await _customPropertyRepository.GetAllAsync();
        Assert.That(allProperties.All(p => p.PropertyValue.EndsWith("_Updated")), Is.True);
    }

    [Test]
    public async Task BulkOperations_DeleteAll_WorksCorrectly()
    {
        // Arrange
        var properties = new[]
        {
            new CustomProperty(_testDocumentId1, _fieldDefId1, "Value1"),
            new CustomProperty(_testDocumentId1, _fieldDefId2, "Value2"),
            new CustomProperty(_testDocumentId2, _fieldDefId1, "Value3")
        };

        await _customPropertyRepository.InsertAllAsync(properties);

        // Act
        var deleteAllResult = await _customPropertyRepository.DeleteAllAsync(properties);

        // Assert
        Assert.That(deleteAllResult, Is.EqualTo(3));

        // Verify deletion
        var finalCount = await _customPropertyRepository.CountAsync();
        Assert.That(finalCount, Is.EqualTo(0));
    }

    #endregion

    #region Integration Tests

    [Test]
    public async Task IntegrationTest_CompleteWorkflow_WorksCorrectly()
    {
        // This test verifies a complete workflow:
        // 1. Create field definitions
        // 2. Create properties for documents
        // 3. Query properties by document
        // 4. Update property values
        // 5. Query again to verify updates

        // Arrange - Create additional field definition
        var newFieldDef = new CustomFieldDefinition("DrawingSize", true);
        await _customFieldDefinitionRepository.InsertAsync(newFieldDef);

        // Act 1 - Create properties for document 1
        var properties = new[]
        {
            new CustomProperty(_testDocumentId1, _fieldDefId1, "ARCH"),
            new CustomProperty(_testDocumentId1, _fieldDefId2, "Design"),
            new CustomProperty(_testDocumentId1, newFieldDef.Id, "A1")
        };

        await _customPropertyRepository.InsertAllAsync(properties);

        // Assert 1 - Verify properties were created
        var doc1Properties = await _customPropertyRepository.GetPropertiesByDocumentAsync(_testDocumentId1);
        Assert.That(doc1Properties, Has.Count.EqualTo(3));

        // Act 2 - Update a property value
        properties[1].PropertyValue = "Construction";
        await _customPropertyRepository.UpdateAsync(properties[1]);

        // Assert 2 - Verify update
        var updatedProperties = await _customPropertyRepository.GetPropertiesByDocumentAsync(_testDocumentId1);
        var phaseProperty = updatedProperties.FirstOrDefault(p => p.CustomFieldDefinitionId == _fieldDefId2);
        Assert.That(phaseProperty, Is.Not.Null);
        Assert.That(phaseProperty.PropertyValue, Is.EqualTo("Construction"));

        // Act 3 - Verify distinct property names includes new field
        var distinctNames = await _customPropertyRepository.GetDistinctPropertyNamesAsync();
        Assert.That(distinctNames, Has.Count.EqualTo(4));
        Assert.That(distinctNames, Does.Contain("DrawingSize"));
    }

    #endregion
}
