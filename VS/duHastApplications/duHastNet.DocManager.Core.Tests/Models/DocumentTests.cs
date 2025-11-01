using NUnit.Framework;
using duHastNet.DocManager.Core.Models;

namespace duHastNet.DocManager.Core.Tests.Models;

[TestFixture]
public class DocumentTests
{
    [Test]
    public void Constructor_WithAllParameters_SetsAllProperties()
    {
        // Arrange
        var number = "A-101";
        var name = "Ground Floor Plan";
        var revision = "3";
        var revisionId = 5;

        // Act
        var document = new Document(number, name, revision, revisionId);

        // Assert
        Assert.That(document.Number, Is.EqualTo(number));
        Assert.That(document.Name, Is.EqualTo(name));
        Assert.That(document.Revision, Is.EqualTo(revision));
        Assert.That(document.RevisionId, Is.EqualTo(revisionId));
        Assert.That(document.Id, Is.EqualTo(0)); // Auto-increment not set until database insert
        Assert.That(document.CustomProperties, Is.Not.Null);
        Assert.That(document.CustomProperties.Count, Is.EqualTo(0));
    }

    [Test]
    public void ToString_FormatsCorrectly()
    {
        // Arrange
        var document = new Document("S-201", "Structural Foundation Plan", "2B", 3);
        var expectedString = "S-201 Rev 2B - Structural Foundation Plan";

        // Act
        var result = document.ToString();

        // Assert
        Assert.That(result, Is.EqualTo(expectedString));
    }

    [Test]
    public void IsNewerThan_WithSameNumberAndHigherRevision_ReturnsTrue()
    {
        // Arrange
        var document1 = new Document("A-101", "Floor Plan", "2", 1);
        var document2 = new Document("A-101", "Floor Plan", "3", 2);

        // Act
        var result = document2.IsNewerThan(document1);

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public void IsSameDocumentAs_WithSameNumber_ReturnsTrue()
    {
        // Arrange
        var document1 = new Document("M-301", "HVAC Plan", "1", 1);
        var document2 = new Document("M-301", "HVAC Plan Updated", "2", 2);

        // Act
        var result = document1.IsSameDocumentAs(document2);

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public void IsSameDocumentAs_WithDifferentNumber_ReturnsFalse()
    {
        // Arrange
        var document1 = new Document("A-101", "Floor Plan", "1", 1);
        var document2 = new Document("A-102", "Ceiling Plan", "1", 1);

        // Act
        var result = document1.IsSameDocumentAs(document2);

        // Assert
        Assert.That(result, Is.False);
    }
}