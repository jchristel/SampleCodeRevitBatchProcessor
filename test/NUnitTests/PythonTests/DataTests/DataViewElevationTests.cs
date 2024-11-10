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
                },
                { "tags", new List<Dictionary<string, object>>
                    {
                        new Dictionary<string, object>
                        {
                            { "data_type", "tag" },
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
                                    }
                                }
                            },
                            { "point", new Dictionary<string, object>
                                {
                                    { "x", 5.0 },
                                    { "y", 5.0 },
                                    { "z", 5.0 }
                                }
                            },
                            { "elbow_location", new Dictionary<string, object>
                                {
                                    { "x", 1.0 },
                                    { "y", 1.0 },
                                    { "z", 1.0 }
                                }
                            },
                            { "leader_end", "end_point" },
                            { "leader_reference", "reference_point" },
                            { "leader_element_reference_id", 123 }
                        },
                        new Dictionary<string, object>
                        {
                            { "data_type", "tag" },
                            { "bounding_box", new Dictionary<string, object>
                                {
                                    { "DataType", "bounding box 2" },
                                    { "bounding_box", new Dictionary<string, object>
                                        {
                                            { "min_x", 1.0 },
                                            { "max_x", 11.0 },
                                            { "min_y", 1.0 },
                                            { "max_y", 11.0 }
                                        }
                                    }
                                }
                            },
                            { "point", new Dictionary<string, object>
                                {
                                    { "x", 6.0 },
                                    { "y", 6.0 },
                                    { "z", 6.0 }
                                }
                            },
                            { "elbow_location", new Dictionary<string, object>
                                {
                                    { "x", 2.0 },
                                    { "y", 2.0 },
                                    { "z", 2.0 }
                                }
                            },
                            { "leader_end", "start_point" },
                            { "leader_reference", "reference_point" },
                            { "leader_element_reference_id", 456 }
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

            // Assert tag properties
            Assert.IsNotNull(dataViewElevation.tags, "Expected tags list to be initialized.");
            Assert.AreEqual(2, dataViewElevation.tags.Count, "Expected two tags.");

            var firstTag = dataViewElevation.tags[0];
            Assert.AreEqual("tag", firstTag.data_type, "Expected first tag data_type to be 'tag'.");
            Assert.AreEqual(0.0, firstTag.bounding_box.bounding_box.min_x, "Expected first tag bounding_box.min_x to match input.");
            Assert.AreEqual(10.0, firstTag.bounding_box.bounding_box.max_x, "Expected first tag bounding_box.max_x to match input.");
            Assert.AreEqual(5.0, firstTag.point.x, "Expected first tag point.x to be 5.0.");
            Assert.AreEqual(5.0, firstTag.point.y, "Expected first tag point.y to be 5.0.");
            Assert.AreEqual(5.0, firstTag.point.z, "Expected first tag point.z to be 5.0.");
            Assert.AreEqual(1.0, firstTag.elbow_location.x, "Expected first tag elbow_location.x to be 1.0.");
            Assert.AreEqual(1.0, firstTag.elbow_location.y, "Expected first tag elbow_location.y to be 1.0.");
            Assert.AreEqual(1.0, firstTag.elbow_location.z, "Expected first tag elbow_location.z to be 1.0.");
            Assert.AreEqual("end_point", firstTag.leader_end, "Expected first tag leader_end to be 'end_point'.");
            Assert.AreEqual("reference_point", firstTag.leader_reference, "Expected first tag leader_reference to be 'reference_point'.");
            Assert.AreEqual(123, firstTag.leader_element_reference_id, "Expected first tag leader_element_reference_id to be 123.");

            var secondTag = dataViewElevation.tags[1];
            Assert.AreEqual("tag", secondTag.data_type, "Expected second tag data_type to be 'tag'.");
            Assert.AreEqual(1.0, secondTag.bounding_box.bounding_box.min_x, "Expected second tag bounding_box.min_x to match input.");
            Assert.AreEqual(11.0, secondTag.bounding_box.bounding_box.max_x, "Expected second tag bounding_box.max_x to match input.");
            Assert.AreEqual(6.0, secondTag.point.x, "Expected second tag point.x to be 6.0.");
            Assert.AreEqual(6.0, secondTag.point.y, "Expected second tag point.y to be 6.0.");
            Assert.AreEqual(6.0, secondTag.point.z, "Expected second tag point.z to be 6.0.");
            Assert.AreEqual(2.0, secondTag.elbow_location.x, "Expected second tag elbow_location.x to be 2.0.");
            Assert.AreEqual(2.0, secondTag.elbow_location.y, "Expected second tag elbow_location.y to be 2.0.");
            Assert.AreEqual(2.0, secondTag.elbow_location.z, "Expected second tag elbow_location.z to be 2.0.");
            Assert.AreEqual("start_point", secondTag.leader_end, "Expected second tag leader_end to be 'start_point'.");
            Assert.AreEqual("reference_point", secondTag.leader_reference, "Expected second tag leader_reference to be 'reference_point'.");
            Assert.AreEqual(456, secondTag.leader_element_reference_id, "Expected second tag leader_element_reference_id to be 456.");
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
                },
                { "tags", new List<Dictionary<string, object>>
                    {
                        new Dictionary<string, object>
                        {
                            { "data_type", "tag" },
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
                                    }
                                }
                            },
                            { "point", new Dictionary<string, object>
                                {
                                    { "x", 5.0 },
                                    { "y", 5.0 },
                                    { "z", 5.0 }
                                }
                            },
                            { "elbow_location", new Dictionary<string, object>
                                {
                                    { "x", 1.0 },
                                    { "y", 1.0 },
                                    { "z", 1.0 }
                                }
                            },
                            { "leader_end", "end_point" },
                            { "leader_reference", "reference_point" },
                            { "leader_element_reference_id", 123 }
                        },
                        new Dictionary<string, object>
                        {
                            { "data_type", "tag" },
                            { "bounding_box", new Dictionary<string, object>
                                {
                                    { "DataType", "bounding box 2" },
                                    { "bounding_box", new Dictionary<string, object>
                                        {
                                            { "min_x", 1.0 },
                                            { "max_x", 11.0 },
                                            { "min_y", 1.0 },
                                            { "max_y", 11.0 }
                                        }
                                    }
                                }
                            },
                            { "point", new Dictionary<string, object>
                                {
                                    { "x", 6.0 },
                                    { "y", 6.0 },
                                    { "z", 6.0 }
                                }
                            },
                            { "elbow_location", new Dictionary<string, object>
                                {
                                    { "x", 2.0 },
                                    { "y", 2.0 },
                                    { "z", 2.0 }
                                }
                            },
                            { "leader_end", "start_point" },
                            { "leader_reference", "reference_point" },
                            { "leader_element_reference_id", 456 }
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

        [Test]
        public void EqualityCheckWithDifferentTags_ShouldReturnTrue()
        {
            // Arrange: valid JSON with id, data_type, bounding box, and tags fields
            var jsonString1 = CreateJson(new Dictionary<string, object>
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
                },
                { "tags", new List<Dictionary<string, object>>
                    {
                        new Dictionary<string, object>
                        {
                            { "data_type", "tag" },
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
                                    }
                                }
                            },
                            { "point", new Dictionary<string, object>
                                {
                                    { "x", 6.0 },
                                    { "y", 5.0 },
                                    { "z", 5.0 }
                                }
                            },
                            { "elbow_location", new Dictionary<string, object>
                                {
                                    { "x", 1.0 },
                                    { "y", 1.0 },
                                    { "z", 1.0 }
                                }
                            },
                            { "leader_end", "end_point" },
                            { "leader_reference", "reference_point" },
                            { "leader_element_reference_id", 123 }
                        },
                        new Dictionary<string, object>
                        {
                            { "data_type", "tag" },
                            { "bounding_box", new Dictionary<string, object>
                                {
                                    { "DataType", "bounding box 2" },
                                    { "bounding_box", new Dictionary<string, object>
                                        {
                                            { "min_x", 1.0 },
                                            { "max_x", 11.0 },
                                            { "min_y", 1.0 },
                                            { "max_y", 11.0 }
                                        }
                                    }
                                }
                            },
                            { "point", new Dictionary<string, object>
                                {
                                    { "x", 6.0 },
                                    { "y", 6.0 },
                                    { "z", 6.0 }
                                }
                            },
                            { "elbow_location", new Dictionary<string, object>
                                {
                                    { "x", 2.0 },
                                    { "y", 2.0 },
                                    { "z", 2.0 }
                                }
                            },
                            { "leader_end", "start_point" },
                            { "leader_reference", "reference_point" },
                            { "leader_element_reference_id", 456 }
                        }
                    }
                }
            });


            // Arrange: valid JSON with id, data_type, bounding box, and tags fields
            var jsonString2 = CreateJson(new Dictionary<string, object>
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
                },
                { "tags", new List<Dictionary<string, object>>
                    {
                        new Dictionary<string, object>
                        {
                            { "data_type", "tag" },
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
                                    }
                                }
                            },
                            { "point", new Dictionary<string, object>
                                {
                                    { "x", 5.0 },
                                    { "y", 5.0 },
                                    { "z", 5.0 }
                                }
                            },
                            { "elbow_location", new Dictionary<string, object>
                                {
                                    { "x", 1.0 },
                                    { "y", 1.0 },
                                    { "z", 1.0 }
                                }
                            },
                            { "leader_end", "end_point" },
                            { "leader_reference", "reference_point" },
                            { "leader_element_reference_id", 123 }
                        },
                        new Dictionary<string, object>
                        {
                            { "data_type", "tag" },
                            { "bounding_box", new Dictionary<string, object>
                                {
                                    { "DataType", "bounding box 2" },
                                    { "bounding_box", new Dictionary<string, object>
                                        {
                                            { "min_x", 1.0 },
                                            { "max_x", 11.0 },
                                            { "min_y", 1.0 },
                                            { "max_y", 11.0 }
                                        }
                                    }
                                }
                            },
                            { "point", new Dictionary<string, object>
                                {
                                    { "x", 6.0 },
                                    { "y", 6.0 },
                                    { "z", 6.0 }
                                }
                            },
                            { "elbow_location", new Dictionary<string, object>
                                {
                                    { "x", 2.0 },
                                    { "y", 2.0 },
                                    { "z", 2.0 }
                                }
                            },
                            { "leader_end", "start_point" },
                            { "leader_reference", "reference_point" },
                            { "leader_element_reference_id", 456 }
                        }
                    }
                }
            });
            // Act: Create two DataViewElevation instances using the same JSON data
            var dataViewElevation1 = PythonEngineManager.DataViewElevationClass(jsonString1);
            var dataViewElevation2 = PythonEngineManager.DataViewElevationClass(jsonString2);

            // Assert: The two instances should not be equal
            Assert.IsTrue(dataViewElevation1 != dataViewElevation2, "Operator != should return true for instances with the same bounding box.");
            Assert.IsFalse(dataViewElevation1 == dataViewElevation2, "Operator = should return false for instances with the same bounding box.");
        }
    }
}
