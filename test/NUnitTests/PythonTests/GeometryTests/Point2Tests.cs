using NUnit.Framework;
using IronPython.Hosting;
using Microsoft.Scripting.Hosting;
using IronPython.Runtime.Exceptions;
using PythonTests.Setup;

namespace PythonTests
{
    public class Point2Tests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.IsNotNull(PythonEngineManager.Point2Class, "Point2Class should be loaded.");
        }

        [Test]
        public void Point2_ToJson()
        {
            // set up a point2 instance
            dynamic point2Instance = PythonEngineManager.Point2Class(0.0, 0.0);

            var result = point2Instance.to_json();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"x\": 0.0, \"y\": 0.0, \"json_ini\": null}";

            Assert.AreEqual(jsonString, result);
        }

        [Test]
        public void Point2_ToJsonUtf()
        {
            // set up a point2 instance
            dynamic point2Instance = PythonEngineManager.Point2Class(0.0, 0.0);

            var result = point2Instance.to_json_utf();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"x\": 0.0, \"y\": 0.0, \"json_ini\": null}";

            Assert.AreEqual(jsonString, result);
        }

        [Test]
        public void Point2_IniFromJson()
        {
            string json = "{\"x\": 5.0, \"y\": 10.0}";

            dynamic point2Instance = PythonEngineManager.Point2Class(j: json);

            Assert.AreEqual(5.0, point2Instance.x);
            Assert.AreEqual(10.0, point2Instance.y);
        }

        [Test]
        public void Point2_WithInvalidJson_ThrowsValueError()
        {
            // invalid json
            string json = "{\"x\": 5.0}";

            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.Point2Class(j: json));
            Assert.That(ex.Message, Does.Contain("JSON must contain 'x' and 'y' keys."));
        }

        [Test]
        public void Point2_WithNullJsonAndCoordinates_ThrowsValueError()
        { 
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.Point2Class());
            Assert.That(ex.Message, Does.Contain("x expected float. Got <class 'NoneType'> instead."));
        }


        [Test]
        public void Point2_WithIntegerXCoordinates_ThrowsValueError()
        {
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.Point2Class(x: -1, y: 0));
            // Output the result to the console
            //Console.WriteLine($"Result of int: {ex.Message}");
            Assert.That(ex.Message, Does.Contain("x expected float. Got <class 'int'> instead."));
        }

        [Test]
        public void Point2_WithIntegerYCoordinates_ThrowsValueError()
        {
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.Point2Class(x: -1.0, y: 0));
            // Output the result to the console
            Console.WriteLine($"Result of int: {ex.Message}");
            Assert.That(ex.Message, Does.Contain("y expected float. Got <class 'int'> instead."));
        }

        [Test]
        public void Point2_WithNegativeCoordinates_ThrowsValueError()
        {
            var point = PythonEngineManager.Point2Class(x: -1.0, y: 0.0);
            Assert.AreEqual(-1.0, point.x);
            Assert.AreEqual(0.0, point.y);
        }

        [Test]
        public void Point2_WithValidCoordinates_InitializesProperties()
        {
            var point = PythonEngineManager.Point2Class(x: 3.0, y: 4.0);

            Assert.AreEqual(3.0, point.x);
            Assert.AreEqual(4.0, point.y);
        }
    }
}