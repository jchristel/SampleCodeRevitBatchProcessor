using IronPython.Runtime.Exceptions;
using PythonTests.Setup;

namespace PythonTests.GeometryTests
{
    public class BoundingBox2Tests
    {

        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.BoundingBox2Class, Is.Not.Null, "BoundingBox2 should be loaded.");
            Assert.That(PythonEngineManager.Point2Class, Is.Not.Null, "Point2Class should be loaded.");
        }

        [Test]
        public void Bbox2_Width_ShouldReturnCorrectValue()
        {
            // Arrange
            dynamic point1 = PythonEngineManager.Point2Class(1.0, 2.0);
            dynamic point2 = PythonEngineManager.Point2Class(4.0, 6.0);
            dynamic bbox = PythonEngineManager.BoundingBox2Class(point1, point2);

            // Act
            double width = bbox.width();

            // Assert
            Assert.That(width, Is.EqualTo(3.0), "Expected width to be 3.0.");
        }

        [Test]
        public void Bbox2_Depth_ShouldReturnCorrectValue()
        {
            // Arrange
            dynamic point1 = PythonEngineManager.Point2Class(1.0, 2.0);
            dynamic point2 = PythonEngineManager.Point2Class(4.0, 6.0);
            dynamic bbox = PythonEngineManager.BoundingBox2Class(point1, point2);

            // Act
            double depth = bbox.depth();

            // Assert
            Assert.That(depth, Is.EqualTo(4.0), "Expected depth to be 4.0.");
        }

        [Test]
        public void Bbox2_Ratio_ShouldReturnCorrectValue()
        {
            // Arrange
            dynamic point1 = PythonEngineManager.Point2Class(1.0, 2.0);
            dynamic point2 = PythonEngineManager.Point2Class(5.0, 4.0);
            dynamic bbox = PythonEngineManager.BoundingBox2Class(point1, point2);

            // Act
            double ratio = bbox.ratio();

            // Assert
            Assert.That(ratio, Is.EqualTo(2.0), "Expected ratio to be 2.0.");
        }

        [Test]
        public void Bbox2_Ratio_WithZeroDepth_ShouldThrowValueError()
        {
            // Arrange
            dynamic point1 = PythonEngineManager.Point2Class(1.0, 2.0);
            dynamic point2 = PythonEngineManager.Point2Class(5.0, 2.0); // Zero depth
            dynamic bbox = PythonEngineManager.BoundingBox2Class(point1, point2);

            // Act & Assert
            var ex = Assert.Throws<ValueErrorException>(() => bbox.ratio());
            Assert.That(ex.Message, Does.Contain("division by 0.0 is not allowed"));
        }

        [Test]
        public void Bbox2_ToJson()
        {
            // Initialize two points
            dynamic point1 = PythonEngineManager.Point2Class(1.0, 2.0);
            dynamic point2 = PythonEngineManager.Point2Class(3.0, 4.0);

            // Initialize bounding box with points
            dynamic bbox = PythonEngineManager.BoundingBox2Class(point1, point2);

            var result = bbox.to_json_ordered();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"json_ini\": null, \"max_x\": 3.0, \"max_y\": 4.0, \"min_x\": 1.0, \"min_y\": 2.0}";

            Assert.That(jsonString, Is.EqualTo(result));
        }

        [Test]
        public void Bbox2_ToJsonUtf()
        {
            // Initialize two points
            dynamic point1 = PythonEngineManager.Point2Class(1.0, 2.0);
            dynamic point2 = PythonEngineManager.Point2Class(3.0, 4.0);

            // Initialize bounding box with points
            dynamic bbox = PythonEngineManager.BoundingBox2Class(point1, point2);

            var result = bbox.to_json_utf_ordered();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"json_ini\": null, \"max_x\": 3.0, \"max_y\": 4.0, \"min_x\": 1.0, \"min_y\": 2.0}";

            Assert.That(jsonString, Is.EqualTo(result));
        }

        [Test]
        public void Bbox2_Initialize_WithPoints_ShouldSetCorrectBoundaries()
        {
            // Initialize two points
            dynamic point1 = PythonEngineManager.Point2Class(1.0, 2.0);
            dynamic point2 = PythonEngineManager.Point2Class(3.0, 4.0);

            // Initialize bounding box with points
            dynamic bbox = PythonEngineManager.BoundingBox2Class(point1, point2);

            Assert.That(1.0, Is.EqualTo(bbox.min_x));
            Assert.That(2.0, Is.EqualTo(bbox.min_y));
            Assert.That(3.0, Is.EqualTo(bbox.max_x));
            Assert.That(4.0, Is.EqualTo(bbox.max_y));
        }

        [Test]
        public void Bbox2_Initialize_WithJson_ShouldSetCorrectBoundaries()
        {
            // JSON input string with point1 and point2 data
            string json = @"{ ""min_x"": 1.1, ""min_y"": 2.2, ""max_x"": 3.3, ""max_y"": 4.4 }";

            // Initialize bounding box with JSON
            dynamic bbox = PythonEngineManager.BoundingBox2Class(j: json);

            Assert.That(1.1, Is.EqualTo(bbox.min_x));
            Assert.That(2.2, Is.EqualTo(bbox.min_y));
            Assert.That(3.3, Is.EqualTo(bbox.max_x));
            Assert.That(4.4, Is.EqualTo(bbox.max_y));
        }

        [Test]
        public void Bbox2_Update_WithNewPoints_ShouldUpdateBoundaries()
        {
            dynamic point1 = PythonEngineManager.Point2Class(1.0, 1.0);
            dynamic point2 = PythonEngineManager.Point2Class(2.0, 2.0);
            dynamic bbox = PythonEngineManager.BoundingBox2Class(point1, point2);

            dynamic newPoint1 = PythonEngineManager.Point2Class(0.0, 0.0);
            dynamic newPoint2 = PythonEngineManager.Point2Class(3.0, 3.0);
            bbox.update(newPoint1, newPoint2);

            Assert.That(0.0, Is.EqualTo(bbox.min_x));
            Assert.That(0.0, Is.EqualTo(bbox.min_y));
            Assert.That(3.0, Is.EqualTo(bbox.max_x));
            Assert.That(3.0, Is.EqualTo(bbox.max_y));
        }

        [Test]
        public void Bbox2_Contains_PointWithinBounds_ShouldReturnTrue()
        {
            dynamic point1 = PythonEngineManager.Point2Class(1.0, 1.0);
            dynamic point2 = PythonEngineManager.Point2Class(3.0, 3.0);
            dynamic bbox = PythonEngineManager.BoundingBox2Class(point1, point2);

            dynamic insidePoint = PythonEngineManager.Point2Class(2.0, 2.0);
            Assert.That(bbox.contains(insidePoint), Is.True);
        }

        [Test]
        public void Bbox2_Contains_PointOutsideBounds_ShouldReturnFalse()
        {
            dynamic point1 = PythonEngineManager.Point2Class(1.0, 1.0);
            dynamic point2 = PythonEngineManager.Point2Class(3.0, 3.0);
            dynamic bbox = PythonEngineManager.BoundingBox2Class(point1, point2);

            dynamic outsidePoint = PythonEngineManager.Point2Class(4.0, 4.0);
            Assert.That(bbox.contains(outsidePoint), Is.False);
        }

        [Test]
        public void Bbox2_Initialize_WithInvalidPoint_ShouldThrowTypeError()
        {
            dynamic invalidPoint = new { x = 1.0, y = 2.0 }; // Not a Point2 instance

            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.BoundingBox2Class(invalidPoint, invalidPoint));
            Assert.That(ex.Message, Does.Contain("Point2 instance"));
        }

        [Test]
        public void Bbox2_Initialize_WithMissingPoints_ShouldInitialiseDefault()
        {
            dynamic bbox = PythonEngineManager.BoundingBox2Class(null, null);
            Assert.That(0.0, Is.EqualTo(bbox.min_x));
            Assert.That(0.0, Is.EqualTo(bbox.min_y));
            Assert.That(0.0, Is.EqualTo(bbox.max_x));
            Assert.That(0.0, Is.EqualTo(bbox.max_y));

        }

        [Test]
        public void Bbox2_Update_WithInvalidType_ShouldThrowTypeError()
        {
            dynamic point1 = PythonEngineManager.Point2Class(1.0, 1.0);
            dynamic point2 = PythonEngineManager.Point2Class(2.0, 2.0);
            dynamic bbox = PythonEngineManager.BoundingBox2Class(point1, point2);

            var ex = Assert.Throws<TypeErrorException>(() => bbox.update(point1, new { x = 3.0, y = 3.0 }));
            Assert.That(ex.Message, Does.Contain("Point2 instance"));
        }

        [Test]
        public void Bbox2_StringRepresentation_ReturnsCorrectFormat()
        {
            dynamic point1 = PythonEngineManager.Point2Class(1.0, 1.0);
            dynamic point2 = PythonEngineManager.Point2Class(2.0, 2.0);
            dynamic bbox = PythonEngineManager.BoundingBox2Class(point1, point2);

            // Call the __str__ method directly
            var str = bbox.__str__();

            Assert.That("BoundingBox2D(1.0, 1.0, 2.0, 2.0)", Is.EqualTo(str));
        }

        [Test]
        public void EqualBoundingBoxesShouldReturnTrue()
        {
            dynamic point1 = PythonEngineManager.Point2Class(1.0, 1.0);
            dynamic point2 = PythonEngineManager.Point2Class(2.0, 2.0);
            // Initialize two bounding boxes with the same values
            dynamic _boundingBox1 = PythonEngineManager.BoundingBox2Class(point1, point2);
            dynamic _boundingBox2 = PythonEngineManager.BoundingBox2Class(point1, point2);
            

            Assert.That(_boundingBox1 == _boundingBox2, Is.True, "Expected equal bounding boxes to return true.");
        }

        [Test]
        public void DifferentBoundingBoxesShouldReturnFalse()
        {
            dynamic point1 = PythonEngineManager.Point2Class(1.0, 1.0);
            dynamic point2 = PythonEngineManager.Point2Class(2.0, 2.0);
            dynamic point3 = PythonEngineManager.Point2Class(0.0, 0.0);
            dynamic point4 = PythonEngineManager.Point2Class(3.0, 3.0);
            // Initialize two bounding boxes with the same values
            dynamic _boundingBox1 = PythonEngineManager.BoundingBox2Class(point1, point2);
            dynamic _boundingBox3 = PythonEngineManager.BoundingBox2Class(point3, point4);
           

            Assert.That(_boundingBox1 != _boundingBox3, Is.True, "Expected different bounding boxes to return true.");
        }

        [Test]
        public void DifferentTypesShouldReturnNotImplemented()
        {
            dynamic point1 = PythonEngineManager.Point2Class(1.0, 1.0);
            dynamic point2 = PythonEngineManager.Point2Class(2.0, 2.0);
            // Here we test against a different type to check for NotImplemented
            var differentType = new object();
            // Initialize bounding box
            dynamic _boundingBox1 = PythonEngineManager.BoundingBox2Class(point1, point2);

            Assert.That(_boundingBox1 == differentType, Is.False, "Expected different bounding boxes to return false.");
        }
    }
}
