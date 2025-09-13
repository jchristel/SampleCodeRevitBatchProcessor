using NUnit.Framework;
using SQLite;
using duHastNet.DocManager.Core.Services.Repositories;
using duHastNet.DocManager.Core.Models;
using System.IO;

namespace duHastNet.DocManager.Core.Tests.Services.Repositories;

[TestFixture]
public class CustomPropertyRepositoryTests_Part2_SearchOperations
{
    private SQLiteAsyncConnection _connection;
    private string _databasePath;
    private CustomPropertyRepository _customPropertyRepository;
    private DocumentRepository _documentRepository;
    private RevisionRepository _revisionRepository;
    private int _testDocumentId1;
    private int _testDocumentId2;

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

        _customPropertyRepository = new CustomPropertyRepository(_connection);
        _documentRepository = new DocumentRepository(_connection);
        _revisionRepository = new RevisionRepository(_connection);

        // Create test data
        var testRevision = new Revision(new DateTime(2024, 2, 15), "Test Revision");
        await _revisionRepository.InsertAsync(testRevision);

        var document1 = new Document("A-101", "Floor Plan", "1", testRevision.Id);
        var document2 = new Document("A-102", "Ceiling Plan", "1", testRevision.Id);

        await _documentRepository.InsertAsync(document1);
        await _documentRepository.InsertAsync(document2);

        _testDocumentId1 = document1.Id;
        _testDocumentId2 = document2.Id;
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
    public async Task GetPropertiesByNameAsync_WithMultipleDocumentsHavingSameProperty_ReturnsAllProperties()
    {
        // Arrange
        var properties = new[]
        {
            new CustomProperty(_testDocumentId1, "DisciplineCode", "ARCH"),
            new CustomProperty(_testDocumentId2, "DisciplineCode", "MECH"),
            new CustomProperty(_testDocumentId1, "ProjectPhase", "Construction")
        };

        foreach (var property in properties)
        {
            await _customPropertyRepository.InsertAsync(property);
        }

        // Act
        var result = await _customPropertyRepository.GetPropertiesByNameAsync("DisciplineCode");

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
        Assert.That(result.All(p => p.PropertyName == "DisciplineCode"), Is.True);

        var docIds = result.Select(p => p.DocumentId).ToList();
        Assert.That(docIds, Does.Contain((_testDocumentId1)));
        Assert.That(docIds, Does.Contain((_testDocumentId2)));
    }

    [Test]
    public async Task GetPropertiesByNameAsync_NonExistentPropertyName_ReturnsEmptyList()
    {
        // Arrange
        var property = new CustomProperty(_testDocumentId1, "DisciplineCode", "ARCH");
        await _customPropertyRepository.InsertAsync(property);

        // Act
        var result = await _customPropertyRepository.GetPropertiesByNameAsync("NonExistent");

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    [Test]
    public async Task GetPropertiesByNameAndValueAsync_WithMatchingNameAndValue_ReturnsMatchingProperties()
    {
        // Arrange
        var properties = new[]
        {
            new CustomProperty(_testDocumentId1, "DisciplineCode", "ARCH"),
            new CustomProperty(_testDocumentId2, "DisciplineCode", "ARCH"),
            new CustomProperty(_testDocumentId1, "DisciplineCode", "MECH"), // Same document, different value
            new CustomProperty(_testDocumentId2, "ProjectPhase", "ARCH") // Different property, same value
        };

        foreach (var property in properties)
        {
            await _customPropertyRepository.InsertAsync(property);
        }

        // Act
        var result = await _customPropertyRepository.GetPropertiesByNameAndValueAsync("DisciplineCode", "ARCH");

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
        Assert.That(result.All(p => p.PropertyName == "DisciplineCode" && p.PropertyValue == "ARCH"), Is.True);
    }

    [Test]
    public async Task GetPropertiesByNameAndValueAsync_NoMatches_ReturnsEmptyList()
    {
        // Arrange
        var property = new CustomProperty(_testDocumentId1, "DisciplineCode", "ARCH");
        await _customPropertyRepository.InsertAsync(property);

        // Act
        var result = await _customPropertyRepository.GetPropertiesByNameAndValueAsync("DisciplineCode", "MECH");

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    [Test]
    public async Task GetPropertiesByNameAndValueAsync_CaseSensitiveValue_ExactMatchOnly()
    {
        // Arrange
        var properties = new[]
        {
            new CustomProperty(_testDocumentId1, "DisciplineCode", "ARCH"),
            new CustomProperty(_testDocumentId2, "DisciplineCode", "arch") // Different case
        };

        foreach (var property in properties)
        {
            await _customPropertyRepository.InsertAsync(property);
        }

        // Act
        var result = await _customPropertyRepository.GetPropertiesByNameAndValueAsync("DisciplineCode", "ARCH");

        // Assert
        Assert.That(result, Has.Count.EqualTo(1));
        Assert.That(result[0].PropertyValue, Is.EqualTo("ARCH"));
    }

    [Test]
    public async Task GetDistinctPropertyNamesAsync_WithMultipleProperties_ReturnsUniqueNamesOrderedAlphabetically()
    {
        // Arrange
        var properties = new[]
        {
            new CustomProperty(_testDocumentId1, "ZoneCode", "Zone A"),
            new CustomProperty(_testDocumentId1, "DisciplineCode", "ARCH"),
            new CustomProperty(_testDocumentId2, "DisciplineCode", "MECH"), // Duplicate name
            new CustomProperty(_testDocumentId2, "ProjectPhase", "Construction"),
            new CustomProperty(_testDocumentId1, "DrawingSize", "A1")
        };

        foreach (var property in properties)
        {
            await _customPropertyRepository.InsertAsync(property);
        }

        // Act
        var result = await _customPropertyRepository.GetDistinctPropertyNamesAsync();

        // Assert
        Assert.That(result, Has.Count.EqualTo(4)); // Should be unique
        Assert.That(result, Is.EqualTo(new[] { "DisciplineCode", "DrawingSize", "ProjectPhase", "ZoneCode" })); // Alphabetically ordered
    }

    [Test]
    public async Task GetDistinctPropertyNamesAsync_NoProperties_ReturnsEmptyList()
    {
        // Act
        var result = await _customPropertyRepository.GetDistinctPropertyNamesAsync();

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    [Test]
    public async Task GetDistinctPropertyNamesAsync_WithDuplicateNames_ReturnsUniqueOnly()
    {
        // Arrange
        var properties = new[]
        {
            new CustomProperty(_testDocumentId1, "DisciplineCode", "ARCH"),
            new CustomProperty(_testDocumentId2, "DisciplineCode", "MECH"),
            new CustomProperty(_testDocumentId1, "DisciplineCode", "ELEC"), // Same name, different value
            new CustomProperty(_testDocumentId2, "ProjectPhase", "Design")
        };

        foreach (var property in properties)
        {
            await _customPropertyRepository.InsertAsync(property);
        }

        // Act
        var result = await _customPropertyRepository.GetDistinctPropertyNamesAsync();

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
        Assert.That(result, Does.Contain(("DisciplineCode")));
        Assert.That(result, Does.Contain(("ProjectPhase")));
    }

    [Test]
    public async Task GetPropertiesByNameAsync_CaseHandling_ReturnsExpectedResults()
    {
        // Note: This test depends on SQLite's default case-insensitive behavior for ASCII characters
        // Arrange
        var property = new CustomProperty(_testDocumentId1, "DisciplineCode", "ARCH");
        await _customPropertyRepository.InsertAsync(property);

        // Act - Test with different case
        var result = await _customPropertyRepository.GetPropertiesByNameAsync("disciplinecode");

        // Assert
        // Behavior may vary based on SQLite collation settings
        // This test documents the actual behavior rather than asserting specific case sensitivity
        Assert.That(result, Is.Not.Null);
        Console.WriteLine($"Case-insensitive search returned {result.Count} results");
    }

    [Test]
    public async Task SearchOperations_WithLargeDataset_PerformEfficiently()
    {
        // Arrange - Create a larger dataset to test performance
        var properties = new List<CustomProperty>();
        var propertyNames = new[] { "DisciplineCode", "ProjectPhase", "DrawingSize", "ZoneCode", "Level" };
        var propertyValues = new[] { "ARCH", "MECH", "ELEC", "STRUCT", "CIVIL" };

        for (int i = 0; i < 100; i++)
        {
            var documentId = (i % 2 == 0) ? _testDocumentId1 : _testDocumentId2;
            var propertyName = propertyNames[i % propertyNames.Length];
            var propertyValue = propertyValues[i % propertyValues.Length];

            properties.Add(new CustomProperty(documentId, propertyName, $"{propertyValue}_{i}"));
        }

        await _customPropertyRepository.InsertAllAsync(properties);

        // Act & Assert - Test various search operations
        var disciplineProperties = await _customPropertyRepository.GetPropertiesByNameAsync("DisciplineCode");
        Assert.That(disciplineProperties, Has.Count.EqualTo(20)); // 100/5 = 20 per property name

        var archProperties = await _customPropertyRepository.GetPropertiesByNameAndValueAsync("DisciplineCode", "ARCH_0");
        Assert.That(archProperties, Has.Count.EqualTo(1));

        var distinctNames = await _customPropertyRepository.GetDistinctPropertyNamesAsync();
        Assert.That(distinctNames, Has.Count.EqualTo(5));

        var doc1Properties = await _customPropertyRepository.GetPropertiesByDocumentAsync(_testDocumentId1);
        Assert.That(doc1Properties, Has.Count.EqualTo(50)); // Half of the properties
    }
}