using IronPython.Runtime.Exceptions;
using PythonTests.Setup;

namespace PythonTests.GeometryTests
{
    public class BoundingBoxBase
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.BoundingBoxBaseClass, Is.Not.Null, "BoundingBoxBase should be loaded.");
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
            Assert.That(instance.json_ini, Is.Not.Null);
            Assert.That(1.1,Is.EqualTo( instance.json_ini["min_x"]));
            Assert.That(2.2, Is.EqualTo(instance.json_ini["min_y"]));
            Assert.That(3.3, Is.EqualTo(instance.json_ini["max_x"]));
            Assert.That(4.4, Is.EqualTo(instance.json_ini["max_y"]));
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
            Assert.That(instance.json_ini, Is.Null);
            Assert.That(0.0, Is.EqualTo(instance.min_x));
            Assert.That(0.0, Is.EqualTo(instance.max_x));
            Assert.That(0.0, Is.EqualTo(instance.min_y));
            Assert.That(0.0, Is.EqualTo(instance.max_y));
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

        [Test]
        public void Width_ShouldRaiseNotImplementedError()
        {
            // Arrange
            dynamic instance = PythonEngineManager.BoundingBoxBaseClass();

            // Act & Assert
            var ex = Assert.Throws<System.NotImplementedException>(() => instance.width());
            Assert.That(ex.Message, Does.Contain("Subclasses should implement this method"));
        }

        [Test]
        public void Depth_ShouldRaiseNotImplementedError()
        {
            // Arrange
            dynamic instance = PythonEngineManager.BoundingBoxBaseClass();

            // Act & Assert
            var ex = Assert.Throws<System.NotImplementedException>(() => instance.depth());
            Assert.That(ex.Message, Does.Contain("Subclasses should implement this method"));
        }

        [Test]
        public void Ratio_ShouldRaiseNotImplementedError()
        {
            // Arrange
            dynamic instance = PythonEngineManager.BoundingBoxBaseClass();

            // Act & Assert
            var ex = Assert.Throws<System.NotImplementedException>(() => instance.ratio());
            Assert.That(ex.Message, Does.Contain("Subclasses should implement this method"));
        }

        [Test]
        public void EqualityOperator_ShouldCompareBoundingBoxes()
        {
            // Arrange
            string json1 = @"{ ""min_x"": 1.1, ""min_y"": 2.2, ""max_x"": 3.3, ""max_y"": 4.4 }";
            string json2 = @"{ ""min_x"": 1.1, ""min_y"": 2.2, ""max_x"": 3.3, ""max_y"": 4.4 }";

            dynamic instance1 = PythonEngineManager.BoundingBoxBaseClass(json1);
            dynamic instance2 = PythonEngineManager.BoundingBoxBaseClass(json2);

            // Act
            bool areEqual = instance1 == instance2;

            // Assert
            Assert.That(areEqual, Is.True, "Instances with identical properties should be equal.");
        }
    }
}
