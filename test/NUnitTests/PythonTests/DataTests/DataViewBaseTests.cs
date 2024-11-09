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
            Assert.IsNotNull(PythonEngineManager.DataViewBaseClass, "DataTypeProperties should be loaded.");
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
            Assert.AreEqual("view_type", dataView.data_type, "Data type should be set to the given value.");
            Assert.AreEqual(-1, dataView.id, "ID should default to -1.");
        }

        [Test]
        public void InitializeWithValidJson_ShouldSetId()
        {
            // Arrange: JSON with a valid integer ID
            var jsonString = CreateJson(123);

            // Act: Initialize DataViewBase with JSON
            var dataView = PythonEngineManager.DataViewBaseClass("view_type", jsonString);

            // Assert: ID should be set from JSON
            Assert.AreEqual(123, dataView.id, "ID should match the one provided in JSON.");
        }

        [Test]
        public void InitializeWithInvalidIdType_ShouldThrowTypeError()
        {
            // Arrange: JSON with an invalid ID type (string instead of int)
            var jsonString = CreateJson("invalid_id");

            // Act & Assert: Initialization should throw a TypeError
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataViewBaseClass("view_type", jsonString));
            StringAssert.Contains("Expected 'id' to be an int", ex.Message, "Expected TypeError for non-integer ID.");
        }

        [Test]
        public void InitializeWithInvalidJsonType_ShouldThrowTypeError()
        {
            // Arrange: An invalid JSON type (e.g., list instead of dictionary)
            var invalidJson = new List<object> { "invalid" };

            // Act & Assert: Initialization should throw a TypeError
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataViewBaseClass("view_type", invalidJson));
            StringAssert.Contains("Argument j supplied must be of type string or type dictionary", ex.Message, "Expected TypeError for non-dictionary JSON.");
        }

        [Test]
        public void EqualityWithSameId_ShouldReturnTrue()
        {
            // Arrange: Two DataViewBase instances with the same ID
            var jsonString = CreateJson(123);
            var dataView1 = PythonEngineManager.DataViewBaseClass("view_type", jsonString);
            var dataView2 = PythonEngineManager.DataViewBaseClass("view_type", jsonString);

            // Assert: They should be equal
            Assert.IsTrue(dataView1 == dataView2, "Operator == should return true for instances with the same ID.");
        }

        [Test]
        public void EqualityWithDifferentId_ShouldReturnFalse()
        {
            // Arrange: Two DataViewBase instances with different IDs
            var dataView1 = PythonEngineManager.DataViewBaseClass("view_type", CreateJson(123));
            var dataView2 = PythonEngineManager.DataViewBaseClass("view_type", CreateJson(456));

            // Assert: They should not be equal
            Assert.IsFalse(dataView1.Equals(dataView2), "Instances with different IDs should not be equal.");
            Assert.IsTrue(dataView1 != dataView2, "Operator != should return true for instances with different IDs.");
        }

        [Test]
        public void EqualityWithDifferentType_ShouldReturnNotImplemented()
        {
            // Arrange: DataViewBase instance and an integer (different type)
            var dataView = PythonEngineManager.DataViewBaseClass("view_type");

            // Act & Assert: Comparison should return false for different types
            Assert.IsFalse(dataView.Equals(123), "Equality check should return false for different types.");
        }
    }
}
