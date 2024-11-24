using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;

namespace PythonTests.DataTests
{
    public class DataTagTests
    {
        private string validJsonString;
        private Dictionary<string, object> validJsonDictionary;

        [SetUp]
        public void SetUp()
        {
            // Sample valid JSON for testing DataSheetViewPort
            validJsonDictionary = new Dictionary<string, object>
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
            };
        

            validJsonString = JsonConvert.SerializeObject(validJsonDictionary);
        }



        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.DataTagClass, Is.Not.Null, "DataTypeProperties should be loaded.");
        }

        // Helper method to create JSON strings
        private string CreateJson(Dictionary<string, object> properties)
        {
            return JsonConvert.SerializeObject(properties);
        }

        [Test]
        public void InitializeWithValidJson_ShouldSetPropertiesCorrectly()
        {
            

            // Act
            var dataTag = PythonEngineManager.DataTagClass(validJsonString);

            // Assert
            Assert.That(0.0, Is.EqualTo(dataTag.bounding_box.min_x), "Expected bounding_box.min_x to match input.");
            Assert.That(10.0, Is.EqualTo(dataTag.bounding_box.max_x), "Expected bounding_box.max_x to match input.");
            Assert.That(5.0, Is.EqualTo(dataTag.point.x), "Expected point.x to be 5.0.");
            Assert.That(5.0, Is.EqualTo(dataTag.point.y), "Expected point.y to be 5.0.");
            Assert.That(5.0, Is.EqualTo(dataTag.point.z), "Expected point.z to be 5.0.");
            Assert.That(1.0, Is.EqualTo(dataTag.elbow_location.x), "Expected elbow_location.x to be 1.0.");
            Assert.That("end_point", Is.EqualTo(dataTag.leader_end), "Expected leader_end to match input.");
            Assert.That("reference_point", Is.EqualTo(dataTag.leader_reference), "Expected leader_reference to match input.");
            Assert.That(123, Is.EqualTo(dataTag.leader_element_reference_id), "Expected leader_element_reference_id to be 123.");
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
                        { "min_x", 0.0 },
                        { "max_x", 10.0 },
                        { "min_y", 0.0 },
                        { "max_y", 10.0 },
                           
                    }
                },
                { "leader_element_reference_id", "invalid_id" }
            });

            // Act & Assert: initialization should throw a TypeError due to invalid leader_element_reference_id
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataTagClass(jsonString));
            Assert.That(ex.Message, Does.Contain("Expected 'leader_element_reference_id' to be an int"), "Expected TypeError for incorrect leader_element_reference_id type.");
        }

        [Test]
        public void EqualityCheckWithSameProperties_ShouldReturnTrue()
        { 
            var dataTag1 = PythonEngineManager.DataTagClass(validJsonString);
            var dataTag2 = PythonEngineManager.DataTagClass(validJsonString);

            // Act & Assert: The two instances should be equal
            Assert.That(dataTag1 == dataTag2, Is.True, "Operator == should return true for instances with the same properties.");
        }

        [Test]
        public void EqualityCheckWithDifferentProperties_ShouldReturnFalse()
        {
            

            var jsonString2 = CreateJson(new Dictionary<string, object>
        {
            { "data_type", "tag" },
            { "bounding_box", new Dictionary<string, object>
                {
                    { "DataType", "bounding box 2" },
                    { "min_x", 1.0 },
                    { "max_x", 10.0 },
                    { "min_y", 0.0 },
                    { "max_y", 10.0 },
                }
            },
            { "leader_element_reference_id", 123 }
        });

            var dataTag1 = PythonEngineManager.DataTagClass(validJsonString);
            var dataTag2 = PythonEngineManager.DataTagClass(jsonString2);

            // Act & Assert: The two instances should not be equal due to different bounding boxes
            Assert.That(dataTag1 == dataTag2, Is.False,"Operator == should return false for instances with different bounding boxes.");
        }

        [Test]
        public void EqualityCheckWithNullOtherObject_ShouldReturnFalse()
        {
            var dataTag = PythonEngineManager.DataTagClass(validJsonString);

            // Act & Assert: Equality with null object should return false
            Assert.That(dataTag == null,Is.False, "Operator == should return false when comparing with null.");
        }
    }
}
