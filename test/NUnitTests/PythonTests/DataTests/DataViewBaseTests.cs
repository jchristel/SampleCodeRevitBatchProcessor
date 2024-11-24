using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;

namespace PythonTests.DataTests
{
    public class DataViewBaseTests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.DataViewBaseClass, Is.Not.Null, "DataTypeProperties should be loaded.");
        }

        private dynamic CreateJson(object id)
        {
            // Creates JSON-like structure for testing
            return JsonConvert.SerializeObject(new Dictionary<string, object> { { "id", id } });
        }

        [Test]
        public void InitializeWithDefaultValues_ShouldSetDefaults()
        {
            // Act: Create a DataViewBase instance without JSON input
            var dataView = PythonEngineManager.DataViewBaseClass("view_type");

            // Assert: Check if default values are set correctly
            Assert.That("view_type", Is.EqualTo(dataView.data_type), "Data type should be set to the given value.");
            Assert.That(-1, Is.EqualTo(dataView.id), "ID should default to -1.");
        }

        [Test]
        public void InitializeWithValidJson_ShouldSetId()
        {
            // Arrange: JSON with a valid integer ID
            var jsonString = CreateJson(123);

            // Act: Initialize DataViewBase with JSON
            var dataView = PythonEngineManager.DataViewBaseClass("view_type", jsonString);

            // Assert: ID should be set from JSON
            Assert.That(123, Is.EqualTo(dataView.id), "ID should match the one provided in JSON.");
        }

        [Test]
        public void InitializeWithInvalidIdType_ShouldThrowTypeError()
        {
            // Arrange: JSON with an invalid ID type (string instead of int)
            var jsonString = CreateJson("invalid_id");

            // Act & Assert: Initialization should throw a TypeError
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataViewBaseClass("view_type", jsonString));
            Assert.That(ex.Message, Does.Contain("Expected 'id' to be an int"), "Expected TypeError for non-integer ID.");
        }

        [Test]
        public void InitializeWithInvalidJsonType_ShouldThrowTypeError()
        {
            // Arrange: An invalid JSON type (e.g., list instead of dictionary)
            var invalidJson = new List<object> { "invalid" };

            // Act & Assert: Initialization should throw a TypeError
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataViewBaseClass("view_type", invalidJson));
            Assert.That(ex.Message, Does.Contain("Argument j supplied must be of type string or type dictionary"), "Expected TypeError for non-dictionary JSON.");
        }

        [Test]
        public void EqualityWithSameId_ShouldReturnTrue()
        {
            // Arrange: Two DataViewBase instances with the same ID
            var jsonString = CreateJson(123);
            var dataView1 = PythonEngineManager.DataViewBaseClass("view_type", jsonString);
            var dataView2 = PythonEngineManager.DataViewBaseClass("view_type", jsonString);

            // Assert: They should be equal
            Assert.That(dataView1 == dataView2, Is.True, "Operator == should return true for instances with the same ID.");
        }

        [Test]
        public void EqualityWithDifferentId_ShouldReturnFalse()
        {
            // Arrange: Two DataViewBase instances with different IDs
            var dataView1 = PythonEngineManager.DataViewBaseClass("view_type", CreateJson(123));
            var dataView2 = PythonEngineManager.DataViewBaseClass("view_type", CreateJson(456));

            // Assert: They should not be equal
            Assert.That(dataView1.Equals(dataView2), Is.False, "Instances with different IDs should not be equal.");
            Assert.That(dataView1 != dataView2, Is.True, "Operator != should return true for instances with different IDs.");
        }

        [Test]
        public void EqualityWithDifferentType_ShouldReturnNotImplemented()
        {
            // Arrange: DataViewBase instance and an integer (different type)
            var dataView = PythonEngineManager.DataViewBaseClass("view_type");

            // Act & Assert: Comparison should return false for different types
            Assert.That(dataView.Equals(123), Is.False, "Equality check should return false for different types.");
        }
    }
}
