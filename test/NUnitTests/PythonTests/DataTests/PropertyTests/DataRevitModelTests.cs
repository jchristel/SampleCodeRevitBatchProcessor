using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;


namespace PythonTests.DataTests.PropertyTests
{
    public class DataRevitModelTests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.DataRevitModelClass, Is.Not.Null, "DataRevitModel should be loaded.");
        }

        // Helper method to create a JSON string for DataRevitModel initialization
        private string CreateJson(string name)
        {
            return JsonConvert.SerializeObject(new { name });
        }

        [Test]
        public void InitializeWithValidJson_ShouldSetName()
        {
            // Arrange: JSON data with a valid name
            var jsonString = CreateJson("TestModel");

            // Act: initialize instance with JSON data
            var model = PythonEngineManager.DataRevitModelClass(jsonString);

            // Assert: verify the name is correctly set
            Assert.That("TestModel", Is.EqualTo(model.name), "Expected name to be 'TestModel'.");
        }

        [Test]
        public void InitializeWithEmptyJson_ShouldUseDefaultName()
        {
            // Arrange: an empty JSON object
            var jsonString = JsonConvert.SerializeObject(new { });

            // Act: initialize instance with empty JSON
            var model = PythonEngineManager.DataRevitModelClass(jsonString);

            // Assert: name should use default value
            Assert.That("-", Is.EqualTo(model.name), "Expected default name of '-'.");
        }

        [Test]
        public void InitializeWithNonStringName_ShouldThrowTypeError()
        {
            // Arrange: JSON with a non-string type for name
            var jsonString = JsonConvert.SerializeObject(new { name = 123 });

            // Act & Assert: expect initialization to throw an error
            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.DataRevitModelClass(jsonString));
            Assert.That(ex.Message, Does.Contain("name needs to be of type str"));
        }

        [Test]
        public void InitializeWithNonJsonString_ShouldThrowValueError()
        {
            // Arrange: a non-JSON string input
            var jsonString = "non-json string";

            // Act & Assert: expect initialization to throw an error
            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.DataRevitModelClass(jsonString));
            Assert.That(ex.Message, Does.Contain("Expecting value:"));
        }

        [Test]
        public void InitializeWithValidJson_EmptyName_ShouldSetEmptyName()
        {
            // Arrange: JSON data with an empty string for name
            var jsonString = CreateJson("");

            // Act: initialize instance with JSON data
            var model = PythonEngineManager.DataRevitModelClass(jsonString);

            // Assert: verify the name is set as an empty string
            Assert.That("",Is.EqualTo( model.name), "Expected name to be an empty string.");
        }

        [Test]
        public void EqualInstances_ShouldReturnTrue()
        {
            // Arrange: identical JSON data for two instances
            var jsonString = CreateJson("TestModel");
            var modelA = PythonEngineManager.DataRevitModelClass(jsonString);
            var modelB = PythonEngineManager.DataRevitModelClass(jsonString);

            // Act & Assert: verify equality comparison
            Assert.That(modelA == modelB, Is.True, "Expected two instances with identical data to be equal.");
            Assert.That(modelA != modelB, Is.False, "Expected two instances with identical data not to be unequal.");
        }

        [Test]
        public void DifferentNames_ShouldReturnFalseForEquality()
        {
            // Arrange: different JSON data for two instances
            var jsonStringA = CreateJson("ModelA");
            var jsonStringB = CreateJson("ModelB");
            var modelA = PythonEngineManager.DataRevitModelClass(jsonStringA);
            var modelB = PythonEngineManager.DataRevitModelClass(jsonStringB);

            // Act & Assert: verify inequality
            Assert.That(modelA == modelB, Is.False, "Expected two instances with different names to not be equal.");
            Assert.That(modelA != modelB, Is.True, "Expected two instances with different names to be unequal.");
        }

        [Test]
        public void DefaultNames_ShouldBeEqual()
        {
            // Arrange: two instances with default names
            var modelA = PythonEngineManager.DataRevitModelClass("{}");
            var modelB = PythonEngineManager.DataRevitModelClass("{}");

            // Act & Assert: verify equality for instances with default names
            Assert.That(modelA == modelB, Is.True, "Expected two instances with default names to be equal.");
            Assert.That(modelA != modelB, Is.False, "Expected two instances with default names not to be unequal.");
        }
    }
}
