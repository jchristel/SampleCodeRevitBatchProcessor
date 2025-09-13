using duHastNet.DocManager.Core.Models;

namespace duHastNet.DocManager.Core.Tests.Models
{
    public class RevisionTests
    {
        [SetUp]
        public void Setup()
        {
        }

        [Test]
        public void Constructor_WithDate_SetsRevisionDate()
        {
            // Arrange
            var testDate = new DateTime(2024, 3, 15, 14, 30, 0); // Date with time
            var expectedDate = new DateTime(2024, 3, 15); // Date only (time stripped)

            // Act
            var revision = new duHastNet.DocManager.Core.Models.Revision(testDate);

            // Assert
            Assert.That(revision.RevisionDate, Is.EqualTo(expectedDate));
            Assert.That(revision.Description, Is.Null);
            Assert.That(revision.Id, Is.EqualTo(0)); // Auto-increment not set until database insert
        }

        [Test]
        public void Constructor_WithDateAndDescription_SetsProperties()
        {
            // Arrange
            var testDate = new DateTime(2024, 3, 15, 9, 45, 30); // Date with time
            var expectedDate = new DateTime(2024, 3, 15); // Date only (time stripped)
            var description = "For Construction";

            // Act
            var revision = new Revision(testDate, description);

            // Assert
            Assert.That(revision.RevisionDate, Is.EqualTo(expectedDate));
            Assert.That(revision.Description, Is.EqualTo(description));
            Assert.That(revision.Id, Is.EqualTo(0)); // Auto-increment not set until database insert
        }


        [Test]
        public void ToString_WithoutDescription_FormatsDateOnly()
        {
            // Arrange
            var testDate = new DateTime(2024, 3, 15);
            var revision = new Revision(testDate);
            var expectedString = "2024-03-15";

            // Act
            var result = revision.ToString();

            // Assert
            Assert.That(result, Is.EqualTo(expectedString));
        }
    }
}