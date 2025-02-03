using PythonTests.Setup;

namespace PythonTests.GeometryTests
{
    public class BoundingBox3Tests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.BoundingBox3Class, Is.Not.Null, "BoundingBox3 should be loaded.");
            Assert.That(PythonEngineManager.Point3Class, Is.Not.Null, "Point3Class should be loaded.");
        }


        [Test]
        public void Bbox3_ToJson()
        {
            // Initialize two points
            dynamic point1 = PythonEngineManager.Point3Class(1.0, 2.0, 3.0);
            dynamic point2 = PythonEngineManager.Point3Class(3.0, 4.0, 5.0);

            // Initialize bounding box with points
            dynamic bbox = PythonEngineManager.BoundingBox3Class(point1, point2);

            var result = bbox.to_json_ordered();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"json_ini\": null, \"max_x\": 3.0, \"max_y\": 4.0, \"max_z\": 5.0, \"min_x\": 1.0, \"min_y\": 2.0, \"min_z\": 3.0}";

            Assert.That(jsonString, Is.EqualTo(result));
        }

        [Test]
        public void Bbox3_ToJsonUtf()
        {
            // Initialize two points
            dynamic point1 = PythonEngineManager.Point3Class(1.0, 2.0, 3.0);
            dynamic point2 = PythonEngineManager.Point3Class(3.0, 4.0, 5.0);

            // Initialize bounding box with points
            dynamic bbox = PythonEngineManager.BoundingBox3Class(point1, point2);

            var result = bbox.to_json_utf_ordered();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"json_ini\": null, \"max_x\": 3.0, \"max_y\": 4.0, \"max_z\": 5.0, \"min_x\": 1.0, \"min_y\": 2.0, \"min_z\": 3.0}";

            Assert.That(jsonString, Is.EqualTo(result));
        }

        [Test]
        public void Bbox3_Initialize_WithPoints_ShouldSetCorrectBoundaries()
        {
            // Initialize two points
            dynamic point1 = PythonEngineManager.Point3Class(1.0, 2.0,3.0);
            dynamic point2 = PythonEngineManager.Point3Class(3.0, 4.0,5.0);

            // Initialize bounding box with points
            dynamic bbox = PythonEngineManager.BoundingBox3Class(point1, point2);

            Assert.That(1.0, Is.EqualTo(bbox.min_x));
            Assert.That(2.0, Is.EqualTo(bbox.min_y));
            Assert.That(3.0, Is.EqualTo(bbox.min_z));
            Assert.That(3.0, Is.EqualTo(bbox.max_x));
            Assert.That(4.0, Is.EqualTo(bbox.max_y));
            Assert.That(5.0, Is.EqualTo(bbox.max_z));
        }

        [Test]
        public void Bbox3_Initialize_WithJson_ShouldSetCorrectBoundaries()
        {
            // JSON input string with point1 and point2 data
            string json = @"{ ""min_x"": 1.1, ""min_y"": 2.2, ""min_z"": 3.3, ""max_x"": 4.4, ""max_y"": 5.5, ""max_z"": 6.6 }";

            // Initialize bounding box with JSON
            dynamic bbox = PythonEngineManager.BoundingBox3Class(j: json);

            Assert.That(1.1, Is.EqualTo(bbox.min_x));
            Assert.That(2.2, Is.EqualTo(bbox.min_y));
            Assert.That(3.3, Is.EqualTo(bbox.min_z));
            Assert.That(4.4, Is.EqualTo(bbox.max_x));
            Assert.That(5.5, Is.EqualTo(bbox.max_y));
            Assert.That(6.6, Is.EqualTo(bbox.max_z));
        }

        [Test]
        public void Bbox3_Update_WithNewPoints_ShouldUpdateBoundaries()
        {
            dynamic point1 = PythonEngineManager.Point3Class(1.0, 1.0, 1.0);
            dynamic point2 = PythonEngineManager.Point3Class(2.0, 2.0, 2.0);
            dynamic bbox = PythonEngineManager.BoundingBox3Class(point1, point2);

            dynamic newPoint1 = PythonEngineManager.Point3Class(0.0, 0.0, 0.0);
            dynamic newPoint2 = PythonEngineManager.Point3Class(3.0, 3.0, 3.0);
            bbox.update(newPoint1, newPoint2);

            Assert.That(0.0, Is.EqualTo(bbox.min_x));
            Assert.That(0.0, Is.EqualTo(bbox.min_y));
            Assert.That(0.0, Is.EqualTo(bbox.min_z));
            Assert.That(3.0, Is.EqualTo(bbox.max_x));
            Assert.That(3.0, Is.EqualTo(bbox.max_y));
            Assert.That(3.0, Is.EqualTo(bbox.max_z));
        }


        [Test]
        public void EqualBoundingBoxesShouldReturnTrue()
        {
            dynamic point1 = PythonEngineManager.Point3Class(1.0, 1.0, 1.0);
            dynamic point2 = PythonEngineManager.Point3Class(2.0, 2.0, 2.0);
            // Initialize two bounding boxes with the same values
            dynamic _boundingBox1 = PythonEngineManager.BoundingBox3Class(point1, point2);
            dynamic _boundingBox2 = PythonEngineManager.BoundingBox3Class(point1, point2);


            Assert.That(_boundingBox1 == _boundingBox2, Is.True, "Expected equal bounding boxes to return true.");
        }

        [Test]
        public void DifferentBoundingBoxesShouldReturnFalse()
        {
            dynamic point1 = PythonEngineManager.Point3Class(1.0, 1.0, 1.0);
            dynamic point2 = PythonEngineManager.Point3Class(2.0, 2.0, 2.0);
            dynamic point3 = PythonEngineManager.Point3Class(0.0, 0.0, 0.0);
            dynamic point4 = PythonEngineManager.Point3Class(3.0, 3.0, 3.0);
            // Initialize two bounding boxes with the same values
            dynamic _boundingBox1 = PythonEngineManager.BoundingBox3Class(point1, point2);
            dynamic _boundingBox3 = PythonEngineManager.BoundingBox3Class(point3, point4);


            Assert.That(_boundingBox1 != _boundingBox3, Is.True, "Expected different bounding boxes to return true.");
        }

        [Test]
        public void DifferentTypesShouldReturnNotImplemented()
        {
            dynamic point1 = PythonEngineManager.Point3Class(1.0, 1.0, 1.0);
            dynamic point2 = PythonEngineManager.Point3Class(2.0, 2.0, 2.0);
            // Here we test against a different type to check for NotImplemented
            var differentType = new object();
            // Initialize bounding box
            dynamic _boundingBox1 = PythonEngineManager.BoundingBox3Class(point1, point2);

            Assert.That(_boundingBox1 == differentType, Is.False, "Expected different bounding boxes to return false.");
        }

        [Test]
        public void Bbox3_Width_ShouldReturnCorrectValue()
        {
            dynamic point1 = PythonEngineManager.Point3Class(1.0, 2.0, 3.0);
            dynamic point2 = PythonEngineManager.Point3Class(5.0, 4.0, 6.0);
            dynamic bbox = PythonEngineManager.BoundingBox3Class(point1, point2);

            var expectedWidth = 4.0; // max_x - min_x
            Assert.That(expectedWidth, Is.EqualTo( bbox.width()), "BoundingBox3 width calculation is incorrect.");
        }

        [Test]
        public void Bbox3_Depth_ShouldReturnCorrectValue()
        {
            dynamic point1 = PythonEngineManager.Point3Class(1.0, 2.0, 3.0);
            dynamic point2 = PythonEngineManager.Point3Class(5.0, 6.0, 6.0);
            dynamic bbox = PythonEngineManager.BoundingBox3Class(point1, point2);

            var expectedDepth = 4.0; // max_y - min_y
            Assert.That(expectedDepth, Is.EqualTo(bbox.depth()), "BoundingBox3 depth calculation is incorrect.");
        }

        [Test]
        public void Bbox3_Height_ShouldReturnCorrectValue()
        {
            dynamic point1 = PythonEngineManager.Point3Class(1.0, 2.0, 3.0);
            dynamic point2 = PythonEngineManager.Point3Class(5.0, 4.0, 7.0);
            dynamic bbox = PythonEngineManager.BoundingBox3Class(point1, point2);

            var expectedHeight = 4.0; // max_z - min_z
            Assert.That(expectedHeight, Is.EqualTo(bbox.height()), "BoundingBox3 height calculation is incorrect.");
        }

        [Test]
        public void Bbox3_ZeroDimension_ShouldReturnZeroForWidthDepthHeight()
        {
            dynamic point1 = PythonEngineManager.Point3Class(1.0, 2.0, 3.0);
            dynamic point2 = PythonEngineManager.Point3Class(1.0, 2.0, 3.0); // Same point as point1
            dynamic bbox = PythonEngineManager.BoundingBox3Class(point1, point2);

            Assert.That(0.0, Is.EqualTo(bbox.width()), "Width should be zero for a zero-dimension bounding box.");
            Assert.That(0.0, Is.EqualTo(bbox.depth()), "Depth should be zero for a zero-dimension bounding box.");
            Assert.That(0.0, Is.EqualTo(bbox.height()), "Height should be zero for a zero-dimension bounding box.");
        }
    }
}
