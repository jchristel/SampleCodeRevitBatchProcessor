using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;

namespace PythonTests.DataTests
{
    public class DataViewElevationTests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.IsNotNull(PythonEngineManager.DataViewElevationClass, "DataTypeProperties should be loaded.");
        }

        // Helper method to create JSON strings
        private string CreateJson(Dictionary<string, object> properties)
        {
            return Newtonsoft.Json.JsonConvert.SerializeObject(properties);
        }

        [Test]
        public void InitializeWithValidJson_ShouldSetPropertiesCorrectly()
        {
            // Arrange: valid JSON with id, data_type, bounding box, and tags fields
            var jsonString = CreateJson(new Dictionary<string, object>
            {
                { "data_type", "view_elevation" },
                { "id", 101 },
                { "bounding_box", new Dictionary<string, object>
                    {
                        { "DataType", "bounding box 2" },
                        { "bounding_box", new Dictionary<string, object>
                            {
                                { "min_x", 0.0 },
                                { "max_x", 10.0 },
                                { "min_y", 0.0 },
                                { "max_y", 10.0 }
                            }
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

            // Act
            var dataViewElevation = PythonEngineManager.DataViewElevationClass(jsonString);

            // Assert
            Assert.AreEqual(101, dataViewElevation.id, "Expected id to be initialized correctly.");
            Assert.IsNotNull(dataViewElevation.bounding_box, "Expected bounding_box to be initialized.");
            Assert.AreEqual(0.0, dataViewElevation.bounding_box.bounding_box.min_x, "Expected bounding_box.min_x to match input.");
            Assert.AreEqual(10.0, dataViewElevation.bounding_box.bounding_box.max_x, "Expected bounding_box.max_x to match input.");
            Assert.AreEqual(0.0, dataViewElevation.bounding_box.bounding_box.min_y, "Expected bounding_box.min_y to match input.");
            Assert.AreEqual(10.0, dataViewElevation.bounding_box.bounding_box.max_y, "Expected bounding_box.max_y to match input.");

            // Assert rotation and translation coords if relevant
            Assert.IsNotNull(dataViewElevation.bounding_box.rotation_coord, "Expected rotation_coord to be initialized.");
            Assert.AreEqual(3, dataViewElevation.bounding_box.rotation_coord.rows, "Expected rotation_coord rows to be 3.");
            Assert.AreEqual(3, dataViewElevation.bounding_box.rotation_coord.columns, "Expected rotation_coord columns to be 3.");

            Assert.IsNotNull(dataViewElevation.bounding_box.translation_coord, "Expected translation_coord to be initialized.");
            Assert.AreEqual(0.0, dataViewElevation.bounding_box.translation_coord.x, "Expected translation_coord.x to be 0.0.");
            Assert.AreEqual(0.0, dataViewElevation.bounding_box.translation_coord.y, "Expected translation_coord.y to be 0.0.");
            Assert.AreEqual(0.0, dataViewElevation.bounding_box.translation_coord.z, "Expected translation_coord.z to be 0.0.");
        }

        [Test]
        public void InitializeWithInvalidBoundingBoxType_ShouldThrowValueError()
        {
            // Arrange: JSON with invalid bounding_box type
            var jsonString = CreateJson(new Dictionary<string, object>
            {
                { "data_type", "view_elevation" },
                { "id", 101 },
                { "bounding_box", new Dictionary<string, object>
                    {
                        { "DataType", "bounding box 2" },
                        { "bounding_box", "invalidType" },
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

            // Act & Assert: initialization should throw a ValueError
            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.DataViewElevationClass(jsonString));
            StringAssert.Contains("Node view_elevation failed to initialise with: Node bounding box 2 failed to initialise with: Expecting value", ex.Message, "Expected ValueError for incorrect bounding_box type.");
        }

        [Test]
        public void InitializeWithMissingBoundingBoxField_ShouldThrowValueError()
        {
            // Arrange: JSON with missing bounding_box fields
            var jsonString = CreateJson(new Dictionary<string, object>
            {
                { "data_type", "view_elevation" },
                { "id", 101 },
                { "bounding_box", new Dictionary<string, object>
                    {
                        { "DataType", "bounding box 2" },
                        { "bounding_box", new Dictionary<string, object>
                            {
                                { "min_x", 0.0 },
                                { "max_x", 10.0 }
                            }
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

            // Act & Assert: initialization should throw a ValueError due to missing fields
            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.DataViewElevationClass(jsonString));
            StringAssert.Contains("Node view_elevation failed to initialise with: Node bounding box 2 failed to initialise with: JSON must contain 'max_x', 'max_y', 'min_x', 'min_y' keys.", ex.Message, "Expected ValueError for missing bounding box fields.");
        }

        [Test]
        public void EqualityCheckWithSameBoundingBoxAndTags_ShouldReturnTrue()
        {
            // Arrange: valid JSON with id, data_type, bounding box, and tags fields
            var jsonString = CreateJson(new Dictionary<string, object>
            {
                { "data_type", "view_elevation" },
                { "id", 101 },
                { "bounding_box", new Dictionary<string, object>
                    {
                        { "DataType", "bounding box 2" },
                        { "bounding_box", new Dictionary<string, object>
                            {
                                { "min_x", 0.0 },
                                { "max_x", 10.0 },
                                { "min_y", 0.0 },
                                { "max_y", 10.0 }
                            }
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

            // Act: Create two DataViewElevation instances using the same JSON data
            var dataViewElevation1 = PythonEngineManager.DataViewElevationClass(jsonString);
            var dataViewElevation2 = PythonEngineManager.DataViewElevationClass(jsonString);

            // Assert: The two instances should be equal
            Assert.IsTrue(dataViewElevation1 == dataViewElevation2, "Operator == should return true for instances with the same bounding box.");
        }
    }
}
