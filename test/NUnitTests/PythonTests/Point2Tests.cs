using NUnit.Framework;
using IronPython.Hosting;
using Microsoft.Scripting.Hosting;
using IronPython.Runtime.Exceptions;

namespace PythonTests
{
    public class Point2Tests
    {
        ScriptEngine _engine;
        ScriptScope _scope;

        [SetUp]
        public void Setup()
        {
            // get a python engine
            ScriptEngine engine = PythonRunner.SetupEngine();
            _scope = engine.CreateScope();

            // get the repository path
            string repoPath = PythonRunner.GetRepositoryPath();

            // set path to point2 class
            var pythonFilePath = Path.Combine(repoPath, @"duHast\Geometry\point_2.py");

            //run the file
            engine.ExecuteFile(pythonFilePath, _scope);

            //store the engine instance
            _engine = engine;

        }

        [Test]
        public void ToJson()
        {
            // set up a point2 instance
            dynamic point2Instance = _scope.GetVariable("Point2")(0.0, 0.0);

            var result = point2Instance.to_json();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"x\": 0.0, \"y\": 0.0, \"json_ini\": null}";

            Assert.AreEqual(jsonString, result);
        }

        [Test]
        public void ToJsonUtf()
        {
            // set up a point2 instance
            dynamic point2Instance = _scope.GetVariable("Point2")(0.0, 0.0);

            var result = point2Instance.to_json_utf();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"x\": 0.0, \"y\": 0.0, \"json_ini\": null}";

            Assert.AreEqual(jsonString, result);
        }

        [Test]
        public void IniFromJson()
        {
            string json = "{\"x\": 5.0, \"y\": 10.0}";

            dynamic point2Instance = _scope.GetVariable("Point2")(j: json);

            Assert.AreEqual(5.0, point2Instance.x);
            Assert.AreEqual(10.0, point2Instance.y);
        }

        [Test]
        public void Point2_WithInvalidJson_ThrowsValueError()
        {
            // invalid json
            string json = "{\"x\": 5.0}";

            var ex = Assert.Throws<ValueErrorException>(() => _scope.GetVariable("Point2")(j: json));
            Assert.IsTrue(ex.Message.Contains("JSON must contain 'x' and 'y' keys."));
        }

        [Test]
        public void Point2_WithNullJsonAndCoordinates_ThrowsValueError()
        { 
            var ex = Assert.Throws<TypeErrorException>(() => _scope.GetVariable("Point2")());
            Assert.IsTrue(ex.Message.Contains("x expected float. Got <class 'NoneType'> instead."));
        }


        [Test]
        public void Point2_WithIntegerXCoordinates_ThrowsValueError()
        {
            var ex = Assert.Throws<TypeErrorException>(() => _scope.GetVariable("Point2")(x: -1, y: 0));
            // Output the result to the console
            //Console.WriteLine($"Result of int: {ex.Message}");
            Assert.IsTrue(ex.Message.Contains("x expected float. Got <class 'int'> instead."));
        }

        public void Point2_WithIntegerYCoordinates_ThrowsValueError()
        {
            var ex = Assert.Throws<TypeErrorException>(() => _scope.GetVariable("Point2")(x: -1.0, y: 0));
            // Output the result to the console
            Console.WriteLine($"Result of int: {ex.Message}");
            Assert.IsTrue(ex.Message.Contains("y expected float. Got <class 'int'> instead."));
        }

        [Test]
        public void Point2_WithNegativeCoordinates_ThrowsValueError()
        {
            var point = _scope.GetVariable("Point2")(x: -1.0, y: 0.0);
            Assert.AreEqual(-1.0, point.x);
            Assert.AreEqual(0.0, point.y);
        }

        [Test]
        public void Point2_WithValidCoordinates_InitializesProperties()
        {
            var point = _scope.GetVariable("Point2")(x: 3.0, y: 4.0);

            Assert.AreEqual(3.0, point.x);
            Assert.AreEqual(4.0, point.y);
        }
    }
}