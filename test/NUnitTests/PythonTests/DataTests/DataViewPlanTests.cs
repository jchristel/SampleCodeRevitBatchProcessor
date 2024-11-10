using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;

namespace PythonTests.DataTests
{
    public class DataViewPlanTests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.IsNotNull(PythonEngineManager.DataViewPlanClass, "DataTypeProperties should be loaded.");
        }

        // Helper method to create JSON strings
        private string CreateJson(Dictionary<string, object> properties)
        {
            return Newtonsoft.Json.JsonConvert.SerializeObject(properties);
        }

        [Test]
        public void DataViewPlan_Constructor_ValidJson_ShouldInitializeCorrectly()
        {
            // Sample valid JSON for testing
            var jsonString = CreateJson(new Dictionary<string, object>
            {
                { "data_type", "view_plan" },
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
                },
                { "tags", new List<Dictionary<string, object>>
                    {
                        new Dictionary<string, object>
                        {
                            { "data_type", "tag" },
                            { "bounding_box", new Dictionary<string, object>
                                {
                                    { "min_x", 0.0 },
                                    { "max_x", 10.0 },
                                    { "min_y", 0.0 },
                                    { "max_y", 10.0 }
                                }
                            },
                            { "point", new Dictionary<string, object> { { "x", 5.0 }, { "y", 5.0 }, { "z", 5.0 } } },
                            { "elbow_location", new Dictionary<string, object> { { "x", 1.0 }, { "y", 1.0 }, { "z", 1.0 } } },
                            { "leader_end", "end_point" },
                            { "leader_reference", "reference_point" },
                            { "leader_element_reference_id", 123 }
                        }
                    }
                }
            });


            // Act
            var dataViewPlan = PythonEngineManager.DataViewPlanClass(jsonString);

            // Assert
            Assert.AreEqual("view_plan", dataViewPlan.data_type);
            Assert.AreEqual(101, dataViewPlan.id);
            Assert.IsNotNull(dataViewPlan.bounding_box);
            Assert.AreEqual(0.0, dataViewPlan.bounding_box.bounding_box.min_x);
            Assert.AreEqual(10.0, dataViewPlan.bounding_box.bounding_box.max_x);
            Assert.AreEqual(0.0, dataViewPlan.bounding_box.bounding_box.min_y);
            Assert.AreEqual(10.0, dataViewPlan.bounding_box.bounding_box.max_y);
            Assert.IsNotNull(dataViewPlan.tags);
            Assert.AreEqual(1, dataViewPlan.tags.Count);
            Assert.AreEqual("tag", dataViewPlan.tags[0].data_type);
        }

        [Test]
        public void DataViewPlan_Constructor_EmptyJson_ShouldInitializeWithDefaults()
        {
            // Act
            var dataViewPlan = PythonEngineManager.DataViewPlanClass();

            // Assert
            Assert.AreEqual("view_plan", dataViewPlan.data_type);
            Assert.AreEqual(-1, dataViewPlan.id);
            Assert.IsNotNull(dataViewPlan.bounding_box);
            Assert.AreEqual(0.0, dataViewPlan.bounding_box.bounding_box.min_x);
            Assert.AreEqual(0.0, dataViewPlan.bounding_box.bounding_box.max_x);
            Assert.AreEqual(0.0, dataViewPlan.bounding_box.bounding_box.min_y);
            Assert.AreEqual(0.0, dataViewPlan.bounding_box.bounding_box.max_y);
            Assert.IsNotNull(dataViewPlan.tags);
            Assert.AreEqual(0, dataViewPlan.tags.Count);
        }

        [Test]
        public void DataViewPlan_Constructor_InvalidJson_ShouldThrowException()
        {
            // Arrange
            var invalidJsonString = "Invalid JSON String";

            // Act & Assert
            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.DataViewPlanClass(invalidJsonString));
            Assert.That(ex.Message, Does.Contain("Expecting value: line 1"));
        }

        [Test]
        public void DataViewPlan_Equals_ValidComparison_ShouldReturnTrue()
        {
            var jsonString = CreateJson(new Dictionary<string, object>
            {
                { "data_type", "view_plan" },
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
                },
                { "tags", new List<Dictionary<string, object>>
                    {
                        new Dictionary<string, object>
                        {
                            { "data_type", "tag" },
                            { "bounding_box", new Dictionary<string, object>
                                {
                                    { "min_x", 0.0 },
                                    { "max_x", 10.0 },
                                    { "min_y", 0.0 },
                                    { "max_y", 10.0 }
                                }
                            },
                            { "point", new Dictionary<string, object> { { "x", 5.0 }, { "y", 5.0 }, { "z", 5.0 } } },
                            { "elbow_location", new Dictionary<string, object> { { "x", 1.0 }, { "y", 1.0 }, { "z", 1.0 } } },
                            { "leader_end", "end_point" },
                            { "leader_reference", "reference_point" },
                            { "leader_element_reference_id", 123 }
                        }
                    }
                }
            });
            // Arrange
            var dataViewPlan1 = PythonEngineManager.DataViewPlanClass(jsonString);
            var dataViewPlan2 = PythonEngineManager.DataViewPlanClass(jsonString);

            // Act
            var areEqual = dataViewPlan1==dataViewPlan2;

            // Assert
            Assert.IsTrue(areEqual);
        }

        [Test]
        public void DataViewPlan_Equals_InvalidComparison_ShouldReturnFalse()
        {
            var jsonString = CreateJson(new Dictionary<string, object>
            {
                { "data_type", "view_plan" },
                { "id", 101 },
                { "bounding_box", new Dictionary<string, object>
                    {
                        { "min_x", 0.0 },
                        { "max_x", 10.0 },
                        { "min_y", 0.0 },
                        { "max_y", 10.0 }
                    }
                },
                { "tags", new List<Dictionary<string, object>>
                    {
                        new Dictionary<string, object>
                        {
                            { "data_type", "tag" },
                            { "bounding_box", new Dictionary<string, object>
                                {
                                    { "min_x", 0.0 },
                                    { "max_x", 10.0 },
                                    { "min_y", 0.0 },
                                    { "max_y", 10.0 }
                                }
                            },
                            { "point", new Dictionary<string, object> { { "x", 5.0 }, { "y", 5.0 }, { "z", 5.0 } } },
                            { "elbow_location", new Dictionary<string, object> { { "x", 1.0 }, { "y", 1.0 }, { "z", 1.0 } } },
                            { "leader_end", "end_point" },
                            { "leader_reference", "reference_point" },
                            { "leader_element_reference_id", 123 }
                        }
                    }
                }
            });
            // Arrange
            var dataViewPlan1 = PythonEngineManager.DataViewPlanClass(jsonString);
            var dataViewPlan2 = PythonEngineManager.DataViewPlanClass(); // Empty object

            // Act
            var areEqual = dataViewPlan1.Equals(dataViewPlan2);

            // Assert
            Assert.IsFalse(areEqual);
        }

        [Test]
        public void DataViewPlan_Equals_NonDataViewPlan_ShouldReturnNotImplemented()
        {
            // Sample valid JSON for testing
            var jsonString = CreateJson(new Dictionary<string, object>
            {
                { "data_type", "view_plan" },
                { "id", 101 },
                { "bounding_box", new Dictionary<string, object>
                    {
                        { "min_x", 0.0 },
                        { "max_x", 10.0 },
                        { "min_y", 0.0 },
                        { "max_y", 10.0 }
                    }
                },
                { "tags", new List<Dictionary<string, object>>
                    {
                        new Dictionary<string, object>
                        {
                            { "data_type", "tag" },
                            { "bounding_box", new Dictionary<string, object>
                                {
                                    { "min_x", 0.0 },
                                    { "max_x", 10.0 },
                                    { "min_y", 0.0 },
                                    { "max_y", 10.0 }
                                }
                            },
                            { "point", new Dictionary<string, object> { { "x", 5.0 }, { "y", 5.0 }, { "z", 5.0 } } },
                            { "elbow_location", new Dictionary<string, object> { { "x", 1.0 }, { "y", 1.0 }, { "z", 1.0 } } },
                            { "leader_end", "end_point" },
                            { "leader_reference", "reference_point" },
                            { "leader_element_reference_id", 123 }
                        }
                    }
                }
            });

            // Arrange
            var dataViewPlan = PythonEngineManager.DataViewPlanClass(jsonString);
            var nonDataViewPlan = new object();

            // Act
            var areEqual = dataViewPlan == nonDataViewPlan;

            // Assert
            Assert.AreEqual(areEqual, false);
        }

        [Test]
        public void DataViewPlan_Nequality_Comparison_ShouldReturnTrueForNonEqualObjects()
        {
            // Sample valid JSON for testing
            var jsonString = CreateJson(new Dictionary<string, object>
            {
                { "data_type", "view_plan" },
                { "id", 101 },
                { "bounding_box", new Dictionary<string, object>
                    {
                        { "min_x", 0.0 },
                        { "max_x", 10.0 },
                        { "min_y", 0.0 },
                        { "max_y", 10.0 }
                    }
                },
                { "tags", new List<Dictionary<string, object>>
                    {
                        new Dictionary<string, object>
                        {
                            { "data_type", "tag" },
                            { "bounding_box", new Dictionary<string, object>
                                {
                                    { "min_x", 0.0 },
                                    { "max_x", 10.0 },
                                    { "min_y", 0.0 },
                                    { "max_y", 10.0 }
                                }
                            },
                            { "point", new Dictionary<string, object> { { "x", 5.0 }, { "y", 5.0 }, { "z", 5.0 } } },
                            { "elbow_location", new Dictionary<string, object> { { "x", 1.0 }, { "y", 1.0 }, { "z", 1.0 } } },
                            { "leader_end", "end_point" },
                            { "leader_reference", "reference_point" },
                            { "leader_element_reference_id", 123 }
                        }
                    }
                }
            });

            // Arrange
            var dataViewPlan1 = PythonEngineManager.DataViewPlanClass(jsonString);
            var dataViewPlan2 = PythonEngineManager.DataViewPlanClass(); // Empty object

            // Act
            var areNotEqual = dataViewPlan1 != dataViewPlan2;

            // Assert
            Assert.IsTrue(areNotEqual);
        }

        [Test]
        public void DataViewPlan_Constructor_InvalidJsonType_ShouldThrowException()
        {
            // Arrange
            var invalidJson = new List<string> { "invalid", "json" };

            // Act & Assert
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataViewPlanClass(invalidJson));
            Assert.That(ex.Message, Does.Contain("Argument j supplied must be of type string or type dictionary"));
        }
    }
}
