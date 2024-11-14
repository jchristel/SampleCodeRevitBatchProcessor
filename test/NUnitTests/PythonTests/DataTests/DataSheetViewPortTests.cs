using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;

namespace PythonTests.DataTests
{
    public class DataSheetViewPortTests
    {
        private string validJsonString;
        private Dictionary<string, object> validJsonDictionary;

        [SetUp]
        public void SetUp()
        {
            // Sample valid JSON for testing DataSheetViewPort
            validJsonDictionary = new Dictionary<string, object>
            {
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
            };

                validJsonString = JsonConvert.SerializeObject(validJsonDictionary);
            }


        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.IsNotNull(PythonEngineManager.DataSheetViewPortClass, "DataTypeProperties should be loaded.");
        }

        [Test]
        public void DataSheetViewPort_Constructor_ValidJson_ShouldInitializeCorrectly()
        {
            // Act
            var dataSheetViewPort = PythonEngineManager.DataSheetViewPortClass(validJsonString);

            // Assert
            Assert.AreEqual("sheet view port", dataSheetViewPort.data_type);
            Assert.AreEqual(1001, dataSheetViewPort.view_id);
            Assert.AreEqual(PythonEngineManager.DataViewPortTypeNames.THREE_D, dataSheetViewPort.vp_type);
            Assert.IsNotNull(dataSheetViewPort.bounding_box);
            Assert.AreEqual(0.0, dataSheetViewPort.bounding_box.min_x);
            Assert.AreEqual(10.0, dataSheetViewPort.bounding_box.max_x);
            Assert.AreEqual(0.0, dataSheetViewPort.bounding_box.min_y);
            Assert.AreEqual(10.0, dataSheetViewPort.bounding_box.max_y);
            Assert.AreEqual(5.0, dataSheetViewPort.centre_point.x);
            Assert.AreEqual(5.0, dataSheetViewPort.centre_point.y);


            Assert.AreEqual(0.0, dataSheetViewPort.view.bounding_box.min_x);
            Assert.AreEqual(10.0, dataSheetViewPort.view.bounding_box.max_x);
            Assert.AreEqual(0.0, dataSheetViewPort.view.bounding_box.min_y);
            Assert.AreEqual(10.0, dataSheetViewPort.view.bounding_box.max_y);
        }

        [Test]
        public void DataSheetViewPort_Constructor_InvalidJsonType_ShouldThrowException()
        {
            // Arrange
            var invalidJson = new List<string> { "invalid", "json" };

            // Act & Assert
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataSheetViewPortClass(invalidJson));
            Assert.That(ex.Message, Does.Contain("Argument j supplied must be of type string or type dictionary"));
        }

        [Test]
        public void DataSheetViewPort_Constructor_EmptyJson_ShouldInitializeWithDefaults()
        {
            // Act
            var dataSheetViewPort = PythonEngineManager.DataSheetViewPortClass();

            // Assert
            Assert.AreEqual("sheet view port", dataSheetViewPort.data_type);
            Assert.AreEqual(-1, dataSheetViewPort.view_id);
            Assert.AreEqual(PythonEngineManager.DataViewPortTypeNames.FLOOR_PLAN, dataSheetViewPort.vp_type);
            Assert.IsNotNull(dataSheetViewPort.bounding_box);
            Assert.AreEqual(0.0, dataSheetViewPort.bounding_box.min_x);
            Assert.AreEqual(0.0, dataSheetViewPort.bounding_box.max_x);
            Assert.AreEqual(0.0, dataSheetViewPort.bounding_box.min_y);
            Assert.AreEqual(0.0, dataSheetViewPort.bounding_box.max_y);
            Assert.AreEqual(0.0, dataSheetViewPort.centre_point.x);
            Assert.AreEqual(0.0, dataSheetViewPort.centre_point.y);

            Assert.AreEqual(-1, dataSheetViewPort.view.id);
            Assert.AreEqual(0.0, dataSheetViewPort.view.bounding_box.min_x);
            Assert.AreEqual(0.0, dataSheetViewPort.view.bounding_box.max_x);
            Assert.AreEqual(0.0, dataSheetViewPort.view.bounding_box.min_y);
            Assert.AreEqual(0.0, dataSheetViewPort.view.bounding_box.max_y);
            Assert.AreEqual(0, dataSheetViewPort.view.tags.Count);
        }

        [Test]
        public void DataSheetViewPort_Constructor_InvalidViewPortType_ShouldThrowException()
        {
            // Arrange
            var invalidJson = new Dictionary<string, object>
        {
            { "vp_type", "unsupported_view_port_type" }
        };

            // Act & Assert
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataSheetViewPortClass(JsonConvert.SerializeObject(invalidJson)));
            Assert.That(ex.Message, Does.Contain("Unsupported viewport type"));
        }

        [Test]
        public void DataSheetViewPort_Equals_ValidComparison_ShouldReturnTrue()
        {
            // Arrange
            var dataSheetViewPort1 = PythonEngineManager.DataSheetViewPortClass(validJsonString);
            var dataSheetViewPort2 = PythonEngineManager.DataSheetViewPortClass(validJsonString);

            // Act
            var areEqual = dataSheetViewPort1==dataSheetViewPort2;

            // Assert
            Assert.IsTrue(areEqual);
        }

        [Test]
        public void DataSheetViewPort_Equals_InvalidComparison_ShouldReturnFalse()
        {
            // Arrange
            var dataSheetViewPort1 = PythonEngineManager.DataSheetViewPortClass(validJsonString);
            var dataSheetViewPort2 = PythonEngineManager.DataSheetViewPortClass(); // Empty object

            // Act
            var areEqual = dataSheetViewPort1.Equals(dataSheetViewPort2);

            // Assert
            Assert.IsFalse(areEqual);
        }

        [Test]
        public void DataSheetViewPort_Equals_NonDataSheetViewPort_ShouldReturnNotImplemented()
        {
            // Arrange
            var dataSheetViewPort = PythonEngineManager.DataSheetViewPortClass(validJsonString);
            var nonDataSheetViewPort = new object();

            // Act
            var areEqual = dataSheetViewPort==nonDataSheetViewPort;

            // Assert
            Assert.AreEqual(areEqual, false);
        }

        [Test]
        public void DataSheetViewPort_Nequality_Comparison_ShouldReturnTrueForNonEqualObjects()
        {
            // Arrange
            var dataSheetViewPort1 = PythonEngineManager.DataSheetViewPortClass(validJsonString);
            var dataSheetViewPort2 = PythonEngineManager.DataSheetViewPortClass(); // Empty object

            // Act
            var areNotEqual = dataSheetViewPort1 != dataSheetViewPort2;

            // Assert
            Assert.IsTrue(areNotEqual);
        }

    }
}
