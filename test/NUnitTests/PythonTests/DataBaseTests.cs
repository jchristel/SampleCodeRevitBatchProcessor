using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Scripting.Hosting;
using IronPython.Runtime.Exceptions;

namespace PythonTests
{
    public class DataBaseTests
    {
        ScriptEngine _engine;
        ScriptScope _scope;

        private dynamic _dataBaseClass;

        [SetUp]
        public void Setup()
        {
            // get a python engine
            ScriptEngine engine = PythonRunner.SetupEngine();
            _scope = engine.CreateScope();

            // get the repository path
            string repoPath = PythonRunner.GetRepositoryPath();

            // set path to bounding box 2 class
            var pythonFilePath_dataBase = Path.Combine(repoPath, @"duHast\Data\Objects\data_base.py");

            //run the file
            engine.ExecuteFile(pythonFilePath_dataBase, _scope);

            _dataBaseClass = _scope.GetVariable("DataBase");

            //store the engine instance
            _engine = engine;
        }


        [Test]
        public void Constructor_WithValidDataType_ShouldSetDataTypeCorrectly()
        {
            // Arrange
            string dataType = "example_type";

            // Act
            dynamic instance = _dataBaseClass(dataType);
            
            // Assert
            Assert.AreEqual(dataType, instance.DataType);
        }

        [Test]
        public void DataType_Property_ShouldReturnCorrectDataType()
        {
            // Arrange
            string dataType = "test_type";
            dynamic instance = _dataBaseClass(dataType);

            // Act
            string result = instance.DataType;

            // Assert
            Assert.That(result, Is.EqualTo("test_type"));
        }

        [Test]
        public void Constructor_WithEmptyStringDataType_ShouldSetDataTypeCorrectly()
        {
            // Arrange
            string dataType = "";

            // Act
            dynamic instance = _dataBaseClass(dataType);

            // Assert
            Assert.AreEqual(dataType, instance.DataType);
        }

        [Test]
        public void Constructor_WithNullDataType_ShouldThrowTypeError()
        {
            // Act & Assert
            var ex=Assert.Throws<TypeErrorException>(() => _dataBaseClass(null));
            Assert.That(ex.Message, Does.Contain("data_type must be a string, got"));
        }
    }
}
