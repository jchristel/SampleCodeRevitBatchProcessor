using IronPython.Runtime.Exceptions;
using PythonTests.Setup;

namespace PythonTests.GeometryTests
{
    public class Point3Tests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.Point3Class, Is.Not.Null, "Point3Class should be loaded.");
        }

        [Test]
        public void Point3_ToJson()
        {
            // set up a point2 instance
            dynamic point3Instance = PythonEngineManager.Point3Class(0.0, 0.0,0.0);

            var result = point3Instance.to_json();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"x\": 0.0, \"y\": 0.0, \"z\": 0.0, \"json_ini\": null}";

            Assert.That(jsonString, Is.EqualTo(result));
        }

        [Test]
        public void Point3_toJsonUtf()
        {
            // set up a point2 instance
            dynamic point3Instance = PythonEngineManager.Point3Class(0.0, 0.0,0.0);

            var result = point3Instance.to_json_utf();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"x\": 0.0, \"y\": 0.0, \"z\": 0.0, \"json_ini\": null}";

            Assert.That(jsonString, Is.EqualTo(result));
        }

        [Test]
        public void Point3_IniFromJson()
        {
            string json = "{\"x\": 5.0, \"y\": 10.0, \"z\": 20.0}";

            dynamic point3Instance = PythonEngineManager.Point3Class(j: json);

            Assert.That(5.0, Is.EqualTo(point3Instance.x));
            Assert.That(10.0, Is.EqualTo(point3Instance.y));
            Assert.That(20.0, Is.EqualTo(point3Instance.z));
        }

        [Test]
        public void Point3_WithInvalidJson_ThrowsValueError()
        {
            // invalid json
            string json = "{\"x\": 5.0}";

            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.Point3Class(j: json));
            Assert.That(ex.Message, Does.Contain("JSON must contain 'x' and 'y' keys."));
        }

        [Test]
        public void Point3_WithNullJsonAndCoordinates_ThrowsValueError()
        {
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.Point3Class());
            Assert.That(ex.Message, Does.Contain("x expected float. Got <class 'NoneType'> instead."));
        }


        [Test]
        public void Point3_WithIntegerXCoordinates_ThrowsValueError()
        {
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.Point3Class(x: -1, y: 0, z:0));
            // Output the result to the console
            //Console.WriteLine($"Result of int: {ex.Message}");
            Assert.That(ex.Message, Does.Contain("x expected float. Got <class 'int'> instead."));
        }

        [Test]
        public void Point3_WithIntegerYCoordinates_ThrowsValueError()
        {
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.Point3Class(x: -1.0, y: 0, z:0));
            // Output the result to the console
            Console.WriteLine($"Result of int: {ex.Message}");
            Assert.That(ex.Message, Does.Contain("y expected float. Got <class 'int'> instead."));
        }

        [Test]
        public void Point3_WithIntegerZCoordinates_ThrowsValueError()
        {
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.Point3Class(x: -1.0, y: 0.0, z: 0));
            // Output the result to the console
            Console.WriteLine($"Result of int: {ex.Message}");
            Assert.That(ex.Message, Does.Contain("z expected float. Got <class 'int'> instead."));
        }

        [Test]
        public void Point3_WithNegativeCoordinates_ThrowsValueError()
        {
            var point = PythonEngineManager.Point3Class(x: -1.0, y: 0.0, z:-0.1);
            Assert.That(-1.0, Is.EqualTo(point.x));
            Assert.That(0.0, Is.EqualTo(point.y));
            Assert.That(-0.1, Is.EqualTo(point.z));
        }

        [Test]
        public void Point3_WithValidCoordinates_InitializesProperties()
        {
            var point = PythonEngineManager.Point3Class(x: 3.0, y: 4.0, z:1.0);

            Assert.That(3.0, Is.EqualTo(point.x));
            Assert.That(4.0, Is.EqualTo(point.y));
            Assert.That(1.0, Is.EqualTo(point.z));
        }
    }
}
