using IronPython.Runtime.Exceptions;
using Newtonsoft.Json;
using PythonTests.Setup;

namespace PythonTests.DataTests.PropertyTests
{
    public class DataElementGeometry
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.DataElementGeometryBaseClass, Is.Not.Null, "DataElementGeometryBase should be loaded.");
        }

        [Test]
        public void Constructor_ValidJson_ShouldInitializeCorrectly()
        {
            // Arrange
            var jsonString = "{\"polygon\":{\"data_type\":\"polygon\",\"rotation_coord\":{\"columns\":3,\"data\":[[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]],\"rows\":3},\"DataType\":\"polygon\",\"inner_loops\":[],\"translation_coord\":{\"x\":0.0,\"z\":0.0,\"json_ini\":null,\"y\":0.0},\"outer_loop\":[{\"x\":0.0,\"y\":0.0,\"json_ini\":null},{\"x\":0.1,\"y\":1.0,\"json_ini\":null},{\"x\":0.0,\"y\":0.0,\"json_ini\":null}]}}";
        
            // Act
            dynamic instance = PythonEngineManager.DataElementGeometryBaseClass(jsonString);

            // Assert
            Assert.That(instance.polygon, Is.Not.Null);
            Assert.That(0.0,Is.EqualTo( instance.polygon.outer_loop[0].x));
            Assert.That(0.0, Is.EqualTo(instance.polygon.outer_loop[0].y));
            Assert.That(0.1, Is.EqualTo(instance.polygon.outer_loop[1].x));
            Assert.That(1.0, Is.EqualTo(instance.polygon.outer_loop[1].y));
            Assert.That(0, Is.EqualTo(instance.polygon.inner_loops.Count));
        }

        [Test]
        public void Constructor_InvalidJson_ShouldThrowJsonDecodeError()
        {
            // Arrange
            string invalidJsonString = "{ invalid json }";

            // Act & Assert
            Assert.Throws<ValueErrorException>(() => PythonEngineManager.DataElementGeometryBaseClass(invalidJsonString));
        }

        [Test]
        public void Constructor_EmptyJson_ShouldThrowTypeException()
        {
            // Arrange
            var emptyJsonDict = new Dictionary<string, object>();
            string jsonString = JsonConvert.SerializeObject(emptyJsonDict);
            Console.WriteLine(jsonString);
            // Act
            dynamic instance = PythonEngineManager.DataElementGeometryBaseClass(jsonString);

            // Assert
            Assert.That(instance.polygon, Is.Not.Null);
            Assert.That(0, Is.EqualTo(instance.polygon.outer_loop.Count));
            Assert.That(0, Is.EqualTo(instance.polygon.inner_loops.Count));
        }

        [Test]
        public void Constructor_PolygonDataMissing_ShouldInitializeEmptyPolygon()
        {
            // Arrange
            var jsonDictWithoutPolygon = new Dictionary<string, object>
            {
                { "otherProperty", "someValue" }
            };
            string jsonString = JsonConvert.SerializeObject(jsonDictWithoutPolygon);

            // Act
            dynamic instance = PythonEngineManager.DataElementGeometryBaseClass(jsonString);

            // Assert
            Assert.That(instance.polygon, Is.Not.Null);
            Assert.That(0, Is.EqualTo(instance.polygon.outer_loop.Count));
            Assert.That(0, Is.EqualTo(instance.polygon.inner_loops.Count));
        }

        [Test]
        public void Constructor_PolygonDataMalformed_ShouldThrowPythonException()
        {
            // Arrange
            var jsonDictWithMalformedPolygon = new Dictionary<string, object>
            {
                { "polygon", new List<object> { "not_a_dictionary" } }
            };
            string jsonString = JsonConvert.SerializeObject(jsonDictWithMalformedPolygon);
            //Console.WriteLine(jsonString);
            // Act & Assert
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataElementGeometryBaseClass(jsonString));
            Console.WriteLine(ex.Message);
            Assert.That(ex.Message, Does.Contain("failed to initialise"));
        }

        [Test]
        public void Constructor_NullJson_ShouldInitializeEmptyPolygon()
        {
            // Act
            dynamic instance = PythonEngineManager.DataElementGeometryBaseClass(null);

            // Assert
            Assert.That(instance.polygon, Is.Not.Null);
            Assert.That(0, Is.EqualTo(instance.polygon.outer_loop.Count));
            Assert.That(0, Is.EqualTo(instance.polygon.inner_loops.Count));
            Console.WriteLine(instance.to_json_ordered());
        }

        
        public void DataElementGeometry_ToJson()
        {
            // Arrange
            var jsonString = "{\"polygon\": {\"data_type\": \"polygon\", \"rotation_coord\":{\"columns\":3,\"data\":[[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]],\"rows\":3},\"DataType\":\"polygon\",\"inner_loops\":[],\"translation_coord\":{\"x\":0.0,\"z\":0.0,\"json_ini\":null,\"y\":0.0},\"outer_loop\":[{\"x\":0.0,\"y\":0.0,\"json_ini\":null},{\"x\":0.1,\"y\":1.0,\"json_ini\":null},{\"x\":0.0,\"y\":0.0,\"json_ini\":null}]}}";

            // Act
            dynamic instance = PythonEngineManager.DataElementGeometryBaseClass(jsonString);
            var result = instance.to_json_ordered();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
           
            Assert.That(jsonString, Is.EqualTo(result));
        }
    }
}
