using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;

namespace PythonTests.DataTests
{
    public class DataTagTests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.IsNotNull(PythonEngineManager.DataTagClass, "DataTypeProperties should be loaded.");
        }

        // Helper method to create JSON strings
        private string CreateJson(Dictionary<string, object> properties)
        {
            return JsonConvert.SerializeObject(properties);
        }

        [Test]
        public void InitializeWithValidJson_ShouldSetPropertiesCorrectly()
        {
            // Arrange: valid JSON with bounding box, point, elbow_location, and other properties
            var jsonString = CreateJson(new Dictionary<string, object>
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
            });

            // Act
            var dataTag = PythonEngineManager.DataTagClass(jsonString);

            // Assert
            Assert.AreEqual(0.0, dataTag.bounding_box.bounding_box.min_x, "Expected bounding_box.min_x to match input.");
            Assert.AreEqual(10.0, dataTag.bounding_box.bounding_box.max_x, "Expected bounding_box.max_x to match input.");
            Assert.AreEqual(5.0, dataTag.point.x, "Expected point.x to be 5.0.");
            Assert.AreEqual(5.0, dataTag.point.y, "Expected point.y to be 5.0.");
            Assert.AreEqual(5.0, dataTag.point.z, "Expected point.z to be 5.0.");
            Assert.AreEqual(1.0, dataTag.elbow_location.x, "Expected elbow_location.x to be 1.0.");
            Assert.AreEqual("end_point", dataTag.leader_end, "Expected leader_end to match input.");
            Assert.AreEqual("reference_point", dataTag.leader_reference, "Expected leader_reference to match input.");
            Assert.AreEqual(123, dataTag.leader_element_reference_id, "Expected leader_element_reference_id to be 123.");
        }

        [Test]
        public void InitializeWithInvalidLeaderElementReferenceId_ShouldThrowTypeError()
        {
            // Arrange: JSON with an invalid leader_element_reference_id type (string instead of int)
            var jsonString = CreateJson(new Dictionary<string, object>
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
                { "leader_element_reference_id", "invalid_id" }
            });

            // Act & Assert: initialization should throw a TypeError due to invalid leader_element_reference_id
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataTagClass(jsonString));
            StringAssert.Contains("Expected 'leader_element_reference_id' to be an int", ex.Message, "Expected TypeError for incorrect leader_element_reference_id type.");
        }

        [Test]
        public void EqualityCheckWithSameProperties_ShouldReturnTrue()
        {
            // Arrange: valid JSON with bounding box, point, elbow_location, and other properties
            var jsonString = CreateJson(new Dictionary<string, object>
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
            });

            var dataTag1 = PythonEngineManager.DataTagClass(jsonString);
            var dataTag2 = PythonEngineManager.DataTagClass(jsonString);

            // Act & Assert: The two instances should be equal
            Assert.IsTrue(dataTag1 == dataTag2, "Operator == should return true for instances with the same properties.");
        }

        [Test]
        public void EqualityCheckWithDifferentProperties_ShouldReturnFalse()
        {
            // Arrange: JSON with different bounding box values
            var jsonString1 = CreateJson(new Dictionary<string, object>
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
            { "leader_element_reference_id", 123 }
        });

            var jsonString2 = CreateJson(new Dictionary<string, object>
        {
            { "data_type", "tag" },
            { "bounding_box", new Dictionary<string, object>
                {
                    { "DataType", "bounding box 2" },
                    { "bounding_box", new Dictionary<string, object>
                        {
                            { "min_x", 1.0 },
                            { "max_x", 10.0 },
                            { "min_y", 0.0 },
                            { "max_y", 10.0 }
                        }
                    }
                }
            },
            { "leader_element_reference_id", 123 }
        });

            var dataTag1 = PythonEngineManager.DataTagClass(jsonString1);
            var dataTag2 = PythonEngineManager.DataTagClass(jsonString2);

            // Act & Assert: The two instances should not be equal due to different bounding boxes
            Assert.IsFalse(dataTag1 == dataTag2, "Operator == should return false for instances with different bounding boxes.");
        }

        [Test]
        public void EqualityCheckWithNullOtherObject_ShouldReturnFalse()
        {
            // Arrange: valid JSON to create a DataTag object
            var jsonString = CreateJson(new Dictionary<string, object>
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
            }
        });

            var dataTag = PythonEngineManager.DataTagClass(jsonString);

            // Act & Assert: Equality with null object should return false
            Assert.IsFalse(dataTag == null, "Operator == should return false when comparing with null.");
        }
    }
}
