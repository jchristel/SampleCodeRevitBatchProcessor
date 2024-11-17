using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;

namespace PythonTests.DataTests.PropertyTests.GeometryTests
{
    public class DataGeometryBoundingBox2
    {
        private string validJsonString;
        private Dictionary<string, object> validJsonDictionary;



        [SetUp]
        public void SetUp()
        {
            // Sample valid JSON for testing
            validJsonDictionary = new Dictionary<string, object>
            {
                { "min_x", 1.1 },
                { "max_x", 3.3 },
                { "min_y", 2.2 },
                { "max_y", 4.4}
            };

            validJsonString = JsonConvert.SerializeObject(validJsonDictionary);
        }
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.IsNotNull(PythonEngineManager.DataGeometryBoundingBox2Class, "DataGeometryBoundingBox2 should be loaded.");
            Assert.IsNotNull(PythonEngineManager.Point2Class, "Point2Class should be loaded.");
        }

        [Test]
        public void Constructor_WithValidJson_ShouldSetBoundingBox()
        {
            // Act
            dynamic instance = PythonEngineManager.DataGeometryBoundingBox2Class(validJsonString);

            // Assert
            Assert.AreEqual(1.1, instance.min_x);
            Assert.AreEqual(2.2, instance.min_y);
            Assert.AreEqual(3.3, instance.max_x);
            Assert.AreEqual(4.4, instance.max_y);
        }

        [Test]
        public void Constructor_WithInvalidJson_ShouldThrowValueError ()
        {
            // Arrange
            validJsonDictionary = new Dictionary<string, object>
            {
                { "invalid_key", 1.1 }
            };
            string invalidJson = JsonConvert.SerializeObject(validJsonDictionary);

            // Act & Assert
            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.DataGeometryBoundingBox2Class(invalidJson));
            Assert.That(ex.Message, Does.Contain("JSON must contain 'max_x', 'max_y', 'min_x', 'min_y' keys"));
        }

        [Test]
        public void Constructor_WithNonDictionaryJson_ShouldThrowValueError()
        {
            // Arrange
            string invalidJson = "[1, 2, 3]";

            // Act & Assert
            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.DataGeometryBoundingBox2Class(invalidJson));
            Assert.That(ex.Message, Does.Contain("JSON must contain 'max_x', 'max_y', 'min_x', 'min_y' keys"));
        }

        [Test]
        public void SetBoundingBoxByPoints_WithValidPoints_ShouldUpdateBoundingBox()
        {
            // Arrange
            dynamic instance = PythonEngineManager.DataGeometryBoundingBox2Class();
            dynamic minPoint = PythonEngineManager.Point2Class(5.5, 6.6);
            dynamic maxPoint = PythonEngineManager.Point2Class(7.7, 8.8);

            // Act
            instance.update(minPoint, maxPoint);

            Console.WriteLine(instance.to_json());

            // Assert
            Assert.AreEqual(5.5, instance.min_x);
            Assert.AreEqual(6.6, instance.min_y);
            Assert.AreEqual(7.7, instance.max_x);
            Assert.AreEqual(8.8, instance.max_y);
        }

        [Test]
        public void SetBoundingBoxByPoints_WithInvalidMin_ShouldThrowTypeError()
        {
            // Arrange
            dynamic instance = PythonEngineManager.DataGeometryBoundingBox2Class();
            dynamic maxPoint = PythonEngineManager.Point2Class(7.7, 8.8);

            // Act & Assert
            var ex = Assert.Throws<TypeErrorException>(() => instance.update("invalid", maxPoint));
            Assert.That(ex.Message, Does.Contain("point1 expected Point2 instance"));
        }

        [Test]
        public void SetBoundingBoxByPoints_WithInvalidMax_ShouldThrowTypeError()
        {
            // Arrange
            dynamic instance = PythonEngineManager.DataGeometryBoundingBox2Class();
            dynamic minPoint = PythonEngineManager.Point2Class(5.5, 6.6);

            // Act & Assert
            var ex = Assert.Throws<TypeErrorException>(() => instance.update(minPoint, "invalid"));
            Assert.That(ex.Message, Does.Contain("point2 expected Point2 instance"));
        }

        [Test]
        public void EqualInstances_ShouldReturnTrue()
        {
            // JSON representation with identical bounding box min and max coordinates
            var jsonString = JsonConvert.SerializeObject(new
            {
                    min_x = 5.5,
                    max_x = 7.7,
                    min_y = 6.6,
                    max_y = 8.8
            });

            Console.WriteLine(jsonString);

            // Initialize two instances with the same JSON data
            var dataGeometryA = PythonEngineManager.DataGeometryBoundingBox2Class(jsonString);
            var dataGeometryB = PythonEngineManager.DataGeometryBoundingBox2Class(jsonString);

            // Assert that the two instances are equal
            Assert.IsTrue(dataGeometryA == dataGeometryB, "Expected equal instances to return true.");
        }

        [Test]
        public void NotEqualInstances_ShouldReturnTrue()
        {
            // JSON representation for the second instance with different bounding box coordinates
            var jsonStringB = JsonConvert.SerializeObject(new
            {
                
                    min_x = 4.0,
                    max_x = 6.5,
                    min_y = 3.3,
                    max_y = 9.0
               
            });

            Console.WriteLine($"jsonStringB: {jsonStringB}");

            // Initialize two instances with different JSON data
            var dataGeometryA = PythonEngineManager.DataGeometryBoundingBox2Class(validJsonString);
            var dataGeometryB = PythonEngineManager.DataGeometryBoundingBox2Class(jsonStringB);

            // Assert that the two instances are not equal
            Assert.IsTrue(dataGeometryA != dataGeometryB, "Expected instances with different data to return true for inequality.");
        }

        [Test]
        public void EqualOperator_WithIdenticalBoundingBox_ShouldReturnTrue()
        { 
            // Initialize two instances with the same JSON data
            var dataGeometryA = PythonEngineManager.DataGeometryBoundingBox2Class(validJsonString);
            var dataGeometryB = PythonEngineManager.DataGeometryBoundingBox2Class(validJsonString);

            // Assert that the '==' operator returns true for equal instances
            Assert.IsTrue(dataGeometryA == dataGeometryB, "Expected '==' to return true for identical bounding boxes.");
        }

        [Test]
        public void NotEqualOperator_WithDifferentBoundingBox_ShouldReturnTrue()
        {
           

            // JSON representation for the second instance with different bounding box coordinates
            var jsonStringB = JsonConvert.SerializeObject(new
            {
                
                    min_x = 3.0,
                    max_x = 4.0,
                    min_y = 1.5,
                    max_y = 5.5
                
            });

            // Initialize two instances with different JSON data
            var dataGeometryA = PythonEngineManager.DataGeometryBoundingBox2Class(validJsonString);
            var dataGeometryB = PythonEngineManager.DataGeometryBoundingBox2Class(jsonStringB);

            // Assert that the '!=' operator returns true for non-equal instances
            Assert.IsFalse(dataGeometryA == dataGeometryB, "Expected '!=' to return true for different bounding boxes.");
        }
    }
}
