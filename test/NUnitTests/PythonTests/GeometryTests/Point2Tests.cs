using IronPython.Runtime.Exceptions;
using PythonTests.Setup;

namespace PythonTests.GeometryTests
{
    public class Point2Tests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.Point2Class, Is.Not.Null, "Point2Class should be loaded.");
        }

        [Test]
        public void Point2_ToJson()
        {
            // set up a point2 instance
            dynamic point2Instance = PythonEngineManager.Point2Class(0.0, 0.0);

            var result = point2Instance.to_json_ordered();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"json_ini\": null, \"x\": 0.0, \"y\": 0.0}";

            Assert.That(jsonString, Is.EqualTo(result));
        }

        [Test]
        public void Point2_ToJsonUtf()
        {
            // set up a point2 instance
            dynamic point2Instance = PythonEngineManager.Point2Class(0.0, 0.0);

            var result = point2Instance.to_json_utf_ordered();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"json_ini\": null, \"x\": 0.0, \"y\": 0.0}";

            Assert.That(jsonString, Is.EqualTo(result));
        }

        [Test]
        public void Point2_IniFromJson()
        {
            string json = "{\"x\": 5.0, \"y\": 10.0}";

            dynamic point2Instance = PythonEngineManager.Point2Class(j: json);

            Assert.That(5.0, Is.EqualTo(point2Instance.x));
            Assert.That(10.0, Is.EqualTo(point2Instance.y));
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
            Assert.That(-1.0, Is.EqualTo(point.x));
            Assert.That(0.0, Is.EqualTo(point.y));
        }

        [Test]
        public void Point2_WithValidCoordinates_InitializesProperties()
        {
            var point = PythonEngineManager.Point2Class(x: 3.0, y: 4.0);

            Assert.That(3.0, Is.EqualTo(point.x));
            Assert.That(4.0, Is.EqualTo(point.y));
        }
    }
}