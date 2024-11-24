using IronPython.Runtime.Exceptions;
using PythonTests.Setup;

namespace PythonTests.DataTests.PropertyTests
{
    public class DataInstanceProperties
    {

        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.DataInstancePropertiesClass, Is.Not.Null, "DataInstanceProperties should be loaded.");
            Assert.That(PythonEngineManager.DataPropertyClass, Is.Not.Null, "DataProperty should be loaded.");
        }


        [Test]
        public void Constructor_WithValidPythonDictionary_ShouldSetPropertiesCorrectly()
        {
            // Arrange: Create a JSON-like dictionary structure with id and properties
            var jsonDict = PythonEngineManager.PythonEngine.Execute(@"{'id': 123,'properties': [{'name': 'Property1', 'value': 456},{'name': 'Property2', 'value': 'TestValue'}]}", PythonEngineManager.Scope);

            // Act: Instantiate the DataInstanceProperties object with the dictionary
            dynamic dataInstanceProperties = PythonEngineManager.DataInstancePropertiesClass(jsonDict);

            // Assert: Check if 'id' and 'properties' were set correctly
            Assert.That(123, Is.EqualTo(dataInstanceProperties.id));

            // Check properties list contents
            var properties = dataInstanceProperties.properties;
            Assert.That(2, Is.EqualTo(properties.Count));

            // First property checks
            Assert.That("Property1", Is.EqualTo(properties[0].name));
            Assert.That(456, Is.EqualTo(properties[0].value));

            // Second property checks
            Assert.That("Property2", Is.EqualTo(properties[1].name));
            Assert.That("TestValue", Is.EqualTo(properties[1].value));
        }

        [Test]
        public void Constructor_WithInvalidId_ShouldThrowTypeError()
        {
            // Arrange: Pass a string as 'id' to induce a TypeError
            var invalidJsonDict = PythonEngineManager.PythonEngine.Execute(@"{'id': 'InvalidId','properties': []}", PythonEngineManager.Scope);

            // Act & Assert: Expect an exception due to invalid 'id' type
            var ex = Assert.Throws<TypeErrorException>(() =>
            {
                var dataInstanceProperties = PythonEngineManager.DataInstancePropertiesClass(invalidJsonDict);
            });

            Assert.That(ex.Message, Does.Contain("Expected 'id' to be an int"));
        }

        [Test]
        public void Constructor_WithNonDictionaryInput_ShouldThrowTypeError()
        {
            // Arrange: Use an invalid type (integer) for input
            var invalidInput = 123;

            // Act & Assert: Expect a TypeError
            var ex = Assert.Throws<TypeErrorException>(() =>
            {
                var dataInstanceProperties = PythonEngineManager.DataInstancePropertiesClass(invalidInput);
            });

            Assert.That(ex.Message, Does.Contain("Argument j supplied must be of type string or type dictionary"));
        }
    }
}
