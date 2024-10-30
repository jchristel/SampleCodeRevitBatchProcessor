using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Scripting.Hosting;
using IronPython.Runtime.Exceptions;

namespace PythonTests
{
    public class BoundingBoxBase
    {
        ScriptEngine _engine;
        ScriptScope _scope;

        private dynamic boundingBoxBaseClass;
           
        [SetUp]
        public void Setup()
        {
            // get a python engine
            ScriptEngine engine = PythonRunner.SetupEngine();
            _scope = engine.CreateScope();

            // get the repository path
            string repoPath = PythonRunner.GetRepositoryPath();

            // set path to bounding box base class
            var pythonFilePath_bbox2 = Path.Combine(repoPath, @"duHast\Geometry\bounding_box_base.py");
                
            //run the file
            engine.ExecuteFile(pythonFilePath_bbox2, _scope);
                
            boundingBoxBaseClass = _scope.GetVariable("BoundingBoxBase");
                
            //store the engine instance
            _engine = engine;
        }


        [Test]
        public void Constructor_WithValidJson_ShouldSetJsonIni()
        {
            // Arrange
            string json = @"
            {
                ""point1"": { ""x"": 1.1, ""y"": 2.2 },
                ""point2"": { ""x"": 3.3, ""y"": 4.4 }
            }";

            // Act
            dynamic instance = boundingBoxBaseClass(json);

            // Assert
            Assert.IsNotNull(instance.json_ini);
            Assert.AreEqual(1.1, instance.json_ini["point1"]["x"]);
            Assert.AreEqual(2.2, instance.json_ini["point1"]["y"]);
            Assert.AreEqual(3.3, instance.json_ini["point2"]["x"]);
            Assert.AreEqual(4.4, instance.json_ini["point2"]["y"]);
        }

        [Test]
        public void Constructor_WithInvalidJson_ShouldThrowValueError()
        {
            // Arrange
            string invalidJson = @"{ ""invalid_key"": {} }";

            // Act & Assert
            var ex = Assert.Throws<ValueErrorException>(() => boundingBoxBaseClass(invalidJson));
            Assert.IsTrue(ex.Message.Contains("JSON must contain 'point1' and 'point2' keys."));
        }

        [Test]
        public void Constructor_WithNonDictionaryJson_ShouldThrowTypeError()
        {
            // Arrange
            string invalidJson = "[1, 2, 3]";

            // Act & Assert
            var ex = Assert.Throws<ValueErrorException>(() => boundingBoxBaseClass(invalidJson));
            Console.WriteLine(ex.Message);
            Assert.IsTrue(ex.Message.Contains("JSON must contain"));
        }

        [Test]
        public void Constructor_WithoutJson_ShouldInitializeDefaultValues()
        {
            // Act
            dynamic instance = boundingBoxBaseClass();

            // Assert
            Assert.IsNull(instance.json_ini);
            Assert.AreEqual(double.PositiveInfinity, instance.min_x);
            Assert.AreEqual(double.NegativeInfinity, instance.max_x);
            Assert.AreEqual(double.PositiveInfinity, instance.min_y);
            Assert.AreEqual(double.NegativeInfinity, instance.max_y);
        }

        [Test]
        public void Contains_ShouldRaiseNotImplementedError()
        {
            // Arrange
            dynamic instance = boundingBoxBaseClass();

            // Act & Assert
            var ex = Assert.Throws<ValueErrorException>(() => instance.contains(new { x = 0, y = 0 }));
            Assert.IsTrue(ex.Message.Contains("Subclasses should implement this method"));
        }

        [Test]
        public void ToString_ShouldReturnExpectedFormat()
        {
            // Arrange
            dynamic instance = boundingBoxBaseClass();

            // Act
            string result = instance.ToString();

            // Assert
            Assert.AreEqual("BoundingBoxBase(inf, inf, -inf, -inf)", result);
        }
    }
}
