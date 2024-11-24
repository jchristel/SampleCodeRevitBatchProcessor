using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;


namespace PythonTests.DataTests.PropertyTests.GeometryTests
{

    public class DataGeometryBaseTests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.DataGeometryBaseClass, Is.Not.Null, "DataGeometryBase should be loaded.");
            Assert.That(PythonEngineManager.Point3Class, Is.Not.Null, "Point3Class should be loaded.");
            Assert.That(PythonEngineManager.MatrixClass, Is.Not.Null, "MatrixClass should be loaded.");
        }

        [Test]
        public void Constructor_WithValidDataType_ShouldSetDataTypeCorrectly()
        {
            // Arrange
            string dataType = "geometry_data";

            // Act
            dynamic instance = PythonEngineManager.DataGeometryBaseClass(dataType);

            // Assert
            Assert.That(dataType,Is.EqualTo( instance.DataType));
        }

        [Test]
        public void Constructor_WithDefaultValues_ShouldInitializeWithDefaultTranslationAndRotation()
        {
            // Arrange
            string dataType = "geometry_data";

            // Act
            dynamic instance = PythonEngineManager.DataGeometryBaseClass(dataType);

            // Assert
            Assert.That(instance.translation_coord, Is.InstanceOf(PythonEngineManager.Point3Class));
            Assert.That(0.0, Is.EqualTo(instance.translation_coord.x));
            Assert.That(0.0, Is.EqualTo(instance.translation_coord.y));
            Assert.That(0.0, Is.EqualTo(instance.translation_coord.z));

            Assert.That(instance.rotation_coord, Is.InstanceOf(PythonEngineManager.MatrixClass));
            Assert.That(3, Is.EqualTo(instance.rotation_coord.rows));
            Assert.That(3, Is.EqualTo(instance.rotation_coord.columns));
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

            Console.WriteLine(instance.to_json());

            // Act & Assert
            Assert.That(1.1, Is.EqualTo(instance.translation_coord.x));
            Assert.That(2.2, Is.EqualTo(instance.translation_coord.y));
            Assert.That(3.3, Is.EqualTo(instance.translation_coord.z));
            Assert.That(3, Is.EqualTo(instance.rotation_coord.rows));
            Assert.That(3, Is.EqualTo(instance.rotation_coord.columns));
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
            Assert.That(instance.translation_coord, Is.InstanceOf(PythonEngineManager.Point3Class));
            Assert.That(instance.rotation_coord, Is.InstanceOf(PythonEngineManager.MatrixClass));
        }

        [Test]
        public void EqualInstances_ShouldReturnTrue()
        {
            // JSON representation with identical translation and rotation coordinates
            var jsonString = JsonConvert.SerializeObject(new
            {
                translation_coord = new { x = 1.0, y = 2.0, z = 3.0 },
                rotation_coord = new
                {
                    data = new[] { new[] { 1.0, 0.0, 0.0 }, new[] { 0.0, 1.0, 0.0 }, new[] { 0.0, 0.0, 1.0 } },
                    rows = 3,
                    columns = 3
                }
            });

            Console.WriteLine(jsonString);

            // Initialize two instances with the same JSON data
            var dataGeometryA = PythonEngineManager.DataGeometryBaseClass("geometry_type", jsonString);
            var dataGeometryB = PythonEngineManager.DataGeometryBaseClass("geometry_type", jsonString);

            // Assert that the two instances are equal
            Assert.That(dataGeometryA == dataGeometryB, Is.True, "Expected equal instances to return true.");
        }

        [Test]
        public void UnequalInstances_ShouldReturnFalse()
        {
            // JSON representation for first instance
            var jsonStringA = JsonConvert.SerializeObject(new
            {
                translation_coord = new { x = 1.0, y = 2.0, z = 3.0 },
                rotation_coord = new
                {
                    data = new[] { new[] { 1.0, 0.0, 0.0 }, new[] { 0.0, 1.0, 0.0 }, new[] { 0.0, 0.0, 1.0 } },
                    rows = 3,
                    columns = 3
                }
            });

            // JSON representation for second instance with different translation
            var jsonStringB = JsonConvert.SerializeObject(new
            {
                translation_coord = new { x = 4.0, y = 5.0, z = 6.0 },
                rotation_coord = new
                {
                    data = new[] { new[] { 1.0, 0.0, 0.0 }, new[] { 0.0, 1.0, 0.0 }, new[] { 0.0, 0.0, 1.0 } },
                    rows = 3,
                    columns = 3
                }

            });

            Console.WriteLine(jsonStringA);
            Console.WriteLine(jsonStringB);

            // Initialize two instances with different JSON data
            var dataGeometryA = PythonEngineManager.DataGeometryBaseClass("geometry_type", jsonStringA);
            var dataGeometryB = PythonEngineManager.DataGeometryBaseClass("geometry_type", jsonStringB);

            // Assert that the two instances are not equal
            Assert.That(dataGeometryA == dataGeometryB, Is.False, "Expected unequal instances to return false.");
        }

        [Test]
        public void UnequalRotation_ShouldReturnFalse()
        {
            // JSON representation for first instance
            var jsonStringA = JsonConvert.SerializeObject(new
            {
                translation_coord = new { x = 1.0, y = 2.0, z = 3.0 },
                rotation_coord = new
                {
                    data = new[] { new[] { 1.0, 0.0, 0.0 }, new[] { 0.0, 1.0, 0.0 }, new[] { 0.0, 0.0, 1.0 } },
                    rows = 3,
                    columns = 3
                }
            });

            // JSON representation for second instance with different rotation
            var jsonStringB = JsonConvert.SerializeObject(new
            {
                translation_coord = new { x = 1.0, y = 2.0, z = 3.0 },
                rotation_coord = new
                {
                    data = new[] { new[] { 0.0, 1.0, 0.0 }, new[] { 1.0, 0.0, 0.0 }, new[] { 0.0, 0.0, 1.0 } },
                    rows = 3,
                    columns = 3
                }
            });

            // Initialize two instances with different rotation matrices
            var dataGeometryA = PythonEngineManager.DataGeometryBaseClass("geometry_type", jsonStringA);
            var dataGeometryB = PythonEngineManager.DataGeometryBaseClass("geometry_type", jsonStringB);

            // Assert that the two instances are not equal due to different rotation coordinates
            Assert.That(dataGeometryA == dataGeometryB, Is.False, "Expected instances with different rotations to be unequal.");
        }

        [Test]
        public void NullComparison_ShouldReturnFalse()
        {
            // JSON representation for instance
            var jsonString = JsonConvert.SerializeObject(new
            {
                translation_coord = new { x = 1.0, y = 2.0, z = 3.0 },
                rotation_coord = new
                {
                    data = new[] { new[] { 0.0, 1.0, 0.0 }, new[] { 1.0, 0.0, 0.0 }, new[] { 0.0, 0.0, 1.0 } },
                    rows = 3,
                    columns = 3
                }
            });

            // Initialize instance with JSON data
            var dataGeometry = PythonEngineManager.DataGeometryBaseClass("geometry_type", jsonString);

            // Assert that the instance is not equal to null
            Assert.That(dataGeometry == null, Is.False, "Expected instance comparison with null to be false.");
        }
    }
}
