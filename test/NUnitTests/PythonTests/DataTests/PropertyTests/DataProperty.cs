using IronPython.Runtime.Exceptions;
using PythonTests.Setup;

namespace PythonTests.DataTests.PropertyTests
{
    public class DataProperty
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.DataInstancePropertiesClass, Is.Not.Null, "DataInstanceProperties should be loaded.");
            Assert.That(PythonEngineManager.DataPropertyClass, Is.Not.Null, "DataProperty should be loaded.");
        }

        [Test]
        public void Constructor_WithValidJsonString_ShouldInitializeProperties()
        {
            // Arrange
            string json = "{\"name\": \"TestProperty\", \"value\": 123}";

            // Act
            dynamic dataProperty = PythonEngineManager.DataPropertyClass(json);

            // Assert
            Assert.That("TestProperty", Is.EqualTo( dataProperty.name));
            Assert.That(123, Is.EqualTo(dataProperty.value));
        }

        [Test]
        public void Constructor_WithValidJsonDictionary_ShouldInitializeProperties()
        {
            // Arrange
            var pythonDict = PythonEngineManager.PythonEngine.Execute("dict(name='TestProperty', value=123)", PythonEngineManager.Scope);

            // Act
            dynamic dataProperty = PythonEngineManager.DataPropertyClass(pythonDict);

            // Assert
            Assert.That("TestProperty", Is.EqualTo(dataProperty.name));
            Assert.That(123, Is.EqualTo(dataProperty.value));
        }

        [Test]
        public void Constructor_WithInvalidJsonString_ShouldThrowJsonException()
        {
            // Arrange
            string invalidJson = "{invalid json}";

            // Act & Assert
            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.DataPropertyClass(invalidJson));
            Assert.That(ex.Message, Does.Contain("Expecting property name enclosed in double quotes"));
        }

        [Test]
        public void Constructor_WithInvalidJsonType_ShouldThrowTypeError()
        {
            // Arrange
            var invalidInput = 12345;

            // Act & Assert
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataPropertyClass(invalidInput));
            Assert.That(ex.Message, Does.Contain("Argument j supplied must be of type string or type dictionary."));
        }

        [Test]
        public void Constructor_WithMissingNameProperty_ShouldSetDefaultName()
        {
            // Arrange
            string json = "{\"value\": 123}";

            // Act
            dynamic dataProperty = PythonEngineManager.DataPropertyClass(json);

            // Assert
            Assert.That("-", Is.EqualTo(dataProperty.name));
            Assert.That(123, Is.EqualTo(dataProperty.value));
        }

        [Test]
        public void Constructor_WithMissingValueProperty_ShouldSetDefaultValue()
        {
            // Arrange
            string json = "{\"name\": \"TestProperty\"}";

            // Act
            dynamic dataProperty = PythonEngineManager.DataPropertyClass(json);
           
            // Assert
            Assert.That("TestProperty", Is.EqualTo(dataProperty.name));
            Assert.That(null, Is.EqualTo(dataProperty.value));
        }

        [Test]
        public void Constructor_WithInvalidNameType_ShouldThrowTypeError()
        {
            // Arrange
            var pythonDict = PythonEngineManager.PythonEngine.Execute("dict(name=1234, value=789)", PythonEngineManager.Scope);

            // Act & Assert
            var ex = Assert.Throws < ValueErrorException > (() => PythonEngineManager.DataPropertyClass(pythonDict));
            Assert.That(ex.Message, Does.Contain("failed to initialise"));
        }

        [Test]
        public void Constructor_WithValidJsonObject_ShouldInitializeCorrectly()
        {
            // Arrange
            var pythonDict = PythonEngineManager.PythonEngine.Execute("dict(name='PropertyName', value=789)", PythonEngineManager.Scope);

            // Act
            dynamic dataProperty = PythonEngineManager.DataPropertyClass(pythonDict);

            // Assert
            Assert.That("PropertyName",Is.EqualTo( dataProperty.name));
            Assert.That(789, Is.EqualTo(dataProperty.value));
        }

        [Test]
        public void DefaultConstructor_ShouldSetDefaultValues()
        {
            // Arrange & Act
            dynamic dataProperty = PythonEngineManager.DataPropertyClass();

            // Assert
            Assert.That("-", Is.EqualTo(dataProperty.name)); // default name
            Assert.That(dataProperty.value, Is.Null);       // default value
        }

    }
}
