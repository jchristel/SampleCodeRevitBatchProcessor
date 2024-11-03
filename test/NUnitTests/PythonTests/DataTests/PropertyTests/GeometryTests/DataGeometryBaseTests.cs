using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Scripting.Hosting;
using IronPython.Runtime.Exceptions;
using PythonTests.Setup;


namespace PythonTests
{

    public class DataGeometryBaseTests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.IsNotNull(PythonEngineManager.DataGeometryBaseClass, "DataGeometryBase should be loaded.");
            Assert.IsNotNull(PythonEngineManager.Point3Class, "Point3Class should be loaded.");
            Assert.IsNotNull(PythonEngineManager.MatrixClass, "MatrixClass should be loaded.");
        }

        [Test]
        public void Constructor_WithValidDataType_ShouldSetDataTypeCorrectly()
        {
            // Arrange
            string dataType = "geometry_data";

            // Act
            dynamic instance = PythonEngineManager.DataGeometryBaseClass(dataType);

            // Assert
            Assert.AreEqual(dataType, instance.DataType);
        }

        [Test]
        public void Constructor_WithDefaultValues_ShouldInitializeWithDefaultTranslationAndRotation()
        {
            // Arrange
            string dataType = "geometry_data";

            // Act
            dynamic instance = PythonEngineManager.DataGeometryBaseClass(dataType);

            // Assert
            Assert.IsInstanceOf(PythonEngineManager.Point3Class, instance.translation_coord);
            Assert.AreEqual(0.0, instance.translation_coord.x);
            Assert.AreEqual(0.0, instance.translation_coord.y);
            Assert.AreEqual(0.0, instance.translation_coord.z);

            Assert.IsInstanceOf(PythonEngineManager.MatrixClass, instance.rotation_coord);
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
            dynamic instance = PythonEngineManager.DataGeometryBaseClass(dataType, json);

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
            Assert.Throws<ValueErrorException>(() => PythonEngineManager.DataGeometryBaseClass(dataType, "invalid_json"));
        }

        [Test]
        public void Constructor_WithNullJson_ShouldUseDefaultValues()
        {
            // Arrange
            string dataType = "geometry_data";

            // Act
            dynamic instance = PythonEngineManager.DataGeometryBaseClass(dataType, null);

            // Assert
            Assert.IsInstanceOf(PythonEngineManager.Point3Class, instance.translation_coord);
            Assert.IsInstanceOf(PythonEngineManager.MatrixClass, instance.rotation_coord);
        }
    }
}
