using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;

namespace PythonTests.DataTests
{
    public class DataViewElevationTests
    {
        private string validJsonString;
        private Dictionary<string, object> validJsonDictionary;

        [SetUp]
        public void SetUp()
        {
            // Sample valid JSON for testing DataSheetViewPort
            validJsonDictionary = new Dictionary<string, object>
            {
                { "data_type", "view_elevation" },
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
                },
                { "tags", new List<Dictionary<string, object>>
                    {
                        new Dictionary<string, object>
                        {
                            { "data_type", "tag" },
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
                                    { "min_x", 1.0 },
                                    { "max_x", 11.0 },
                                    { "min_y", 1.0 },
                                    { "max_y", 11.0 },
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
            };


            validJsonString = JsonConvert.SerializeObject(validJsonDictionary);
        }

        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.DataViewElevationClass, Is.Not.Null, "DataTypeProperties should be loaded.");
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
            var dataViewElevation = PythonEngineManager.DataViewElevationClass(validJsonString);

            // Assert
            Assert.That(101, Is.EqualTo(dataViewElevation.id), "Expected id to be initialized correctly.");
            Assert.That(dataViewElevation.bounding_box,Is.Not.Null, "Expected bounding_box to be initialized.");
            Assert.That(0.0, Is.EqualTo(dataViewElevation.bounding_box.min_x), "Expected bounding_box.min_x to match input.");
            Assert.That(10.0, Is.EqualTo(dataViewElevation.bounding_box.max_x), "Expected bounding_box.max_x to match input.");
            Assert.That(0.0, Is.EqualTo(dataViewElevation.bounding_box.min_y), "Expected bounding_box.min_y to match input.");
            Assert.That(10.0, Is.EqualTo(dataViewElevation.bounding_box.max_y), "Expected bounding_box.max_y to match input.");

            // Assert rotation and translation coords if relevant
            Assert.That(dataViewElevation.bounding_box.rotation_coord, Is.Not.Null, "Expected rotation_coord to be initialized.");
            Assert.That(3, Is.EqualTo(dataViewElevation.bounding_box.rotation_coord.rows), "Expected rotation_coord rows to be 3.");
            Assert.That(3, Is.EqualTo(dataViewElevation.bounding_box.rotation_coord.columns), "Expected rotation_coord columns to be 3.");

            Assert.That(dataViewElevation.bounding_box.translation_coord, Is.Not.Null, "Expected translation_coord to be initialized.");
            Assert.That(0.0, Is.EqualTo(dataViewElevation.bounding_box.translation_coord.x), "Expected translation_coord.x to be 0.0.");
            Assert.That(0.0, Is.EqualTo(dataViewElevation.bounding_box.translation_coord.y), "Expected translation_coord.y to be 0.0.");
            Assert.That(0.0, Is.EqualTo(dataViewElevation.bounding_box.translation_coord.z), "Expected translation_coord.z to be 0.0.");

            // Assert tag properties
            Assert.That(dataViewElevation.tags, Is.Not.Null, "Expected tags list to be initialized.");
            Assert.That(2, Is.EqualTo(dataViewElevation.tags.Count), "Expected two tags.");

            var firstTag = dataViewElevation.tags[0];
            Assert.That("tag", Is.EqualTo(firstTag.data_type), "Expected first tag data_type to be 'tag'.");
            Assert.That(0.0, Is.EqualTo(firstTag.bounding_box.min_x), "Expected first tag bounding_box.min_x to match input.");
            Assert.That(10.0, Is.EqualTo(firstTag.bounding_box.max_x), "Expected first tag bounding_box.max_x to match input.");
            Assert.That(5.0, Is.EqualTo(firstTag.point.x), "Expected first tag point.x to be 5.0.");
            Assert.That(5.0, Is.EqualTo(firstTag.point.y), "Expected first tag point.y to be 5.0.");
            Assert.That(5.0, Is.EqualTo(firstTag.point.z), "Expected first tag point.z to be 5.0.");
            Assert.That(1.0, Is.EqualTo(firstTag.elbow_location.x), "Expected first tag elbow_location.x to be 1.0.");
            Assert.That(1.0, Is.EqualTo(firstTag.elbow_location.y), "Expected first tag elbow_location.y to be 1.0.");
            Assert.That(1.0, Is.EqualTo(firstTag.elbow_location.z), "Expected first tag elbow_location.z to be 1.0.");
            Assert.That("end_point", Is.EqualTo(firstTag.leader_end), "Expected first tag leader_end to be 'end_point'.");
            Assert.That("reference_point", Is.EqualTo(firstTag.leader_reference), "Expected first tag leader_reference to be 'reference_point'.");
            Assert.That(123, Is.EqualTo(firstTag.leader_element_reference_id), "Expected first tag leader_element_reference_id to be 123.");

            var secondTag = dataViewElevation.tags[1];
            Assert.That("tag", Is.EqualTo(secondTag.data_type), "Expected second tag data_type to be 'tag'.");
            Assert.That(1.0, Is.EqualTo(secondTag.bounding_box.min_x), "Expected second tag bounding_box.min_x to match input.");
            Assert.That(11.0, Is.EqualTo(secondTag.bounding_box.max_x), "Expected second tag bounding_box.max_x to match input.");
            Assert.That(6.0, Is.EqualTo(secondTag.point.x), "Expected second tag point.x to be 6.0.");
            Assert.That(6.0, Is.EqualTo(secondTag.point.y), "Expected second tag point.y to be 6.0.");
            Assert.That(6.0, Is.EqualTo(secondTag.point.z), "Expected second tag point.z to be 6.0.");
            Assert.That(2.0, Is.EqualTo(secondTag.elbow_location.x), "Expected second tag elbow_location.x to be 2.0.");
            Assert.That(2.0, Is.EqualTo(secondTag.elbow_location.y), "Expected second tag elbow_location.y to be 2.0.");
            Assert.That(2.0, Is.EqualTo(secondTag.elbow_location.z), "Expected second tag elbow_location.z to be 2.0.");
            Assert.That("start_point", Is.EqualTo(secondTag.leader_end), "Expected second tag leader_end to be 'start_point'.");
            Assert.That("reference_point", Is.EqualTo(secondTag.leader_reference), "Expected second tag leader_reference to be 'reference_point'.");
            Assert.That(456, Is.EqualTo(secondTag.leader_element_reference_id), "Expected second tag leader_element_reference_id to be 456.");
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
            Assert.That(ex.Message, Does.Contain("Node view_elevation failed to initialise with: JSON must contain 'max_x',"), "Expected ValueError for incorrect bounding_box type.");
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

            // Act & Assert: initialization should throw a ValueError due to missing fields
            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.DataViewElevationClass(jsonString));
            Assert.That(ex.Message, Does.Contain("Node view_elevation failed to initialise with: JSON must contain 'max_x',"), "Expected ValueError for missing bounding box fields.");
        }

        [Test]
        public void EqualityCheckWithSameBoundingBoxAndTags_ShouldReturnTrue()
        {

            // Act: Create two DataViewElevation instances using the same JSON data
            var dataViewElevation1 = PythonEngineManager.DataViewElevationClass(validJsonString);
            var dataViewElevation2 = PythonEngineManager.DataViewElevationClass(validJsonString);

            // Assert: The two instances should be equal
            Assert.That(dataViewElevation1 == dataViewElevation2, Is.True, "Operator == should return true for instances with the same bounding box.");
        }

        [Test]
        public void EqualityCheckWithDifferentTags_ShouldReturnTrue()
        {


            // Arrange: valid JSON with id, data_type, bounding box, and tags fields
            var jsonString2 = CreateJson(new Dictionary<string, object>
            {
                { "data_type", "view_elevation" },
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
                },
                { "tags", new List<Dictionary<string, object>>
                    {
                        new Dictionary<string, object>
                        {
                            { "data_type", "tag" },
                            { "bounding_box", new Dictionary<string, object>
                                {
                                    { "DataType", "bounding box 2" },
                                   
                                            { "min_x", 0.0 },
                                            { "max_x", 10.0 },
                                            { "min_y", 0.0 },
                                            { "max_y", 10.0 },
                                       
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
                                    
                                    { "min_x", 1.0 },
                                    { "max_x", 11.0 },
                                    { "min_y", 1.0 },
                                    { "max_y", 11.0 },
                                        
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
                            { "leader_element_reference_id", 1000 }
                        }
                    }
                }
            });
            // Act: Create two DataViewElevation instances using the same JSON data
            var dataViewElevation1 = PythonEngineManager.DataViewElevationClass(validJsonString);
            var dataViewElevation2 = PythonEngineManager.DataViewElevationClass(jsonString2);

            // Assert: The two instances should not be equal
            Assert.That(dataViewElevation1 != dataViewElevation2, Is.True, "Operator != should return true for instances with the different tags.");
            Assert.That(dataViewElevation1 == dataViewElevation2, Is.False, "Operator = should return false for instances with the different tags.");
        }
    }
}
