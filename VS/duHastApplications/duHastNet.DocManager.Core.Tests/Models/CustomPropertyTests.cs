using NUnit.Framework;
using duHastNet.DocManager.Core.Models;

namespace duHastNet.DocManager.Core.Tests.Models;

[TestFixture]
public class CustomPropertyTests
{
    [Test]
    public void DefaultConstructor_InitializesWithDefaultValues()
    {
        // Act
        var customProperty = new CustomProperty();

        // Assert
        Assert.That(customProperty.Id, Is.EqualTo(0));
        Assert.That(customProperty.DocumentId, Is.EqualTo(0));
        Assert.That(customProperty.PropertyName, Is.EqualTo(string.Empty));
        Assert.That(customProperty.PropertyValue, Is.EqualTo(string.Empty));
    }

    [Test]
    public void Constructor_WithAllParameters_SetsAllProperties()
    {
        // Arrange
        var documentId = 5;
        var propertyName = "ProjectPhase";
        var propertyValue = "Construction";

        // Act
        var customProperty = new CustomProperty(documentId, propertyName, propertyValue);

        // Assert
        Assert.That(customProperty.DocumentId, Is.EqualTo(documentId));
        Assert.That(customProperty.PropertyName, Is.EqualTo(propertyName));
        Assert.That(customProperty.PropertyValue, Is.EqualTo(propertyValue));
        Assert.That(customProperty.Id, Is.EqualTo(0)); // Auto-increment not set until database insert
    }

    [Test]
    public void ToString_FormatsCorrectly()
    {
        // Arrange
        var customProperty = new CustomProperty(1, "DisciplineCode", "ARCH");
        var expectedString = "DisciplineCode: ARCH";

        // Act
        var result = customProperty.ToString();

        // Assert
        Assert.That(result, Is.EqualTo(expectedString));
    }

    [Test]
    public void ToString_WithEmptyValues_FormatsCorrectly()
    {
        // Arrange
        var customProperty = new CustomProperty(1, "", "");
        var expectedString = ": ";

        // Act
        var result = customProperty.ToString();

        // Assert
        Assert.That(result, Is.EqualTo(expectedString));
    }

    [Test]
    public void Properties_CanBeSetAndRetrieved()
    {
        // Arrange
        var customProperty = new CustomProperty();

        // Act
        customProperty.Id = 10;
        customProperty.DocumentId = 25;
        customProperty.PropertyName = "DrawingSize";
        customProperty.PropertyValue = "A1";

        // Assert
        Assert.That(customProperty.Id, Is.EqualTo(10));
        Assert.That(customProperty.DocumentId, Is.EqualTo(25));
        Assert.That(customProperty.PropertyName, Is.EqualTo("DrawingSize"));
        Assert.That(customProperty.PropertyValue, Is.EqualTo("A1"));
    }

    [Test]
    public void Constructor_WithSpecialCharacters_StoresCorrectly()
    {
        // Arrange
        var documentId = 5;
        var propertyName = "File-Path_With.Special@Chars";
        var propertyValue = "C:\\Documents\\Plans\\Floor Plan (Rev 2).dwg";

        // Act
        var customProperty = new CustomProperty(documentId, propertyName, propertyValue);

        // Assert
        Assert.That(customProperty.PropertyName, Is.EqualTo(propertyName));
        Assert.That(customProperty.PropertyValue, Is.EqualTo(propertyValue));
    }

    [Test]
    public void Constructor_WithLongValues_StoresCorrectly()
    {
        // Arrange
        var documentId = 5;
        var propertyName = "VeryLongPropertyNameThatExceedsNormalLength";
        var propertyValue = "This is a very long property value that contains multiple sentences and should be stored correctly even though it's quite lengthy and contains various punctuation marks, numbers like 123, and symbols like @#$%.";

        // Act
        var customProperty = new CustomProperty(documentId, propertyName, propertyValue);

        // Assert
        Assert.That(customProperty.PropertyName, Is.EqualTo(propertyName));
        Assert.That(customProperty.PropertyValue, Is.EqualTo(propertyValue));
    }
}