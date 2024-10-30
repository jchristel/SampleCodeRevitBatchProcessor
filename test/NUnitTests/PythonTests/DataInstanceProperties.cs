using System;
using Microsoft.Scripting.Hosting;
using IronPython.Runtime.Exceptions;

namespace PythonTests
{
    public class DataInstanceProperties
    {
        ScriptEngine _engine;
        ScriptScope _scope;

        private dynamic _dataInstancePropertiesClass;
        private dynamic _dataPropertyClass;

        [SetUp]
        public void Setup()
        {
            // get a python engine
            ScriptEngine engine = PythonRunner.SetupEngine();
            _scope = engine.CreateScope();

            // get the repository path
            string repoPath = PythonRunner.GetRepositoryPath();

            // set path to bounding box 2 class
            var pythonFilePath_data_instance_properties = Path.Combine(repoPath, @"duHast\Data\Objects\Properties\data_instance_properties.py");
            // set path to point2 class
            var pythonFilePath_data_property = Path.Combine(repoPath, @"duHast\Data\Objects\Properties\data_property.py");

            //run the file
            engine.ExecuteFile(pythonFilePath_data_instance_properties, _scope);
            //run the file
            engine.ExecuteFile(pythonFilePath_data_property, _scope);

            _dataInstancePropertiesClass = _scope.GetVariable("DataInstanceProperties");
            _dataPropertyClass = _scope.GetVariable("DataProperty");

            //store the engine instance
            _engine = engine;
        }

        [Test]
        public void Constructor_WithValidPythonDictionary_ShouldSetPropertiesCorrectly()
        {
            // Arrange: Create a JSON-like dictionary structure with id and properties
            var jsonDict = _engine.Execute(@"{'id': 123,'properties': [{'name': 'Property1', 'value': 456},{'name': 'Property2', 'value': 'TestValue'}]}", _scope);

            // Act: Instantiate the DataInstanceProperties object with the dictionary
            dynamic dataInstanceProperties = _dataInstancePropertiesClass(jsonDict);

            // Assert: Check if 'id' and 'properties' were set correctly
            Assert.AreEqual(123, dataInstanceProperties.id);

            // Check properties list contents
            var properties = dataInstanceProperties.properties;
            Assert.AreEqual(2, properties.Count);

            // First property checks
            Assert.AreEqual("Property1", properties[0].name);
            Assert.AreEqual(456, properties[0].value);

            // Second property checks
            Assert.AreEqual("Property2", properties[1].name);
            Assert.AreEqual("TestValue", properties[1].value);
        }

        [Test]
        public void Constructor_WithInvalidId_ShouldThrowTypeError()
        {
            // Arrange: Pass a string as 'id' to induce a TypeError
            var invalidJsonDict = _engine.Execute(@"{'id': 'InvalidId','properties': []}", _scope);

            // Act & Assert: Expect an exception due to invalid 'id' type
            var ex = Assert.Throws<TypeErrorException>(() =>
            {
                var dataInstanceProperties = _dataInstancePropertiesClass(invalidJsonDict);
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
                var dataInstanceProperties = _dataInstancePropertiesClass(invalidInput);
            });

            Assert.That(ex.Message, Does.Contain("Argument j supplied must be of type string or type dictionary"));
        }
    }
}
