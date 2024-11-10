using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;

namespace PythonTests.DataTests.PropertyTests.GeometryTests
{
    public class DataGeometryBoundingBox2
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.IsNotNull(PythonEngineManager.DataGeometryBoundingBox2Class, "DataGeometryBoundingBox2 should be loaded.");
            Assert.IsNotNull(PythonEngineManager.Point2Class, "Point2Class should be loaded.");
        }

        [Test]
        public void Constructor_WithValidJson_ShouldSetBoundingBox()
        {
            // Arrange
            string json = @"{""bounding_box"":{ ""min_x"": 1.1, ""min_y"": 2.2, ""max_x"": 3.3, ""max_y"": 4.4 }}";

            // Act
            dynamic instance = PythonEngineManager.DataGeometryBoundingBox2Class(json);

            // Assert
            Assert.AreEqual(1.1, instance.bounding_box.min_x);
            Assert.AreEqual(2.2, instance.bounding_box.min_y);
            Assert.AreEqual(3.3, instance.bounding_box.max_x);
            Assert.AreEqual(4.4, instance.bounding_box.max_y);
        }

        [Test]
        public void Constructor_WithInvalidJson_ShouldUseDefaultBoundingBox()
        {
            // Arrange
            string invalidJson = @"{ ""invalid_key"": {} }";

            // Act
            dynamic instance = PythonEngineManager.DataGeometryBoundingBox2Class(invalidJson);

            // Assert - Default bounding box points should be 0.0, 0.0
            Assert.AreEqual(0.0, instance.bounding_box.min_x);
            Assert.AreEqual(0.0, instance.bounding_box.min_y);
            Assert.AreEqual(0.0, instance.bounding_box.max_x);
            Assert.AreEqual(0.0, instance.bounding_box.max_y);
        }

        [Test]
        public void Constructor_WithNonDictionaryJson_ShouldThrowTypeError()
        {
            // Arrange
            string invalidJson = "[1, 2, 3]";

            // Act & Assert
            var ex = Assert.Throws<AttributeErrorException>(() => PythonEngineManager.DataGeometryBoundingBox2Class(invalidJson));
            Assert.That(ex.Message, Does.Contain("Node bounding box 2 failed to initialise with: 'list' object has no attribute 'get'"));
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
            Assert.AreEqual(5.5, instance.bounding_box.min_x);
            Assert.AreEqual(6.6, instance.bounding_box.min_y);
            Assert.AreEqual(7.7, instance.bounding_box.max_x);
            Assert.AreEqual(8.8, instance.bounding_box.max_y);
        }

        [Test]
        public void SetBoundingBoxByPoints_WithInvalidMin_ShouldThrowValueError()
        {
            // Arrange
            dynamic instance = PythonEngineManager.DataGeometryBoundingBox2Class();
            dynamic maxPoint = PythonEngineManager.Point2Class(7.7, 8.8);

            // Act & Assert
            var ex = Assert.Throws<ValueErrorException>(() => instance.update("invalid", maxPoint));
            Assert.That(ex.Message, Does.Contain("Min needs to be a point2 instance"));
        }

        [Test]
        public void SetBoundingBoxByPoints_WithInvalidMax_ShouldThrowValueError()
        {
            // Arrange
            dynamic instance = PythonEngineManager.DataGeometryBoundingBox2Class();
            dynamic minPoint = PythonEngineManager.Point2Class(5.5, 6.6);

            // Act & Assert
            var ex = Assert.Throws<ValueErrorException>(() => instance.update(minPoint, "invalid"));
            Assert.That(ex.Message, Does.Contain("Max needs to be a point2 instance"));
        }

        [Test]
        public void EqualInstances_ShouldReturnTrue()
        {
            // JSON representation with identical bounding box min and max coordinates
            var jsonString = JsonConvert.SerializeObject(new
            {
                bounding_box = new
                {
                    min_x = 5.5,
                    max_x = 7.7,
                    min_y = 6.6,
                    max_y = 8.8
                }
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
            // JSON representation for the first instance
            var jsonStringA = JsonConvert.SerializeObject(new
            {
                bounding_box = new
                {
                    min_x = 5.5,
                    max_x = 7.7,
                    min_y = 6.6,
                    max_y = 8.8
                }
            });

            // JSON representation for the second instance with different bounding box coordinates
            var jsonStringB = JsonConvert.SerializeObject(new
            {
                bounding_box = new
                {
                    min_x = 4.0,
                    max_x = 6.5,
                    min_y = 3.3,
                    max_y = 9.0
                }
            });

            Console.WriteLine($"jsonStringA: {jsonStringA}");
            Console.WriteLine($"jsonStringB: {jsonStringB}");

            // Initialize two instances with different JSON data
            var dataGeometryA = PythonEngineManager.DataGeometryBoundingBox2Class(jsonStringA);
            var dataGeometryB = PythonEngineManager.DataGeometryBoundingBox2Class(jsonStringB);

            // Assert that the two instances are not equal
            Assert.IsTrue(dataGeometryA != dataGeometryB, "Expected instances with different data to return true for inequality.");
        }

        [Test]
        public void EqualOperator_WithIdenticalBoundingBox_ShouldReturnTrue()
        {
            // JSON representation with identical bounding box min and max coordinates
            var jsonString = JsonConvert.SerializeObject(new
            {
                bounding_box = new
                {
                    min_x = 1.0,
                    max_x = 5.0,
                    min_y = 2.0,
                    max_y = 6.0
                }
            });

            // Initialize two instances with the same JSON data
            var dataGeometryA = PythonEngineManager.DataGeometryBoundingBox2Class(jsonString);
            var dataGeometryB = PythonEngineManager.DataGeometryBoundingBox2Class(jsonString);

            // Assert that the '==' operator returns true for equal instances
            Assert.IsTrue(dataGeometryA == dataGeometryB, "Expected '==' to return true for identical bounding boxes.");
        }

        [Test]
        public void NotEqualOperator_WithDifferentBoundingBox_ShouldReturnTrue()
        {
            // JSON representation for the first instance
            var jsonStringA = JsonConvert.SerializeObject(new
            {
                bounding_box = new
                {
                    min_x = 1.0,
                    max_x = 5.0,
                    min_y = 2.0,
                    max_y = 6.0
                }
            });

            // JSON representation for the second instance with different bounding box coordinates
            var jsonStringB = JsonConvert.SerializeObject(new
            {
                bounding_box = new
                {
                    min_x = 3.0,
                    max_x = 4.0,
                    min_y = 1.5,
                    max_y = 5.5
                }
            });

            // Initialize two instances with different JSON data
            var dataGeometryA = PythonEngineManager.DataGeometryBoundingBox2Class(jsonStringA);
            var dataGeometryB = PythonEngineManager.DataGeometryBoundingBox2Class(jsonStringB);

            // Assert that the '!=' operator returns true for non-equal instances
            Assert.IsTrue(dataGeometryA != dataGeometryB, "Expected '!=' to return true for different bounding boxes.");
        }
    }
}
