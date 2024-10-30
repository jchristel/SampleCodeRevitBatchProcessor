using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Scripting.Hosting;
using IronPython.Runtime.Exceptions;

namespace PythonTests
{
    public class DataGeometryBaseTests
    {
        ScriptEngine _engine;
        ScriptScope _scope;

        dynamic dataGeometryBaseClass;
        dynamic point3Class;
        dynamic matrixClass;

        [SetUp]
        public void Setup()
        {
            // get a python engine
            ScriptEngine engine = PythonRunner.SetupEngine();
            _scope = engine.CreateScope();

            // get the repository path
            string repoPath = PythonRunner.GetRepositoryPath();

            // set path to data geometry base
            var pythonFilePath_dataGeometryBase = Path.Combine(repoPath, @"duHast\Data\Objects\Properties\Geometry\geometry_base.py");
            
            // set path to matrix class
            var pythonFilePath_matrix = Path.Combine(repoPath, @"duHast\Geometry\matrix.py");
            // set path to point3 class
            var pythonFilePath_point3 = Path.Combine(repoPath, @"duHast\Geometry\point_3.py");

            //run the file
            engine.ExecuteFile(pythonFilePath_point3, _scope);
            //run the file
            engine.ExecuteFile(pythonFilePath_matrix, _scope);
            //run the file
            engine.ExecuteFile(pythonFilePath_dataGeometryBase, _scope);
            
            dataGeometryBaseClass = _scope.GetVariable("DataGeometryBase");
            point3Class = _scope.GetVariable("Point3");
            matrixClass = _scope.GetVariable("Matrix");

            //store the engine instance
            _engine = engine;
        }

        [Test]
        public void Constructor_WithValidDataType_ShouldSetDataTypeCorrectly()
        {
            // Arrange
            string dataType = "geometry_data";

            // Act
            dynamic instance = dataGeometryBaseClass(dataType);

            // Assert
            Assert.AreEqual(dataType, instance.DataType);
        }

        [Test]
        public void Constructor_WithDefaultValues_ShouldInitializeWithDefaultTranslationAndRotation()
        {
            // Arrange
            string dataType = "geometry_data";

            // Act
            dynamic instance = dataGeometryBaseClass(dataType);

            // Assert
            Assert.IsInstanceOf(point3Class, instance.translation_coord);
            Assert.AreEqual(0.0, instance.translation_coord.x);
            Assert.AreEqual(0.0, instance.translation_coord.y);
            Assert.AreEqual(0.0, instance.translation_coord.z);

            Assert.IsInstanceOf(matrixClass, instance.rotation_coord);
            Assert.AreEqual(3, instance.rotation_coord.rows);
            Assert.AreEqual(3, instance.rotation_coord.columns);
        }

        [Test]
        public void Constructor_WithValidJson_ShouldSetTranslationAndRotationFromJson()
        {
            // Arrange
            string dataType = "geometry_data";

            // Define JSON-formatted string
            string json = @"
            {
                ""translation_coord"": { ""x"": 1.1, ""y"": 2.2, ""z"": 3.3 },
                ""rotation_coord"": { ""rows"": 3, ""columns"": 3 }
            }";

            // Act
            dynamic instance = dataGeometryBaseClass(dataType, json);

            // Act & Assert
            Assert.AreEqual(1.1, instance.translation_coord.x);
            Assert.AreEqual(2.2, instance.translation_coord.y);
            Assert.AreEqual(3.3, instance.translation_coord.z);
            Assert.AreEqual(3, instance.rotation_coord.rows);
            Assert.AreEqual(3, instance.rotation_coord.columns);
        }

        [Test]
        public void Constructor_WithInvalidJson_ShouldThrowTypeError()
        {
            // Arrange
            string dataType = "geometry_data";

            // Act & Assert
            Assert.Throws<ValueErrorException>(() => dataGeometryBaseClass(dataType, "invalid_json"));
        }

        [Test]
        public void Constructor_WithNullJson_ShouldUseDefaultValues()
        {
            // Arrange
            string dataType = "geometry_data";

            // Act
            dynamic instance = dataGeometryBaseClass(dataType, null);

            // Assert
            Assert.IsInstanceOf(point3Class, instance.translation_coord);
            Assert.IsInstanceOf(matrixClass, instance.rotation_coord);
        }
    }
}
