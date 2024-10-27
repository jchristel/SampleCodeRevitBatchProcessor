using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Scripting.Hosting;
using IronPython.Runtime.Exceptions;

namespace PythonTests
{
    public class BoundingBox2Tests
    {
        ScriptEngine _engine;
        ScriptScope _scope;

        private dynamic boundingBox2Class;
        private dynamic point2Class;

        [SetUp]
        public void Setup()
        {
            // get a python engine
            ScriptEngine engine = PythonRunner.SetupEngine();
            _scope = engine.CreateScope();

            // get the repository path
            string repoPath = PythonRunner.GetRepositoryPath();

            // set path to bounding box 2 class
            var pythonFilePath_bbox2 = Path.Combine(repoPath, @"duHast\Geometry\bounding_box_2.py");
            // set path to point2 class
            var pythonFilePath_point2 = Path.Combine(repoPath, @"duHast\Geometry\point_2.py");

            //run the file
            engine.ExecuteFile(pythonFilePath_bbox2, _scope);
            //run the file
            engine.ExecuteFile(pythonFilePath_point2, _scope);

            boundingBox2Class = _scope.GetVariable("BoundingBox2");
            point2Class = _scope.GetVariable("Point2");

            //store the engine instance
            _engine = engine;
        }

        [Test]
        public void bbox2_ToJson()
        {
            // Initialize two points
            dynamic point1 = point2Class(1.0, 2.0);
            dynamic point2 = point2Class(3.0, 4.0);

            // Initialize bounding box with points
            dynamic bbox = boundingBox2Class(point1, point2);

            var result = bbox.to_json();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"json_ini\": null, \"max_x\": 3.0, \"max_y\": 4.0, \"min_x\": 1.0, \"min_y\": 2.0}";

            Assert.AreEqual(jsonString, result);
        }

        [Test]
        public void bbox2_ToJsonUtf()
        {
            // Initialize two points
            dynamic point1 = point2Class(1.0, 2.0);
            dynamic point2 = point2Class(3.0, 4.0);

            // Initialize bounding box with points
            dynamic bbox = boundingBox2Class(point1, point2);

            var result = bbox.to_json_utf();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"json_ini\": null, \"max_x\": 3.0, \"max_y\": 4.0, \"min_x\": 1.0, \"min_y\": 2.0}";

            Assert.AreEqual(jsonString, result);
        }

        [Test]
        public void bbox2_Initialize_WithPoints_ShouldSetCorrectBoundaries()
        {
            // Initialize two points
            dynamic point1 = point2Class(1.0, 2.0);
            dynamic point2 = point2Class(3.0, 4.0);

            // Initialize bounding box with points
            dynamic bbox = boundingBox2Class(point1, point2);

            Assert.AreEqual(1.0, bbox.min_x);
            Assert.AreEqual(2.0, bbox.min_y);
            Assert.AreEqual(3.0, bbox.max_x);
            Assert.AreEqual(4.0, bbox.max_y);
        }

        [Test]
        public void bbox2_Initialize_WithJson_ShouldSetCorrectBoundaries()
        {
            // JSON input string with point1 and point2 data
            string json = "{\"point1\": {\"x\": 0.0, \"y\": 1.0}, \"point2\": {\"x\": 5.0, \"y\": 6.0}}";

            // Initialize bounding box with JSON
            dynamic bbox = boundingBox2Class(j: json);

            Assert.AreEqual(0.0, bbox.min_x);
            Assert.AreEqual(1.0, bbox.min_y);
            Assert.AreEqual(5.0, bbox.max_x);
            Assert.AreEqual(6.0, bbox.max_y);
        }

        [Test]
        public void bbox2_Update_WithNewPoints_ShouldUpdateBoundaries()
        {
            dynamic point1 = point2Class(1.0, 1.0);
            dynamic point2 = point2Class(2.0, 2.0);
            dynamic bbox = boundingBox2Class(point1, point2);

            dynamic newPoint1 = point2Class(0.0, 0.0);
            dynamic newPoint2 = point2Class(3.0, 3.0);
            bbox.update(newPoint1, newPoint2);

            Assert.AreEqual(0.0, bbox.min_x);
            Assert.AreEqual(0.0, bbox.min_y);
            Assert.AreEqual(3.0, bbox.max_x);
            Assert.AreEqual(3.0, bbox.max_y);
        }

        [Test]
        public void bbox2_Contains_PointWithinBounds_ShouldReturnTrue()
        {
            dynamic point1 = point2Class(1.0, 1.0);
            dynamic point2 = point2Class(3.0, 3.0);
            dynamic bbox = boundingBox2Class(point1, point2);

            dynamic insidePoint = point2Class(2.0, 2.0);
            Assert.IsTrue(bbox.contains(insidePoint));
        }

        [Test]
        public void bbox2_Contains_PointOutsideBounds_ShouldReturnFalse()
        {
            dynamic point1 = point2Class(1.0, 1.0);
            dynamic point2 = point2Class(3.0, 3.0);
            dynamic bbox = boundingBox2Class(point1, point2);

            dynamic outsidePoint = point2Class(4.0, 4.0);
            Assert.IsFalse(bbox.contains(outsidePoint));
        }

        [Test]
        public void bbox2_Initialize_WithInvalidPoint_ShouldThrowTypeError()
        {
            dynamic invalidPoint = new { x = 1.0, y = 2.0 }; // Not a Point2 instance

            var ex = Assert.Throws<TypeErrorException>(() => boundingBox2Class(invalidPoint, invalidPoint));
            Assert.IsTrue(ex.Message.Contains("Point2 instance"));
        }

        [Test]
        public void bbox2_Initialize_WithMissingPoints_ShouldThrowValueError()
        {
            var ex = Assert.Throws<ValueErrorException>(() => boundingBox2Class(null, null));
            Assert.IsTrue(ex.Message.Contains("Either two Point2 instances or a JSON string with point data"));
        }

        [Test]
        public void bbox2_Update_WithInvalidType_ShouldThrowTypeError()
        {
            dynamic point1 = point2Class(1.0, 1.0);
            dynamic point2 = point2Class(2.0, 2.0);
            dynamic bbox = boundingBox2Class(point1, point2);

            var ex = Assert.Throws<TypeErrorException>(() => bbox.update(point1, new { x = 3.0, y = 3.0 }));
            Assert.IsTrue(ex.Message.Contains("Point2 instance"));
        }

        [Test]
        public void bbox2_StringRepresentation_ReturnsCorrectFormat()
        {
            dynamic point1 = point2Class(1.0, 1.0);
            dynamic point2 = point2Class(2.0, 2.0);
            dynamic bbox = boundingBox2Class(point1, point2);

            // Call the __str__ method directly
            var str = bbox.__str__();

            Assert.AreEqual("BoundingBox2D(1.0, 1.0, 2.0, 2.0)", str);
        }
    }
}
