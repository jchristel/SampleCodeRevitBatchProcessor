using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;

namespace PythonTests.DataTests
{
    public class DataSheetTests
    {

        private string validJsonString;
        private Dictionary<string, object> validJsonDictionary;

        [SetUp]
        public void SetUp()
        {
            // Sample valid JSON for testing DataSheet
            validJsonDictionary = new Dictionary<string, object>
            {
                { "data_type", "sheet" },
                { "instance_properties", new Dictionary<string, object> { { "data_type", "instance" } } },
                { "type_properties", new Dictionary<string, object> { { "data_type", "type" } } },
                { "bounding_box", new Dictionary<string, object>
                        {
                            { "DataType", "bounding box 2" },
                            
                            { "min_x", 0.0 },
                            { "max_x", 10.0 },
                            { "min_y", 0.0 },
                            { "max_y", 10.0 },
                               
                            { "rotation_coord", new Dictionary<string, object>
                                {
                                    { "data", new List<List<double>> { new List<double> { 0.0, 0.0, 0.0 }, new List<double> { 0.0, 0.0, 0.0 }, new List<double> { 0.0, 0.0, 0.0 } } },
                                    { "rows", 3 },
                                    { "columns", 3 }
                                }
                            },
                            { "translation_coord", new Dictionary<string, object>
                                {
                                    { "x", 0.0 },
                                    { "y", 0.0 },
                                    { "z", 0.0 },
                                    { "json_ini", null }
                                }
                            }
                        }
                },
                { "view_ports", new List<Dictionary<string, object>> {
                    new Dictionary<string, object> {
                        { "data_type", "sheet view port" },
                        { "view_id", 1001 },
                        { "vp_type", PythonEngineManager.DataViewPortTypeNames.THREE_D},
                        { "bounding_box", new Dictionary<string, object>
                            {
                                { "DataType", "bounding box 2" },
                                { "min_x", 0.0 },
                                { "max_x", 10.0 },
                                { "min_y", 0.0 },
                                { "max_y", 10.0 },
                                { "rotation_coord", new Dictionary<string, object>
                                    {
                                        { "data", new List<List<double>> { new List<double> { 0.0, 0.0, 0.0 }, new List<double> { 0.0, 0.0, 0.0 }, new List<double> { 0.0, 0.0, 0.0 } } },
                                        { "rows", 3 },
                                        { "columns", 3 }
                                    }
                                },
                                { "translation_coord", new Dictionary<string, object>
                                    {
                                        { "x", 0.0 },
                                        { "y", 0.0 },
                                        { "z", 0.0 },
                                        { "json_ini", null }
                                    }
                                }
                            }
                        },
                        { "centre_point", new Dictionary<string, object>
                            {
                                { "x", 5.0 },
                                { "y", 5.0 }
                            }
                        },
                        { "view", new Dictionary<string, object>
                            {
                                { "data_type", "view_3d" },
                                { "bounding_box", new Dictionary<string, object>
                                    {
                                        { "DataType", "bounding box 2" },
                                        { "min_x", 0.0 },
                                        { "max_x", 10.0 },
                                        { "min_y", 0.0 },
                                        { "max_y", 10.0 },
                                        { "rotation_coord", new Dictionary<string, object>
                                            {
                                                { "data", new List<List<double>> { new List<double> { 0.0, 0.0, 0.0 }, new List<double> { 0.0, 0.0, 0.0 }, new List<double> { 0.0, 0.0, 0.0 } } },
                                                { "rows", 3 },
                                                { "columns", 3 }
                                            }
                                        },
                                        { "translation_coord", new Dictionary<string, object>
                                            {
                                                { "x", 0.0 },
                                                { "y", 0.0 },
                                                { "z", 0.0 },
                                                { "json_ini", null }
                                            }
                                        }
                                    }
                                }

                            }
                        }
                    }
                } 
            }
        };

            validJsonString = JsonConvert.SerializeObject(validJsonDictionary);
        }

        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.IsNotNull(PythonEngineManager.DataSheetClass, "DataTypeProperties should be loaded.");
        }


        [Test]
        public void DataSheet_Constructor_ValidJson_ShouldInitializeCorrectly()
        {
            // Act
            var dataSheet = PythonEngineManager.DataSheetClass(validJsonString);

            // Assert
            Assert.AreEqual("sheet", dataSheet.data_type);
            Assert.IsNotNull(dataSheet.instance_properties);
            Assert.IsNotNull(dataSheet.type_properties);
            Assert.AreEqual(1, dataSheet.view_ports.Count);
            Assert.IsNotNull(dataSheet.view_ports[0]);
            Assert.AreEqual(1001, dataSheet.view_ports[0].view_id);
            Assert.AreEqual(PythonEngineManager.DataViewPortTypeNames.THREE_D, dataSheet.view_ports[0].vp_type);
            Assert.AreEqual(0.0, dataSheet.bounding_box.min_x);
            Assert.AreEqual(10.0, dataSheet.bounding_box.max_x);
        }

        [Test]
        public void DataSheet_Constructor_InvalidJsonType_ShouldThrowException()
        {
            // Arrange
            var invalidJson = new List<string> { "invalid", "json" };

            // Act & Assert
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataSheetClass(invalidJson));
            Assert.That(ex.Message, Does.Contain("Argument j supplied must be of type string or type dictionary"));
        }

        [Test]
        public void DataSheet_Constructor_EmptyJson_ShouldInitializeWithDefaults()
        {
            // Act
            var dataSheet = PythonEngineManager.DataSheetClass();

            // Assert
            Assert.AreEqual("sheet", dataSheet.data_type);
            Assert.IsNotNull(dataSheet.instance_properties);
            Assert.IsNotNull(dataSheet.type_properties);
            Assert.AreEqual(0, dataSheet.view_ports.Count);
            Assert.AreEqual(double.PositiveInfinity, dataSheet.bounding_box.min_x);
            Assert.AreEqual(double.NegativeInfinity, dataSheet.bounding_box.max_x);
        }

        [Test]
        public void DataSheet_Constructor_InvalidData_ShouldThrowException()
        {
            // Arrange
            var invalidJson = new Dictionary<string, object>
            {
                { "bounding_box", "invalid" }
            };

            // Act & Assert
            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.DataSheetClass(JsonConvert.SerializeObject(invalidJson)));
            Assert.That(ex.Message, Does.Contain("Node sheet failed to initialise with: Expecting value: line 1"));
        }

        [Test]
        public void DataSheet_Equals_ValidComparison_ShouldReturnTrue()
        {
            // Arrange
            var dataSheet1 = PythonEngineManager.DataSheetClass(validJsonString);
            var dataSheet2 = PythonEngineManager.DataSheetClass(validJsonString);

            // Act
            var areEqual = dataSheet1==dataSheet2;

            // Assert
            Assert.IsTrue(areEqual);
        }

        [Test]
        public void DataSheet_Equals_InvalidComparison_ShouldReturnFalse()
        {
            // Arrange
            var dataSheet1 = PythonEngineManager.DataSheetClass(validJsonString);
            var dataSheet2 = PythonEngineManager.DataSheetClass(); // Empty object

            // Act
            var areEqual = dataSheet1.Equals(dataSheet2);

            // Assert
            Assert.IsFalse(areEqual);
        }

        [Test]
        public void DataSheet_Equals_NonDataSheetObject_ShouldReturnNotImplemented()
        {
            // Arrange
            var dataSheet = PythonEngineManager.DataSheetClass(validJsonString);
            var nonDataSheetObject = new object();

            // Act
            var areEqual = dataSheet==nonDataSheetObject;

            // Assert
            Assert.AreEqual(areEqual,false);
        }

        [Test]
        public void DataSheet_Nequality_Comparison_ShouldReturnTrueForNonEqualObjects()
        {
            // Arrange
            var dataSheet1 = PythonEngineManager.DataSheetClass(validJsonString);
            var dataSheet2 = PythonEngineManager.DataSheetClass(); // Empty object

            // Act
            var areNotEqual = dataSheet1 != dataSheet2;

            // Assert
            Assert.IsTrue(areNotEqual);
        }

        [Test]
        public void DataSheet_ViewPorts_ShouldInitializeCorrectly()
        {
            // Arrange
            var viewPortJson = new Dictionary<string, object>
            {
                { "vp_type", "schedule" },
                { "view_id", 2002 },
                { "bounding_box", new Dictionary<string, object> { { "min_x", 0.0 }, { "max_x", 10.0 }, { "min_y", 0.0 }, { "max_y", 10.0 } } }
            };

            var jsonWithViewPort = new Dictionary<string, object>
            {
                { "data_type", "sheet" },
                { "view_ports", new List<Dictionary<string, object>> { viewPortJson } }
            };

            // Act
            var dataSheet = PythonEngineManager.DataSheetClass(JsonConvert.SerializeObject(jsonWithViewPort));

            // Assert
            Assert.AreEqual(1, dataSheet.view_ports.Count);
            Assert.AreEqual(2002, dataSheet.view_ports[0].view_id);
            Assert.AreEqual(PythonEngineManager.DataViewPortTypeNames.SCHEDULE, dataSheet.view_ports[0].vp_type);
        }
    }
}
