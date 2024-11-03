using PythonTests.Setup;

namespace PythonTests
{
    public class BoundingBox3Tests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.IsNotNull(PythonEngineManager.BoundingBox3Class, "BoundingBox3 should be loaded.");
            Assert.IsNotNull(PythonEngineManager.Point3Class, "Point3Class should be loaded.");
        }


        [Test]
        public void Bbox3_ToJson()
        {
            // Initialize two points
            dynamic point1 = PythonEngineManager.Point3Class(1.0, 2.0, 3.0);
            dynamic point2 = PythonEngineManager.Point3Class(3.0, 4.0, 5.0);

            // Initialize bounding box with points
            dynamic bbox = PythonEngineManager.BoundingBox3Class(point1, point2);

            var result = bbox.to_json();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"json_ini\": null, \"max_x\": 3.0, \"max_y\": 4.0, \"max_z\": 5.0, \"min_x\": 1.0, \"min_y\": 2.0, \"min_z\": 3.0}";

            Assert.AreEqual(jsonString, result);
        }

        [Test]
        public void Bbox3_ToJsonUtf()
        {
            // Initialize two points
            dynamic point1 = PythonEngineManager.Point3Class(1.0, 2.0, 3.0);
            dynamic point2 = PythonEngineManager.Point3Class(3.0, 4.0, 5.0);

            // Initialize bounding box with points
            dynamic bbox = PythonEngineManager.BoundingBox3Class(point1, point2);

            var result = bbox.to_json_utf();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"json_ini\": null, \"max_x\": 3.0, \"max_y\": 4.0, \"max_z\": 5.0, \"min_x\": 1.0, \"min_y\": 2.0, \"min_z\": 3.0}";

            Assert.AreEqual(jsonString, result);
        }

        [Test]
        public void Bbox3_Initialize_WithPoints_ShouldSetCorrectBoundaries()
        {
            // Initialize two points
            dynamic point1 = PythonEngineManager.Point3Class(1.0, 2.0,3.0);
            dynamic point2 = PythonEngineManager.Point3Class(3.0, 4.0,5.0);

            // Initialize bounding box with points
            dynamic bbox = PythonEngineManager.BoundingBox3Class(point1, point2);

            Assert.AreEqual(1.0, bbox.min_x);
            Assert.AreEqual(2.0, bbox.min_y);
            Assert.AreEqual(3.0, bbox.min_z);
            Assert.AreEqual(3.0, bbox.max_x);
            Assert.AreEqual(4.0, bbox.max_y);
            Assert.AreEqual(5.0, bbox.max_z);
        }

        [Test]
        public void Bbox3_Initialize_WithJson_ShouldSetCorrectBoundaries()
        {
            // JSON input string with point1 and point2 data
            string json = @"{ ""min_x"": 1.1, ""min_y"": 2.2, ""min_z"": 3.3, ""max_x"": 4.4, ""max_y"": 5.5, ""max_z"": 6.6 }";

            // Initialize bounding box with JSON
            dynamic bbox = PythonEngineManager.BoundingBox3Class(j: json);

            Assert.AreEqual(1.1, bbox.min_x);
            Assert.AreEqual(2.2, bbox.min_y);
            Assert.AreEqual(3.3, bbox.min_z);
            Assert.AreEqual(4.4, bbox.max_x);
            Assert.AreEqual(5.5, bbox.max_y);
            Assert.AreEqual(6.6, bbox.max_z);
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

            Assert.AreEqual(0.0, bbox.min_x);
            Assert.AreEqual(0.0, bbox.min_y);
            Assert.AreEqual(0.0, bbox.min_z);
            Assert.AreEqual(3.0, bbox.max_x);
            Assert.AreEqual(3.0, bbox.max_y);
            Assert.AreEqual(3.0, bbox.max_z);
        }

    }
}
