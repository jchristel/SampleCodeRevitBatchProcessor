using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Scripting.Hosting;
using IronPython.Runtime.Exceptions;

namespace PythonTests
{
    public class BoundingBox3Tests
    {
        ScriptEngine _engine;
        ScriptScope _scope;

        private dynamic boundingBox3Class;
        private dynamic point3Class;

        [SetUp]
        public void Setup()
        {
            // get a python engine
            ScriptEngine engine = PythonRunner.SetupEngine();
            _scope = engine.CreateScope();

            // get the repository path
            string repoPath = PythonRunner.GetRepositoryPath();

            // set path to bounding box 2 class
            var pythonFilePath_bbox3 = Path.Combine(repoPath, @"duHast\Geometry\bounding_box_3.py");
            // set path to point2 class
            var pythonFilePath_point3 = Path.Combine(repoPath, @"duHast\Geometry\point_3.py");

            //run the file
            engine.ExecuteFile(pythonFilePath_bbox3, _scope);
            //run the file
            engine.ExecuteFile(pythonFilePath_point3, _scope);

            boundingBox3Class = _scope.GetVariable("BoundingBox3");
            point3Class = _scope.GetVariable("Point3");

            //store the engine instance
            _engine = engine;
        }

        [Test]
        public void bbox3_ToJson()
        {
            // Initialize two points
            dynamic point1 = point3Class(1.0, 2.0, 3.0);
            dynamic point2 = point3Class(3.0, 4.0, 5.0);

            // Initialize bounding box with points
            dynamic bbox = boundingBox3Class(point1, point2);

            var result = bbox.to_json();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"json_ini\": null, \"max_x\": 3.0, \"max_y\": 4.0, \"max_z\": 5.0, \"min_x\": 1.0, \"min_y\": 2.0, \"min_z\": 3.0}";

            Assert.AreEqual(jsonString, result);
        }

        [Test]
        public void bbox3_ToJsonUtf()
        {
            // Initialize two points
            dynamic point1 = point3Class(1.0, 2.0, 3.0);
            dynamic point2 = point3Class(3.0, 4.0, 5.0);

            // Initialize bounding box with points
            dynamic bbox = boundingBox3Class(point1, point2);

            var result = bbox.to_json_utf();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"json_ini\": null, \"max_x\": 3.0, \"max_y\": 4.0, \"max_z\": 5.0, \"min_x\": 1.0, \"min_y\": 2.0, \"min_z\": 3.0}";

            Assert.AreEqual(jsonString, result);
        }

        [Test]
        public void bbox3_Initialize_WithPoints_ShouldSetCorrectBoundaries()
        {
            // Initialize two points
            dynamic point1 = point3Class(1.0, 2.0,3.0);
            dynamic point2 = point3Class(3.0, 4.0,5.0);

            // Initialize bounding box with points
            dynamic bbox = boundingBox3Class(point1, point2);

            Assert.AreEqual(1.0, bbox.min_x);
            Assert.AreEqual(2.0, bbox.min_y);
            Assert.AreEqual(3.0, bbox.min_z);
            Assert.AreEqual(3.0, bbox.max_x);
            Assert.AreEqual(4.0, bbox.max_y);
            Assert.AreEqual(5.0, bbox.max_z);
        }

        [Test]
        public void bbox3_Initialize_WithJson_ShouldSetCorrectBoundaries()
        {
            // JSON input string with point1 and point2 data
            string json = "{\"point1\": {\"x\": 0.0, \"y\": 1.0, \"z\": 2.0}, \"point2\": {\"x\": 5.0, \"y\": 6.0, \"z\": 7.0}}";

            // Initialize bounding box with JSON
            dynamic bbox = boundingBox3Class(j: json);

            Assert.AreEqual(0.0, bbox.min_x);
            Assert.AreEqual(1.0, bbox.min_y);
            Assert.AreEqual(2.0, bbox.min_z);
            Assert.AreEqual(5.0, bbox.max_x);
            Assert.AreEqual(6.0, bbox.max_y);
            Assert.AreEqual(7.0, bbox.max_z);
        }

        [Test]
        public void bbox3_Update_WithNewPoints_ShouldUpdateBoundaries()
        {
            dynamic point1 = point3Class(1.0, 1.0, 1.0);
            dynamic point2 = point3Class(2.0, 2.0, 2.0);
            dynamic bbox = boundingBox3Class(point1, point2);

            dynamic newPoint1 = point3Class(0.0, 0.0, 0.0);
            dynamic newPoint2 = point3Class(3.0, 3.0, 3.0);
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
