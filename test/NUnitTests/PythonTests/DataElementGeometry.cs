using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Scripting.Hosting;
using IronPython.Runtime.Exceptions;
using Newtonsoft.Json;

namespace PythonTests
{
    public class DataElementGeometry
    {
        ScriptEngine _engine;
        ScriptScope _scope;

        private dynamic _dataElementGeometryBaseClass;

        [SetUp]
        public void Setup()
        {
            // get a python engine
            ScriptEngine engine = PythonRunner.SetupEngine();
            _scope = engine.CreateScope();

            // get the repository path
            string repoPath = PythonRunner.GetRepositoryPath();

            // set path to data element geometry class
            var pythonFilePath_data_element_geometry = Path.Combine(repoPath, @"duHast\Data\Objects\Properties\data_element_geometry.py");
            
            //run the file
            engine.ExecuteFile(pythonFilePath_data_element_geometry, _scope);
            
            _dataElementGeometryBaseClass = _scope.GetVariable("DataElementGeometryBase");
            
            //store the engine instance
            _engine = engine;
        }

        [Test]
        public void Constructor_ValidJson_ShouldInitializeCorrectly()
        {
            // Arrange
            var jsonString = "{\"polygon\":{\"data_type\":\"polygon\",\"rotation_coord\":{\"columns\":3,\"data\":[[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]],\"rows\":3},\"DataType\":\"polygon\",\"inner_loops\":[],\"translation_coord\":{\"x\":0.0,\"z\":0.0,\"json_ini\":null,\"y\":0.0},\"outer_loop\":[{\"x\":0.0,\"y\":0.0,\"json_ini\":null},{\"x\":0.1,\"y\":1.0,\"json_ini\":null},{\"x\":0.0,\"y\":0.0,\"json_ini\":null}]}}";
        
            // Act
            dynamic instance = _dataElementGeometryBaseClass(jsonString);

            // Assert
            Assert.IsNotNull(instance.polygon);
            Assert.AreEqual(0.0, instance.polygon.outer_loop[0].x);
            Assert.AreEqual(0.0, instance.polygon.outer_loop[0].y);
            Assert.AreEqual(0.1, instance.polygon.outer_loop[1].x);
            Assert.AreEqual(1.0, instance.polygon.outer_loop[1].y);
            Assert.AreEqual(0, instance.polygon.inner_loops.Count);
        }

        [Test]
        public void Constructor_InvalidJson_ShouldThrowJsonDecodeError()
        {
            // Arrange
            string invalidJsonString = "{ invalid json }";

            // Act & Assert
            Assert.Throws<ValueErrorException>(() => _dataElementGeometryBaseClass(invalidJsonString));
        }

        [Test]
        public void Constructor_EmptyJson_ShouldThrowTypeException()
        {
            // Arrange
            var emptyJsonDict = new Dictionary<string, object>();
            string jsonString = JsonConvert.SerializeObject(emptyJsonDict);
            Console.WriteLine(jsonString);
            // Act
            dynamic instance = _dataElementGeometryBaseClass(jsonString);

            // Assert
            Assert.IsNotNull(instance.polygon);
            Assert.AreEqual(0, instance.polygon.outer_loop.Count);
            Assert.AreEqual(0, instance.polygon.inner_loops.Count);
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
            dynamic instance = _dataElementGeometryBaseClass(jsonString);

            // Assert
            Assert.IsNotNull(instance.polygon);
            Assert.AreEqual(0, instance.polygon.outer_loop.Count);
            Assert.AreEqual(0, instance.polygon.inner_loops.Count);
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
            var ex = Assert.Throws<TypeErrorException>(() => _dataElementGeometryBaseClass(jsonString));
            Console.WriteLine(ex.Message);
            Assert.That(ex.Message, Does.Contain("failed to initialise"));
        }

        [Test]
        public void Constructor_NullJson_ShouldInitializeEmptyPolygon()
        {
            // Act
            dynamic instance = _dataElementGeometryBaseClass(null);

            // Assert
            Assert.IsNotNull(instance.polygon);
            Assert.AreEqual(0, instance.polygon.outer_loop.Count);
            Assert.AreEqual(0, instance.polygon.inner_loops.Count);
            Console.WriteLine(instance.to_json());
        }

       
        public void DataElementGeometry_ToJson()
        {
            // Arrange
            var jsonString = "{\"polygon\": {\"data_type\": \"polygon\", \"rotation_coord\":{\"columns\":3,\"data\":[[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]],\"rows\":3},\"DataType\":\"polygon\",\"inner_loops\":[],\"translation_coord\":{\"x\":0.0,\"z\":0.0,\"json_ini\":null,\"y\":0.0},\"outer_loop\":[{\"x\":0.0,\"y\":0.0,\"json_ini\":null},{\"x\":0.1,\"y\":1.0,\"json_ini\":null},{\"x\":0.0,\"y\":0.0,\"json_ini\":null}]}}";

            // Act
            dynamic instance = _dataElementGeometryBaseClass(jsonString);
            var result = instance.to_json();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
           
            Assert.AreEqual(jsonString, result);
        }
    }
}
