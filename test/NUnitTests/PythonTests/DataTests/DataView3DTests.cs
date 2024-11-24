using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;

namespace PythonTests.DataTests
{
    public class DataView3DTests
    {
        private string validJsonString;
        private Dictionary<string, object> validJsonDictionary;


        [SetUp]
        public void SetUp()
        {
            // Sample valid JSON for testing DataSheetViewPort
            validJsonDictionary = new Dictionary<string, object>
            {
                { "data_type", "view_3d" },
                { "id", 101 },
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
            };


            validJsonString = JsonConvert.SerializeObject(validJsonDictionary);
        }

        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.DataViewThreeDClass, Is.Not.Null, "DataTypeProperties should be loaded.");
        }

        // Helper method to create JSON strings
        private string CreateJson(Dictionary<string, object> properties)
        {
            return Newtonsoft.Json.JsonConvert.SerializeObject(properties);
        }

        [Test]
        public void InitializeWithValidJson_ShouldSetPropertiesCorrectly()
        {
            
            // Act
            var dataViewThreeD = PythonEngineManager.DataViewThreeDClass(validJsonString);

            // Assert
            Assert.That(101, Is.EqualTo(dataViewThreeD.id), "Expected id to be initialized correctly.");
            Assert.That(dataViewThreeD.bounding_box, Is.Not.Null, "Expected bounding_box to be initialized.");
            Assert.That(0.0, Is.EqualTo(dataViewThreeD.bounding_box.min_x), "Expected bounding_box.min_x to match input.");
            Assert.That(10.0, Is.EqualTo(dataViewThreeD.bounding_box.max_x), "Expected bounding_box.max_x to match input.");
            Assert.That(0.0, Is.EqualTo(dataViewThreeD.bounding_box.min_y), "Expected bounding_box.min_y to match input.");
            Assert.That(10.0, Is.EqualTo(dataViewThreeD.bounding_box.max_y), "Expected bounding_box.max_y to match input.");

            // Assert rotation and translation coords if relevant
            Assert.That(dataViewThreeD.bounding_box.rotation_coord, Is.Not.Null, "Expected rotation_coord to be initialized.");
            Assert.That(3, Is.EqualTo(dataViewThreeD.bounding_box.rotation_coord.rows), "Expected rotation_coord rows to be 3.");
            Assert.That(3, Is.EqualTo(dataViewThreeD.bounding_box.rotation_coord.columns), "Expected rotation_coord columns to be 3.");

            Assert.That(dataViewThreeD.bounding_box.translation_coord, Is.Not.Null, "Expected translation_coord to be initialized.");
            Assert.That(0.0, Is.EqualTo(dataViewThreeD.bounding_box.translation_coord.x), "Expected translation_coord.x to be 0.0.");
            Assert.That(0.0, Is.EqualTo(dataViewThreeD.bounding_box.translation_coord.y), "Expected translation_coord.y to be 0.0.");
            Assert.That(0.0, Is.EqualTo(dataViewThreeD.bounding_box.translation_coord.z), "Expected translation_coord.z to be 0.0.");
        }

        [Test]
        public void InitializeWithInvalidBoundingBoxType_ShouldThrowValueError()
        {
            // Arrange: JSON with invalid bounding_box type

            // Arrange: valid JSON with id, data_type, and bounding box fields
            var jsonString = CreateJson(new Dictionary<string, object>
            {
                { "data_type", "view_3d" },
                { "id", 101 },
                { "bounding_box", new Dictionary<string, object>
                    {
                        { "DataType", "bounding box 2" },
                        { "bounding_box", "invalidType"
                        },
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
            });

            // Act & Assert: initialization should throw a TypeError
            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.DataViewThreeDClass(jsonString));
            Assert.That(ex.Message, Does.Contain("Node view_3d failed to initialise with: JSON must contain"), "Expected ValueError for incorrect bounding_box type.");
        }

        [Test]
        public void InitializeWithMissingBoundingBoxField_ShouldThrowValueError()
        {
            // Arrange: valid JSON with id, data_type, and bounding box fields
            var jsonString = CreateJson(new Dictionary<string, object>
            {
                { "data_type", "view_3d" },
                { "id", 101 },
                { "bounding_box", new Dictionary<string, object>
                    {
                        { "DataType", "bounding box 2" },
                        
                                { "min_x", 0.0 },
                                { "max_x", 10.0 },
                           
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
            });

            // Act & Assert: initialization should throw a TypeError due to missing fields
            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.DataViewThreeDClass(jsonString));
            Assert.That(ex.Message, Does.Contain("Node view_3d failed to initialise with: JSON must contain"), "Expected ValueError for missing bounding box fields.");
        }

        [Test]
        public void EqualityCheckWithSameBoundingBox_ShouldReturnTrue()
        {
            
            var dataView1 = PythonEngineManager.DataViewThreeDClass(validJsonString);
            var dataView2 = PythonEngineManager.DataViewThreeDClass(validJsonString);

            // Act & Assert
            Assert.That(dataView1 == dataView2, Is.True, "Operator == should return true for instances with the same bounding box.");
            //Assert.IsTrue(dataView1.Equals(dataView2), "Equals method should return true for instances with the same bounding box.");
        }

        [Test]
        public void EqualityCheckWithDifferentBoundingBox_ShouldReturnFalse()
        {
            
            // Arrange: valid JSON with id, data_type, and bounding box fields
            var jsonString2 = CreateJson(new Dictionary<string, object>
            {
                { "data_type", "view_3d" },
                { "id", 101 },
                { "bounding_box", new Dictionary<string, object>
                    {
                        { "DataType", "bounding box 2" },
                        
                                { "min_x", 10.0 },
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
            });
            var dataView1 = PythonEngineManager.DataViewThreeDClass(validJsonString);
            var dataView2 = PythonEngineManager.DataViewThreeDClass(jsonString2);

            Console.WriteLine(dataView2.to_json());
            Console.WriteLine(dataView1.to_json());

            // Act & Assert
            Assert.That(dataView1 == dataView2, Is.False, "Operator == should return false for instances with different bounding boxes.");
            //Assert.IsFalse(dataView1.Equals(dataView2), "Equals method should return false for instances with different bounding boxes.");
        }
    }
}
