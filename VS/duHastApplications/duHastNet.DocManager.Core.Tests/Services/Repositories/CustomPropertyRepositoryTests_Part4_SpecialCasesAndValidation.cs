using NUnit.Framework;
using SQLite;
using duHastNet.DocManager.Core.Services.Repositories;
using duHastNet.DocManager.Core.Models;
using System.IO;

namespace duHastNet.DocManager.Core.Tests.Services.Repositories;

[TestFixture]
public class CustomPropertyRepositoryTests_Part4_SpecialCasesAndValidation
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
    public async Task PropertyNameHandling_WithSpecialCharacters_WorksCorrectly()
    {
        // Arrange
        var specialProperties = new[]
        {
            new CustomProperty(_testDocumentId1, "Property-With-Dashes", "Value1"),
            new CustomProperty(_testDocumentId1, "Property_With_Underscores", "Value2"),
            new CustomProperty(_testDocumentId1, "Property With Spaces", "Value3"),
            new CustomProperty(_testDocumentId1, "Property.With.Dots", "Value4"),
            new CustomProperty(_testDocumentId1, "Property/With/Slashes", "Value5"),
            new CustomProperty(_testDocumentId1, "Property(With)Parentheses", "Value6"),
            new CustomProperty(_testDocumentId1, "Property[With]Brackets", "Value7")
        };

        foreach (var property in specialProperties)
        {
            await _customPropertyRepository.InsertAsync(property);
        }

        // Act & Assert - Test each special character property
        var prop1 = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "Property-With-Dashes");
        Assert.That(prop1, Is.Not.Null);
        Assert.That(prop1.PropertyValue, Is.EqualTo("Value1"));

        var prop2 = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "Property_With_Underscores");
        Assert.That(prop2, Is.Not.Null);
        Assert.That(prop2.PropertyValue, Is.EqualTo("Value2"));

        var prop3 = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "Property With Spaces");
        Assert.That(prop3, Is.Not.Null);
        Assert.That(prop3.PropertyValue, Is.EqualTo("Value3"));

        var prop4 = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "Property.With.Dots");
        Assert.That(prop4, Is.Not.Null);
        Assert.That(prop4.PropertyValue, Is.EqualTo("Value4"));

        var prop5 = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "Property/With/Slashes");
        Assert.That(prop5, Is.Not.Null);
        Assert.That(prop5.PropertyValue, Is.EqualTo("Value5"));

        var prop6 = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "Property(With)Parentheses");
        Assert.That(prop6, Is.Not.Null);
        Assert.That(prop6.PropertyValue, Is.EqualTo("Value6"));

        var prop7 = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "Property[With]Brackets");
        Assert.That(prop7, Is.Not.Null);
        Assert.That(prop7.PropertyValue, Is.EqualTo("Value7"));
    }

    [Test]
    public async Task PropertyValueHandling_WithLongText_WorksCorrectly()
    {
        // Arrange
        var shortValue = "Short";
        var mediumValue = new string('M', 500); // 500 character string
        var longValue = new string('L', 2000); // 2000 character string

        var properties = new[]
        {
            new CustomProperty(_testDocumentId1, "ShortProperty", shortValue),
            new CustomProperty(_testDocumentId1, "MediumProperty", mediumValue),
            new CustomProperty(_testDocumentId1, "LongProperty", longValue)
        };

        foreach (var property in properties)
        {
            await _customPropertyRepository.InsertAsync(property);
        }

        // Act & Assert
        var shortRetrieved = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "ShortProperty");
        Assert.That(shortRetrieved.PropertyValue, Is.EqualTo(shortValue));
        Assert.That(shortRetrieved.PropertyValue, Has.Length.EqualTo(5));

        var mediumRetrieved = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "MediumProperty");
        Assert.That(mediumRetrieved.PropertyValue, Is.EqualTo(mediumValue));
        Assert.That(mediumRetrieved.PropertyValue, Has.Length.EqualTo(500));

        var longRetrieved = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "LongProperty");
        Assert.That(longRetrieved.PropertyValue, Is.EqualTo(longValue));
        Assert.That(longRetrieved.PropertyValue, Has.Length.EqualTo(2000));
    }

    [Test]
    public async Task PropertyValueHandling_WithSpecialCharacters_WorksCorrectly()
    {
        // Arrange
        var specialValues = new[]
        {
            new CustomProperty(_testDocumentId1, "Unicode", "测试 Test ñoño αβγ δεζ"),
            new CustomProperty(_testDocumentId1, "Symbols", "@#$%^&*()+=[]{}|\\:;\"'<>,.?/~`"),
            new CustomProperty(_testDocumentId1, "Quotes", "Value with \"double quotes\" and 'single quotes'"),
            new CustomProperty(_testDocumentId1, "Path", "C:\\Projects\\File Name (Rev 2).dwg"),
            new CustomProperty(_testDocumentId1, "Json", "{\"key\": \"value\", \"number\": 123}"),
            new CustomProperty(_testDocumentId1, "Xml", "<element attr=\"value\">Content</element>"),
            new CustomProperty(_testDocumentId1, "Sql", "SELECT * FROM table WHERE column = 'value'"),
            new CustomProperty(_testDocumentId1, "NewLines", "Line 1\nLine 2\r\nLine 3"),
            new CustomProperty(_testDocumentId1, "Tabs", "Column1\tColumn2\tColumn3"),
            new CustomProperty(_testDocumentId1, "Empty", ""),
            new CustomProperty(_testDocumentId1, "Whitespace", "   "),
            new CustomProperty(_testDocumentId1, "Mixed", "Mixed: 123 ABC !@# αβγ")
        };

        foreach (var property in specialValues)
        {
            await _customPropertyRepository.InsertAsync(property);
        }

        // Act & Assert
        var unicode = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "Unicode");
        Assert.That(unicode.PropertyValue, Is.EqualTo("测试 Test ñoño αβγ δεζ"));

        var symbols = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "Symbols");
        Assert.That(symbols.PropertyValue, Is.EqualTo("@#$%^&*()+=[]{}|\\:;\"'<>,.?/~`"));

        var quotes = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "Quotes");
        Assert.That(quotes.PropertyValue, Is.EqualTo("Value with \"double quotes\" and 'single quotes'"));

        var path = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "Path");
        Assert.That(path.PropertyValue, Is.EqualTo("C:\\Projects\\File Name (Rev 2).dwg"));

        var json = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "Json");
        Assert.That(json.PropertyValue, Is.EqualTo("{\"key\": \"value\", \"number\": 123}"));

        var xml = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "Xml");
        Assert.That(xml.PropertyValue, Is.EqualTo("<element attr=\"value\">Content</element>"));

        var sql = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "Sql");
        Assert.That(sql.PropertyValue, Is.EqualTo("SELECT * FROM table WHERE column = 'value'"));

        var newLines = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "NewLines");
        Assert.That(newLines.PropertyValue, Is.EqualTo("Line 1\nLine 2\r\nLine 3"));

        var tabs = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "Tabs");
        Assert.That(tabs.PropertyValue, Is.EqualTo("Column1\tColumn2\tColumn3"));

        var empty = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "Empty");
        Assert.That(empty.PropertyValue, Is.EqualTo(""));

        var whitespace = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "Whitespace");
        Assert.That(whitespace.PropertyValue, Is.EqualTo("   "));

        var mixed = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "Mixed");
        Assert.That(mixed.PropertyValue, Is.EqualTo("Mixed: 123 ABC !@# αβγ"));
    }

    [Test]
    public async Task PropertyHandling_WithNullAndEmptyValues_WorksCorrectly()
    {
        // Arrange
        var properties = new[]
        {
            new CustomProperty(_testDocumentId1, "EmptyValue", ""),
            new CustomProperty(_testDocumentId1, "WhitespaceValue", "   "),
            new CustomProperty(_testDocumentId1, "NormalValue", "Normal")
        };

        foreach (var property in properties)
        {
            await _customPropertyRepository.InsertAsync(property);
        }

        // Act & Assert
        var emptyValue = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "EmptyValue");
        Assert.That(emptyValue, Is.Not.Null);
        Assert.That(emptyValue.PropertyValue, Is.EqualTo(""));

        var whitespaceValue = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "WhitespaceValue");
        Assert.That(whitespaceValue, Is.Not.Null);
        Assert.That(whitespaceValue.PropertyValue, Is.EqualTo("   "));

        var normalValue = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "NormalValue");
        Assert.That(normalValue, Is.Not.Null);
        Assert.That(normalValue.PropertyValue, Is.EqualTo("Normal"));
    }

    [Test]
    public async Task PropertyNameHandling_WithDuplicatesAndCasing_WorksCorrectly()
    {
        // Test how the repository handles property names with different casing

        // Arrange
        var properties = new[]
        {
            new CustomProperty(_testDocumentId1, "PropertyName", "Value1"),
            new CustomProperty(_testDocumentId1, "propertyname", "Value2"), // Different case
            new CustomProperty(_testDocumentId1, "PROPERTYNAME", "Value3")  // Different case
        };

        foreach (var property in properties)
        {
            await _customPropertyRepository.InsertAsync(property);
        }

        // Act
        var allProperties = await _customPropertyRepository.GetPropertiesByDocumentAsync(_testDocumentId1);
        var exactMatch = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "PropertyName");

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(allProperties, Has.Count.EqualTo(3), "All three properties should be stored separately");
            Assert.That(exactMatch, Is.Not.Null);
            Assert.That(exactMatch.PropertyValue, Is.EqualTo("Value1"));
        });
    }

    [Test]
    public async Task PropertyOperations_WithVeryLongPropertyNames_WorksCorrectly()
    {
        // Arrange
        var normalName = "NormalPropertyName";
        var longName = new string('P', 255); // Very long property name
        var veryLongName = new string('V', 1000); // Extremely long property name

        var properties = new[]
        {
            new CustomProperty(_testDocumentId1, normalName, "NormalValue"),
            new CustomProperty(_testDocumentId1, longName, "LongNameValue"),
            new CustomProperty(_testDocumentId1, veryLongName, "VeryLongNameValue")
        };

        foreach (var property in properties)
        {
            await _customPropertyRepository.InsertAsync(property);
        }

        // Act & Assert
        var normalRetrieved = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, normalName);
        Assert.That(normalRetrieved, Is.Not.Null);
        Assert.That(normalRetrieved.PropertyValue, Is.EqualTo("NormalValue"));

        var longRetrieved = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, longName);
        Assert.That(longRetrieved, Is.Not.Null);
        Assert.That(longRetrieved.PropertyValue, Is.EqualTo("LongNameValue"));

        var veryLongRetrieved = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, veryLongName);
        Assert.That(veryLongRetrieved, Is.Not.Null);
        Assert.That(veryLongRetrieved.PropertyValue, Is.EqualTo("VeryLongNameValue"));

        // Verify all properties are returned in search operations
        var distinctNames = await _customPropertyRepository.GetDistinctPropertyNamesAsync();
        Assert.That(distinctNames, Has.Count.EqualTo(3));
        Assert.That(distinctNames, Does.Contain(normalName));
        Assert.That(distinctNames, Does.Contain(longName));
        Assert.That(distinctNames, Does.Contain(veryLongName));
    }

    [Test]
    public async Task PropertyOperations_WithNumericValues_WorksCorrectly()
    {
        // Test storing various numeric values as strings

        // Arrange
        var numericProperties = new[]
        {
            new CustomProperty(_testDocumentId1, "Integer", "123"),
            new CustomProperty(_testDocumentId1, "Decimal", "123.45"),
            new CustomProperty(_testDocumentId1, "Negative", "-456.78"),
            new CustomProperty(_testDocumentId1, "Scientific", "1.23E+10"),
            new CustomProperty(_testDocumentId1, "Percentage", "95.5%"),
            new CustomProperty(_testDocumentId1, "Currency", "$1,234.56"),
            new CustomProperty(_testDocumentId1, "Fraction", "3/4"),
            new CustomProperty(_testDocumentId1, "Large", "999999999999999999"),
            new CustomProperty(_testDocumentId1, "Zero", "0"),
            new CustomProperty(_testDocumentId1, "Leading Zeros", "00123")
        };

        foreach (var property in numericProperties)
        {
            await _customPropertyRepository.InsertAsync(property);
        }

        // Act & Assert - Verify all numeric values are stored and retrieved correctly
        var integer = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "Integer");
        Assert.That(integer.PropertyValue, Is.EqualTo("123"));

        var decimalValue = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "Decimal");
        Assert.That(decimalValue.PropertyValue, Is.EqualTo("123.45"));

        var negative = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "Negative");
        Assert.That(negative.PropertyValue, Is.EqualTo("-456.78"));

        var scientific = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "Scientific");
        Assert.That(scientific.PropertyValue, Is.EqualTo("1.23E+10"));

        var leadingZeros = await _customPropertyRepository.GetPropertyAsync(_testDocumentId1, "Leading Zeros");
        Assert.That(leadingZeros.PropertyValue, Is.EqualTo("00123"));

        // Test search operations with numeric values
        var decimalSearch = await _customPropertyRepository.GetPropertiesByNameAndValueAsync("Decimal", "123.45");
        Assert.That(decimalSearch, Has.Count.EqualTo(1));
    }

    [Test]
    public async Task PropertyOperations_ConcurrencyStressTest_HandlesCorrectly()
    {
        // Test concurrent operations on custom properties

        // Arrange
        var tasks = new List<Task>();
        var propertyNames = new[] { "Concurrent1", "Concurrent2", "Concurrent3", "Concurrent4", "Concurrent5" };

        // Act - Create multiple concurrent operations
        for (int i = 0; i < 50; i++)
        {
            var index = i;
            tasks.Add(Task.Run(async () =>
            {
                var propertyName = propertyNames[index % propertyNames.Length];
                var documentId = (index % 2 == 0) ? _testDocumentId1 : _testDocumentId2;

                var property = new CustomProperty(documentId, propertyName, $"Value_{index}");
                await _customPropertyRepository.InsertAsync(property);

                // Immediately try to read it back
                var retrieved = await _customPropertyRepository.GetPropertyAsync(documentId, propertyName);
                Assert.That(retrieved, Is.Not.Null);
            }));
        }

        await Task.WhenAll(tasks);

        // Assert - Verify final state
        var finalCount = await _customPropertyRepository.CountAsync();
        Assert.That(finalCount, Is.GreaterThan(0));
        Assert.That(finalCount, Is.LessThanOrEqualTo(50));

        var distinctNames = await _customPropertyRepository.GetDistinctPropertyNamesAsync();
        Assert.That(distinctNames, Has.Count.LessThanOrEqualTo(5));
    }
}