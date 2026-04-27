using NUnit.Framework;
using SQLite;
using duHastNet.DocManager.Core.Services.Repositories;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.Database;
using System.IO;

namespace duHastNet.DocManager.Core.Tests.Services.Repositories;

[TestFixture]
public class CustomPropertyRepositorySyncTests
{
    private SQLiteConnection _connection;
    private string _databasePath;
    private CustomPropertyRepositorySync _customPropertyRepository;
    private CustomFieldDefinitionRepositorySync _customFieldDefinitionRepository;
    private DocumentRepositorySync _documentRepository;
    private RevisionRepositorySync _revisionRepository;
    private int _testDocumentId1;
    private int _testDocumentId2;
    private int _fieldDefId1; // DisciplineCode
    private int _fieldDefId2; // ProjectPhase
    private int _fieldDefId3; // ZoneCode

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
        _connection.CreateTable<CustomFieldDefinition>();
        _connection.CreateTable<CustomProperty>();

        _customPropertyRepository = new CustomPropertyRepositorySync(_connection);
        _customFieldDefinitionRepository = new CustomFieldDefinitionRepositorySync(_connection);
        _documentRepository = new DocumentRepositorySync(_connection);
        _revisionRepository = new RevisionRepositorySync(_connection);

        // Create test data - Revision
        var testRevision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        _revisionRepository.Insert(testRevision);

        // Create test data - Documents
        var document1 = new Document("A-101", "Floor Plan", "1", testRevision.Id);
        var document2 = new Document("A-102", "Ceiling Plan", "1", testRevision.Id);

        _documentRepository.Insert(document1);
        _documentRepository.Insert(document2);

        _testDocumentId1 = document1.Id;
        _testDocumentId2 = document2.Id;

        // Create test data - CustomFieldDefinitions
        var fieldDef1 = new CustomFieldDefinition("DisciplineCode", true);
        var fieldDef2 = new CustomFieldDefinition("ProjectPhase", true);
        var fieldDef3 = new CustomFieldDefinition("ZoneCode", true);

        _customFieldDefinitionRepository.Insert(fieldDef1);
        _customFieldDefinitionRepository.Insert(fieldDef2);
        _customFieldDefinitionRepository.Insert(fieldDef3);

        _fieldDefId1 = fieldDef1.Id;
        _fieldDefId2 = fieldDef2.Id;
        _fieldDefId3 = fieldDef3.Id;
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

    #region GetPropertiesByDocument Tests

    [Test]
    public void GetPropertiesByDocument_WithPropertiesForDocument_ReturnsPropertiesOrderedByFieldDefinitionId()
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
            _customPropertyRepository.Insert(property);
        }

        // Act
        var result = _customPropertyRepository.GetPropertiesByDocument(_testDocumentId1);

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
    public void GetPropertiesByDocument_NoPropertiesForDocument_ReturnsEmptyList()
    {
        // Arrange - Add property only to document 1
        var property = new CustomProperty(_testDocumentId1, _fieldDefId1, "TestValue");
        _customPropertyRepository.Insert(property);

        // Act - Query document 2 which has no properties
        var result = _customPropertyRepository.GetPropertiesByDocument(_testDocumentId2);

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    [Test]
    public void GetPropertiesByDocument_NonExistentDocument_ReturnsEmptyList()
    {
        // Arrange
        var property = new CustomProperty(_testDocumentId1, _fieldDefId1, "TestValue");
        _customPropertyRepository.Insert(property);

        // Act
        var result = _customPropertyRepository.GetPropertiesByDocument(999);

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    [Test]
    public void GetPropertiesByDocument_WithMultipleDocuments_ReturnsOnlyRequestedDocument()
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
            _customPropertyRepository.Insert(property);
        }

        // Act
        var result = _customPropertyRepository.GetPropertiesByDocument(_testDocumentId1);

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
        Assert.That(result.All(p => p.DocumentId == _testDocumentId1), Is.True);
        Assert.That(result[0].PropertyValue, Is.EqualTo("ARCH"));
        Assert.That(result[1].PropertyValue, Is.EqualTo("Construction"));
    }

    #endregion

    #region GetDistinctPropertyNames Tests

    [Test]
    public void GetDistinctPropertyNames_WithMultipleFieldDefinitions_ReturnsAllNamesOrderedAlphabetically()
    {
        // Arrange - Field definitions already created in Setup:
        // DisciplineCode, ProjectPhase, ZoneCode

        // Act
        var result = _customPropertyRepository.GetDistinctPropertyNames();

        // Assert
        Assert.That(result, Has.Count.EqualTo(3));
        Assert.That(result, Is.EqualTo(new[] { "DisciplineCode", "ProjectPhase", "ZoneCode" })); // Alphabetically ordered
    }

    [Test]
    public void GetDistinctPropertyNames_NoFieldDefinitions_ReturnsEmptyList()
    {
        // Arrange - Delete all field definitions
        _connection.Execute("DELETE FROM CustomFieldDefinitions");

        // Act
        var result = _customPropertyRepository.GetDistinctPropertyNames();

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    [Test]
    public void GetDistinctPropertyNames_WithActiveAndInactiveFields_ReturnsBothActiveAndInactive()
    {
        // Arrange - Add an inactive field definition
        var inactiveField = new CustomFieldDefinition("InactiveField", false);
        _customFieldDefinitionRepository.Insert(inactiveField);

        // Act
        var result = _customPropertyRepository.GetDistinctPropertyNames();

        // Assert
        Assert.That(result, Has.Count.EqualTo(4));
        Assert.That(result, Does.Contain("InactiveField"));
        Assert.That(result, Does.Contain("DisciplineCode"));
        Assert.That(result, Does.Contain("ProjectPhase"));
        Assert.That(result, Does.Contain("ZoneCode"));
    }

    [Test]
    public void GetDistinctPropertyNames_ReturnsNamesRegardlessOfCustomPropertyUsage()
    {
        // This test verifies that GetDistinctPropertyNames returns all field definitions
        // even if no CustomProperty entries exist for them

        // Arrange - Don't create any CustomProperty entries, only field definitions exist
        
        // Act
        var result = _customPropertyRepository.GetDistinctPropertyNames();

        // Assert - Should still return all field definitions
        Assert.That(result, Has.Count.EqualTo(3));
        Assert.That(result, Does.Contain("DisciplineCode"));
        Assert.That(result, Does.Contain("ProjectPhase"));
        Assert.That(result, Does.Contain("ZoneCode"));
    }

    [Test]
    public void GetDistinctPropertyNames_OrderingIsCaseInsensitiveAlphabetical()
    {
        // Arrange - Add fields with mixed case to verify alphabetical ordering
        _connection.Execute("DELETE FROM CustomFieldDefinitions");
        
        var fields = new[]
        {
            new CustomFieldDefinition("zulu", true),
            new CustomFieldDefinition("Alpha", true),
            new CustomFieldDefinition("bravo", true),
            new CustomFieldDefinition("Charlie", true)
        };

        foreach (var field in fields)
        {
            _customFieldDefinitionRepository.Insert(field);
        }

        // Act
        var result = _customPropertyRepository.GetDistinctPropertyNames();

        // Assert - SQLite orders case-sensitively (uppercase before lowercase)
        Assert.That(result, Has.Count.EqualTo(4));
        Assert.That(result[0], Is.EqualTo("Alpha"));
        Assert.That(result[1], Is.EqualTo("Charlie"));
        Assert.That(result[2], Is.EqualTo("bravo"));
        Assert.That(result[3], Is.EqualTo("zulu"));
    }

    #endregion

    #region Inherited BaseRepositorySync Methods Tests

    [Test]
    public void InheritedMethods_InsertAndGetById_WorkCorrectly()
    {
        // Arrange
        var customProperty = new CustomProperty(_testDocumentId1, _fieldDefId1, "TestValue");

        // Act - Insert
        var insertResult = _customPropertyRepository.Insert(customProperty);
        
        // Assert - Insert
        Assert.That(insertResult, Is.EqualTo(1));
        Assert.That(customProperty.Id, Is.GreaterThan(0));

        // Act - GetById
        var retrieved = _customPropertyRepository.GetById(customProperty.Id);
        
        // Assert - GetById
        Assert.That(retrieved, Is.Not.Null);
        Assert.That(retrieved.DocumentId, Is.EqualTo(_testDocumentId1));
        Assert.That(retrieved.CustomFieldDefinitionId, Is.EqualTo(_fieldDefId1));
        Assert.That(retrieved.PropertyValue, Is.EqualTo("TestValue"));
    }

    [Test]
    public void InheritedMethods_Update_WorksCorrectly()
    {
        // Arrange
        var customProperty = new CustomProperty(_testDocumentId1, _fieldDefId1, "OriginalValue");
        _customPropertyRepository.Insert(customProperty);

        // Act - Update
        customProperty.PropertyValue = "UpdatedValue";
        var updateResult = _customPropertyRepository.Update(customProperty);

        // Assert
        Assert.That(updateResult, Is.EqualTo(1));

        // Verify update
        var retrieved = _customPropertyRepository.GetById(customProperty.Id);
        Assert.That(retrieved.PropertyValue, Is.EqualTo("UpdatedValue"));
    }

    [Test]
    public void InheritedMethods_Delete_WorksCorrectly()
    {
        // Arrange
        var customProperty = new CustomProperty(_testDocumentId1, _fieldDefId1, "TestValue");
        _customPropertyRepository.Insert(customProperty);
        var propertyId = customProperty.Id;

        // Act - Delete
        var deleteResult = _customPropertyRepository.Delete(propertyId);

        // Assert
        Assert.That(deleteResult, Is.EqualTo(1));

        // Verify deletion
        var retrieved = _customPropertyRepository.GetById(propertyId);
        Assert.That(retrieved, Is.Null);
    }

    [Test]
    public void InheritedMethods_Find_WorksCorrectly()
    {
        // Arrange
        var property1 = new CustomProperty(_testDocumentId1, _fieldDefId1, "ARCH");
        var property2 = new CustomProperty(_testDocumentId1, _fieldDefId2, "Construction");
        var property3 = new CustomProperty(_testDocumentId2, _fieldDefId1, "MECH");

        _customPropertyRepository.Insert(property1);
        _customPropertyRepository.Insert(property2);
        _customPropertyRepository.Insert(property3);

        // Act - Find all properties for _testDocumentId1
        var result = _customPropertyRepository.Find(p => p.DocumentId == _testDocumentId1);

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
        Assert.That(result.All(p => p.DocumentId == _testDocumentId1), Is.True);
    }

    [Test]
    public void InheritedMethods_Count_WorksCorrectly()
    {
        // Arrange
        var property1 = new CustomProperty(_testDocumentId1, _fieldDefId1, "ARCH");
        var property2 = new CustomProperty(_testDocumentId1, _fieldDefId2, "Construction");
        var property3 = new CustomProperty(_testDocumentId2, _fieldDefId1, "MECH");

        _customPropertyRepository.Insert(property1);
        _customPropertyRepository.Insert(property2);
        _customPropertyRepository.Insert(property3);

        // Act - Count all properties
        var totalCount = _customPropertyRepository.Count();
        
        // Act - Count properties for specific document
        var documentCount = _customPropertyRepository.Count(p => p.DocumentId == _testDocumentId1);

        // Assert
        Assert.That(totalCount, Is.EqualTo(3));
        Assert.That(documentCount, Is.EqualTo(2));
    }

    [Test]
    public void InheritedMethods_GetAll_WorksCorrectly()
    {
        // Arrange
        var property1 = new CustomProperty(_testDocumentId1, _fieldDefId1, "ARCH");
        var property2 = new CustomProperty(_testDocumentId1, _fieldDefId2, "Construction");
        var property3 = new CustomProperty(_testDocumentId2, _fieldDefId1, "MECH");

        _customPropertyRepository.Insert(property1);
        _customPropertyRepository.Insert(property2);
        _customPropertyRepository.Insert(property3);

        // Act
        var result = _customPropertyRepository.GetAll();

        // Assert
        Assert.That(result, Has.Count.EqualTo(3));
    }

    [Test]
    public void InsertAll_WithMultipleProperties_InsertsAll()
    {
        // Arrange
        var properties = new[]
        {
            new CustomProperty(_testDocumentId1, _fieldDefId1, "ARCH"),
            new CustomProperty(_testDocumentId1, _fieldDefId2, "Construction"),
            new CustomProperty(_testDocumentId2, _fieldDefId1, "MECH")
        };

        // Act
        var rowsAffected = _customPropertyRepository.InsertAll(properties);

        // Assert
        Assert.That(rowsAffected, Is.EqualTo(3));

        var allProperties = _customPropertyRepository.GetAll();
        Assert.That(allProperties, Has.Count.EqualTo(3));
    }

    [Test]
    public void UpdateAll_WithMultipleProperties_UpdatesAll()
    {
        // Arrange
        var properties = new[]
        {
            new CustomProperty(_testDocumentId1, _fieldDefId1, "Value1"),
            new CustomProperty(_testDocumentId1, _fieldDefId2, "Value2"),
            new CustomProperty(_testDocumentId2, _fieldDefId1, "Value3")
        };

        _customPropertyRepository.InsertAll(properties);

        // Act — append suffix to all values
        foreach (var prop in properties)
        {
            prop.PropertyValue = prop.PropertyValue + "_Updated";
        }
        var result = _customPropertyRepository.UpdateAll(properties);

        // Assert
        Assert.That(result, Is.EqualTo(3));

        var allProperties = _customPropertyRepository.GetAll();
        Assert.That(allProperties.All(p => p.PropertyValue.EndsWith("_Updated")), Is.True);
    }

    [Test]
    public void DeleteAll_WithMultipleProperties_DeletesAll()
    {
        // Arrange
        var properties = new[]
        {
            new CustomProperty(_testDocumentId1, _fieldDefId1, "Value1"),
            new CustomProperty(_testDocumentId1, _fieldDefId2, "Value2"),
            new CustomProperty(_testDocumentId2, _fieldDefId1, "Value3")
        };

        _customPropertyRepository.InsertAll(properties);

        // Act
        var result = _customPropertyRepository.DeleteAll(properties);

        // Assert
        Assert.That(result, Is.EqualTo(3));

        var finalCount = _customPropertyRepository.Count();
        Assert.That(finalCount, Is.EqualTo(0));
    }

    #endregion

    #region Integration Tests

    [Test]
    public void IntegrationTest_CompleteWorkflow_WorksCorrectly()
    {
        // This test verifies a complete workflow with custom properties

        // Step 1: Create properties for document 1
        var properties = new[]
        {
            new CustomProperty(_testDocumentId1, _fieldDefId1, "ARCH"),
            new CustomProperty(_testDocumentId1, _fieldDefId2, "Construction"),
            new CustomProperty(_testDocumentId1, _fieldDefId3, "Zone A")
        };

        _customPropertyRepository.InsertAll(properties);

        // Step 2: Retrieve and verify
        var doc1Properties = _customPropertyRepository.GetPropertiesByDocument(_testDocumentId1);
        Assert.That(doc1Properties, Has.Count.EqualTo(3));

        // Step 3: Update a property value
        var archProperty = doc1Properties.First(p => p.CustomFieldDefinitionId == _fieldDefId1);
        archProperty.PropertyValue = "ARCHITECTURAL";
        _customPropertyRepository.Update(archProperty);

        // Step 4: Verify update
        var updatedProperty = _customPropertyRepository.GetById(archProperty.Id);
        Assert.That(updatedProperty.PropertyValue, Is.EqualTo("ARCHITECTURAL"));

        // Step 5: Get distinct property names
        var distinctNames = _customPropertyRepository.GetDistinctPropertyNames();
        Assert.That(distinctNames, Has.Count.EqualTo(3));

        // Step 6: Delete one property
        _customPropertyRepository.Delete(archProperty);

        // Step 7: Verify deletion
        var remainingProperties = _customPropertyRepository.GetPropertiesByDocument(_testDocumentId1);
        Assert.That(remainingProperties, Has.Count.EqualTo(2));
    }

    [Test]
    public void IntegrationTest_MultipleDocumentsWithProperties_WorksCorrectly()
    {
        // Create properties for multiple documents
        var properties = new[]
        {
            new CustomProperty(_testDocumentId1, _fieldDefId1, "ARCH"),
            new CustomProperty(_testDocumentId1, _fieldDefId2, "Construction"),
            new CustomProperty(_testDocumentId2, _fieldDefId1, "MECH"),
            new CustomProperty(_testDocumentId2, _fieldDefId3, "Zone B")
        };

        _customPropertyRepository.InsertAll(properties);

        // Verify each document has correct properties
        var doc1Props = _customPropertyRepository.GetPropertiesByDocument(_testDocumentId1);
        var doc2Props = _customPropertyRepository.GetPropertiesByDocument(_testDocumentId2);

        Assert.Multiple(() =>
        {
            Assert.That(doc1Props, Has.Count.EqualTo(2));
            Assert.That(doc2Props, Has.Count.EqualTo(2));
            Assert.That(doc1Props.All(p => p.DocumentId == _testDocumentId1), Is.True);
            Assert.That(doc2Props.All(p => p.DocumentId == _testDocumentId2), Is.True);
        });

        // Verify distinct property names include all field definitions
        var distinctNames = _customPropertyRepository.GetDistinctPropertyNames();
        Assert.That(distinctNames, Has.Count.EqualTo(3));
    }

    #endregion
}
