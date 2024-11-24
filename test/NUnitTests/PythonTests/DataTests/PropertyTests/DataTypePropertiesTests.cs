using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;

namespace PythonTests.DataTests.PropertyTests
{
    public class DataTypePropertiesTests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.DataTypePropertiesClass, Is.Not.Null, "DataTypeProperties should be loaded.");
        }

        // Helper method to create a JSON string for DataTypeProperties initialization
        private string CreateJson(int id, string name = "-", List<object> properties = null)
        {
            return JsonConvert.SerializeObject(new
            {
                id,
                name,
                properties
            });
        }

        [Test]
        public void InitializeWithValidJson_ShouldSetIdAndProperties()
        {
            // Arrange: JSON data with valid id and properties
            var jsonString = CreateJson(123, "TypeName", new List<object>
        {
            new { name = "Property1", value = 456 },
            new { name = "Property2", value = "TestValue" }
        });

            // Act: initialize instance with JSON data
            var model = PythonEngineManager.DataTypePropertiesClass(jsonString);

            // Assert: verify id and properties are correctly set
            Assert.That(123, Is.EqualTo(model.id), "Expected id to be '123'.");
            Assert.That(2, Is.EqualTo(model.properties.Count), "Expected 2 properties to be set.");
            Assert.That("Property1", Is.EqualTo(model.properties[0].name), "Expected first property name to be 'Property1'.");
            Assert.That(456, Is.EqualTo(model.properties[0].value), "Expected first property value to be '456'.");
            Assert.That("Property2", Is.EqualTo(model.properties[1].name), "Expected second property name to be 'Property2'.");
            Assert.That("TestValue", Is.EqualTo(model.properties[1].value), "Expected second property value to be 'TestValue'.");
        }

        [Test]
        public void InitializeWithEmptyJson_ShouldUseDefaultValues()
        {
            // Arrange: an empty JSON object
            var jsonString = JsonConvert.SerializeObject(new { });

            // Act: initialize instance with empty JSON
            var model = PythonEngineManager.DataTypePropertiesClass(jsonString);

            // Assert: verify default values are set
            Assert.That("-", Is.EqualTo(model.name), "Expected default name to be '-'.");
            Assert.That(-1, Is.EqualTo(model.id), "Expected default id to be '-1'.");
            Assert.That(0, Is.EqualTo(model.properties.Count), "Expected default properties list to be empty.");
        }

        [Test]
        public void InitializeWithNonIntegerId_ShouldThrowValueError()
        {
            // Arrange: JSON with a non-integer type for id
            var jsonString = JsonConvert.SerializeObject(new { name = "TypeName", id = "non-integer" });

            // Act & Assert: expect initialization to throw an error
            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.DataTypePropertiesClass(jsonString));
            Assert.That(ex.Message, Does.Contain("Node type_properties failed to initialise with: id needs to "));
        }

        [Test]
        public void InitializeWithProperties_ShouldSetPropertiesCorrectly()
        {
            // Arrange: JSON data with valid properties
            var jsonString = CreateJson(123, "TypeName", new List<object>
        {
            new { name = "Property1", value = 456 },
            new { name = "Property2", value = "TestValue" }
        });

            // Act: initialize instance with JSON data
            var model = PythonEngineManager.DataTypePropertiesClass(jsonString);

            // Assert: verify properties are set correctly
            Assert.That(2, Is.EqualTo(model.properties.Count), "Expected 2 properties to be set.");
            Assert.That("Property1", Is.EqualTo(model.properties[0].name), "Expected first property name to be 'Property1'.");
            Assert.That(456, Is.EqualTo(model.properties[0].value), "Expected first property value to be '456'.");
            Assert.That("Property2", Is.EqualTo(model.properties[1].name), "Expected second property name to be 'Property2'.");
            Assert.That("TestValue", Is.EqualTo(model.properties[1].value), "Expected second property value to be 'TestValue'.");
        }

        [Test]
        public void EqualInstances_ShouldReturnTrue()
        {
            // Arrange: identical JSON data for two instances
            var jsonString = CreateJson(123, "TypeName", new List<object>
        {
            new { name = "Property1", value = 456 }
        });
            var modelA = PythonEngineManager.DataTypePropertiesClass(jsonString);
            var modelB = PythonEngineManager.DataTypePropertiesClass(jsonString);

            // Act & Assert: verify equality comparison
            Assert.That(modelA == modelB, Is.True, "Expected two instances with identical data to be equal.");
            Assert.That(modelA != modelB, Is.False, "Expected two instances with identical data not to be unequal.");
        }

        [Test]
        public void DifferentIdOrName_ShouldReturnFalseForEquality()
        {
            // Arrange: different JSON data for two instances
            var jsonStringA = CreateJson(123, "TypeNameA", new List<object>
        {
            new { name = "Property1", value = 456 }
        });
            var jsonStringB = CreateJson(124, "TypeNameB", new List<object>
        {
            new { name = "Property1", value = 456 }
        });
            var modelA = PythonEngineManager.DataTypePropertiesClass(jsonStringA);
            var modelB = PythonEngineManager.DataTypePropertiesClass(jsonStringB);

            // Act & Assert: verify inequality
            Assert.That(modelA == modelB, Is.False, "Expected two instances with different ids or names to not be equal.");
            Assert.That(modelA != modelB, Is.True, "Expected two instances with different ids or names to be unequal.");
        }

        [Test]
        public void DifferentProperties_ShouldReturnFalseForEquality()
        {
            // Arrange: different property lists for two instances
            var jsonStringA = CreateJson(123, "TypeName", new List<object>
            {
                new { name = "Property1", value = 456 }
            });
            var jsonStringB = CreateJson(123, "TypeName", new List<object>
            {
                new { name = "Property2", value = "TestValue" }
            });
            var modelA = PythonEngineManager.DataTypePropertiesClass(jsonStringA);
            var modelB = PythonEngineManager.DataTypePropertiesClass(jsonStringB);

            // Act & Assert: verify inequality based on properties
            Assert.That(modelA == modelB, Is.False, "Expected instances with different properties to not be equal.");
            Assert.That(modelA != modelB, Is.True, "Expected instances with different properties to be unequal.");
        }

        [Test]
        public void DefaultValues_ShouldBeEqual()
        {
            // Arrange: two instances with default values
            var modelA = PythonEngineManager.DataTypePropertiesClass("{}");
            var modelB = PythonEngineManager.DataTypePropertiesClass("{}");

            // Act & Assert: verify equality for instances with default values
            Assert.That(modelA == modelB, Is.True, "Expected two instances with default values to be equal.");
            Assert.That(modelA != modelB, Is.False, "Expected two instances with default values not to be unequal.");
        }
    }
}
