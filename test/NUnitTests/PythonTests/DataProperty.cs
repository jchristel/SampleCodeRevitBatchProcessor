using System.Text;
using System.Threading.Tasks;
using Microsoft.Scripting.Hosting;
using IronPython.Runtime.Exceptions;

namespace PythonTests
{
    public class DataProperty
    {

        ScriptEngine _engine;
        ScriptScope _scope;

        private dynamic dataPropertyClass;

        [SetUp]
        public void Setup()
        {
            // get a python engine
            ScriptEngine engine = PythonRunner.SetupEngine();
            _scope = engine.CreateScope();

            // get the repository path
            string repoPath = PythonRunner.GetRepositoryPath();

            // set path to bounding box 2 class
            var pythonFilePath_dataDesignSetOption = Path.Combine(repoPath, @"duHast\Data\Objects\Properties\data_property.py");

            //run the file
            engine.ExecuteFile(pythonFilePath_dataDesignSetOption, _scope);

            dataPropertyClass = _scope.GetVariable("DataProperty");

            //store the engine instance
            _engine = engine;
        }

        [Test]
        public void Constructor_WithValidJsonString_ShouldInitializeProperties()
        {
            // Arrange
            string json = "{\"name\": \"TestProperty\", \"value\": 123}";

            // Act
            dynamic dataProperty = dataPropertyClass(json);

            // Assert
            Assert.AreEqual("TestProperty", dataProperty.name);
            Assert.AreEqual(123, dataProperty.value);
        }

        [Test]
        public void Constructor_WithValidJsonDictionary_ShouldInitializeProperties()
        {
            // Arrange
            var pythonDict = _engine.Execute("dict(name='TestProperty', value=123)", _scope);

            // Act
            dynamic dataProperty = dataPropertyClass(pythonDict);

            // Assert
            Assert.AreEqual("TestProperty", dataProperty.name);
            Assert.AreEqual(123, dataProperty.value);
        }

        [Test]
        public void Constructor_WithInvalidJsonString_ShouldThrowJsonException()
        {
            // Arrange
            string invalidJson = "{invalid json}";

            // Act & Assert
            var ex = Assert.Throws<ValueErrorException>(() => dataPropertyClass(invalidJson));
            Assert.That(ex.Message, Does.Contain("Expecting property name enclosed in double quotes"));
        }

        [Test]
        public void Constructor_WithInvalidJsonType_ShouldThrowTypeError()
        {
            // Arrange
            var invalidInput = 12345;

            // Act & Assert
            var ex = Assert.Throws<TypeErrorException>(() => dataPropertyClass(invalidInput));
            Assert.That(ex.Message, Does.Contain("Argument j supplied must be of type string or type dictionary."));
        }

        [Test]
        public void Constructor_WithMissingNameProperty_ShouldSetDefaultName()
        {
            // Arrange
            string json = "{\"value\": 123}";

            // Act
            dynamic dataProperty = dataPropertyClass(json);

            // Assert
            Assert.AreEqual("-", dataProperty.name);
            Assert.AreEqual(123, dataProperty.value);
        }

        [Test]
        public void Constructor_WithMissingValueProperty_ShouldSetDefaultValue()
        {
            // Arrange
            string json = "{\"name\": \"TestProperty\"}";

            // Act
            dynamic dataProperty = dataPropertyClass(json);
           
            // Assert
            Assert.AreEqual("TestProperty", dataProperty.name);
            Assert.AreEqual(null, dataProperty.value);
        }

        [Test]
        public void Constructor_WithInvalidNameType_ShouldThrowTypeError()
        {
            // Arrange
            var pythonDict = _engine.Execute("dict(name=1234, value=789)", _scope);

            // Act & Assert
            var ex = Assert.Throws < ValueErrorException > (() => dataPropertyClass(pythonDict));
            Assert.That(ex.Message, Does.Contain("failed to initialise"));
        }

        [Test]
        public void Constructor_WithValidJsonObject_ShouldInitializeCorrectly()
        {
            // Arrange
            var pythonDict = _engine.Execute("dict(name='PropertyName', value=789)", _scope);

            // Act
            dynamic dataProperty = dataPropertyClass(pythonDict);

            // Assert
            Assert.AreEqual("PropertyName", dataProperty.name);
            Assert.AreEqual(789, dataProperty.value);
        }

        [Test]
        public void DefaultConstructor_ShouldSetDefaultValues()
        {
            // Arrange & Act
            dynamic dataProperty = dataPropertyClass();

            // Assert
            Assert.AreEqual("-", dataProperty.name); // default name
            Assert.IsNull(dataProperty.value);       // default value
        }

    }
}
