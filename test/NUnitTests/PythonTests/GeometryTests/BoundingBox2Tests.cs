using IronPython.Runtime.Exceptions;
using PythonTests.Setup;

namespace PythonTests
{
    public class BoundingBox2Tests
    {

        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.IsNotNull(PythonEngineManager.BoundingBox2Class, "BoundingBox2 should be loaded.");
            Assert.IsNotNull(PythonEngineManager.Point2Class, "Point2Class should be loaded.");
        }

        [Test]
        public void Bbox2_ToJson()
        {
            // Initialize two points
            dynamic point1 = PythonEngineManager.Point2Class(1.0, 2.0);
            dynamic point2 = PythonEngineManager.Point2Class(3.0, 4.0);

            // Initialize bounding box with points
            dynamic bbox = PythonEngineManager.BoundingBox2Class(point1, point2);

            var result = bbox.to_json();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"json_ini\": null, \"max_x\": 3.0, \"max_y\": 4.0, \"min_x\": 1.0, \"min_y\": 2.0}";

            Assert.AreEqual(jsonString, result);
        }

        [Test]
        public void Bbox2_ToJsonUtf()
        {
            // Initialize two points
            dynamic point1 = PythonEngineManager.Point2Class(1.0, 2.0);
            dynamic point2 = PythonEngineManager.Point2Class(3.0, 4.0);

            // Initialize bounding box with points
            dynamic bbox = PythonEngineManager.BoundingBox2Class(point1, point2);

            var result = bbox.to_json_utf();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"json_ini\": null, \"max_x\": 3.0, \"max_y\": 4.0, \"min_x\": 1.0, \"min_y\": 2.0}";

            Assert.AreEqual(jsonString, result);
        }

        [Test]
        public void Bbox2_Initialize_WithPoints_ShouldSetCorrectBoundaries()
        {
            // Initialize two points
            dynamic point1 = PythonEngineManager.Point2Class(1.0, 2.0);
            dynamic point2 = PythonEngineManager.Point2Class(3.0, 4.0);

            // Initialize bounding box with points
            dynamic bbox = PythonEngineManager.BoundingBox2Class(point1, point2);

            Assert.AreEqual(1.0, bbox.min_x);
            Assert.AreEqual(2.0, bbox.min_y);
            Assert.AreEqual(3.0, bbox.max_x);
            Assert.AreEqual(4.0, bbox.max_y);
        }

        [Test]
        public void Bbox2_Initialize_WithJson_ShouldSetCorrectBoundaries()
        {
            // JSON input string with point1 and point2 data
            string json = @"{ ""min_x"": 1.1, ""min_y"": 2.2, ""max_x"": 3.3, ""max_y"": 4.4 }";

            // Initialize bounding box with JSON
            dynamic bbox = PythonEngineManager.BoundingBox2Class(j: json);

            Assert.AreEqual(1.1, bbox.min_x);
            Assert.AreEqual(2.2, bbox.min_y);
            Assert.AreEqual(3.3, bbox.max_x);
            Assert.AreEqual(4.4, bbox.max_y);
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

            Assert.AreEqual(0.0, bbox.min_x);
            Assert.AreEqual(0.0, bbox.min_y);
            Assert.AreEqual(3.0, bbox.max_x);
            Assert.AreEqual(3.0, bbox.max_y);
        }

        [Test]
        public void Bbox2_Contains_PointWithinBounds_ShouldReturnTrue()
        {
            dynamic point1 = PythonEngineManager.Point2Class(1.0, 1.0);
            dynamic point2 = PythonEngineManager.Point2Class(3.0, 3.0);
            dynamic bbox = PythonEngineManager.BoundingBox2Class(point1, point2);

            dynamic insidePoint = PythonEngineManager.Point2Class(2.0, 2.0);
            Assert.IsTrue(bbox.contains(insidePoint));
        }

        [Test]
        public void Bbox2_Contains_PointOutsideBounds_ShouldReturnFalse()
        {
            dynamic point1 = PythonEngineManager.Point2Class(1.0, 1.0);
            dynamic point2 = PythonEngineManager.Point2Class(3.0, 3.0);
            dynamic bbox = PythonEngineManager.BoundingBox2Class(point1, point2);

            dynamic outsidePoint = PythonEngineManager.Point2Class(4.0, 4.0);
            Assert.IsFalse(bbox.contains(outsidePoint));
        }

        [Test]
        public void Bbox2_Initialize_WithInvalidPoint_ShouldThrowTypeError()
        {
            dynamic invalidPoint = new { x = 1.0, y = 2.0 }; // Not a Point2 instance

            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.BoundingBox2Class(invalidPoint, invalidPoint));
            Assert.That(ex.Message, Does.Contain("Point2 instance"));
        }

        [Test]
        public void Bbox2_Initialize_WithMissingPoints_ShouldThrowValueError()
        {
            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.BoundingBox2Class(null, null));
            Assert.That(ex.Message, Does.Contain("Either two Point2 instances or a JSON string with point data"));
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

            Assert.AreEqual("BoundingBox2D(1.0, 1.0, 2.0, 2.0)", str);
        }
    }
}
