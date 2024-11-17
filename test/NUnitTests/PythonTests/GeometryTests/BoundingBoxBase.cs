using IronPython.Runtime.Exceptions;
using PythonTests.Setup;

namespace PythonTests.GeometryTests
{
    public class BoundingBoxBase
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.IsNotNull(PythonEngineManager.BoundingBoxBaseClass, "BoundingBoxBase should be loaded.");
        }


        [Test]
        public void Constructor_WithValidJson_ShouldSetJsonIni()
        {
            // Arrange
            string json = @"{ ""min_x"": 1.1, ""min_y"": 2.2, ""max_x"": 3.3, ""max_y"": 4.4 }";

            Console.WriteLine(json);

            // Act
            dynamic instance = PythonEngineManager.BoundingBoxBaseClass(json);
            

            // Assert
            Assert.IsNotNull(instance.json_ini);
            Assert.AreEqual(1.1, instance.json_ini["min_x"]);
            Assert.AreEqual(2.2, instance.json_ini["min_y"]);
            Assert.AreEqual(3.3, instance.json_ini["max_x"]);
            Assert.AreEqual(4.4, instance.json_ini["max_y"]);
        }

        [Test]
        public void Constructor_WithInvalidJson_ShouldThrowValueError()
        {
            // Arrange
            string invalidJson = @"{ ""invalid_key"": {} }";

            // Act & Assert
            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.BoundingBoxBaseClass(invalidJson));
            Assert.That(ex.Message, Does.Contain("JSON must contain 'max_x', 'max_y', 'min_x', 'min_y' keys."));
        }

        [Test]
        public void Constructor_WithNonDictionaryJson_ShouldThrowTypeError()
        {
            // Arrange
            string invalidJson = "[1, 2, 3]";

            // Act & Assert
            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.BoundingBoxBaseClass(invalidJson));
            Console.WriteLine(ex.Message);
            Assert.That(ex.Message, Does.Contain("JSON must contain"));
        }

        [Test]
        public void Constructor_WithoutJson_ShouldInitializeDefaultValues()
        {
            // Act
            dynamic instance = PythonEngineManager.BoundingBoxBaseClass();

            // Assert
            Assert.IsNull(instance.json_ini);
            Assert.AreEqual(0.0, instance.min_x);
            Assert.AreEqual(0.0, instance.max_x);
            Assert.AreEqual(0.0, instance.min_y);
            Assert.AreEqual(0.0, instance.max_y);
        }

        [Test]
        public void Contains_ShouldRaiseNotImplementedError()
        {
            // Arrange
            dynamic instance = PythonEngineManager.BoundingBoxBaseClass();

            // Act & Assert
            var ex = Assert.Throws<System.NotImplementedException>(() => instance.contains(new { x = 0, y = 0 }));
            Assert.That(ex.Message, Does.Contain("Subclasses should implement this method"));
        }

        [Test]
        public void ToString_ShouldReturnExpectedFormat()
        {
            // Arrange
            dynamic instance = PythonEngineManager.BoundingBoxBaseClass();

            // Act
            string result = instance.__str__();

            // Assert
            Assert.That(result, Is.EqualTo("BoundingBoxBase(0.0, 0.0, 0.0, 0.0)"));
        }
    }
}
