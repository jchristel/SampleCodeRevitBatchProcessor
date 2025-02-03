using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;


namespace PythonTests.DataTests.PropertyTests
{
    public class DataScheduleSegmentTests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.DataScheduleSegmentClass, Is.Not.Null, "DataScheduleSegment should be loaded.");
        }

        // Helper method to create a JSON string for DataScheduleSegment initialization
        private string CreateJson(int index, double height)
        {
            return JsonConvert.SerializeObject(new { index, height });
        }

        [Test]
        public void InitializeWithValidJson_ShouldSetProperties()
        {
            // Arrange: JSON data with both index and height
            var jsonString = CreateJson(3, 12.5);

            // Act: initialize instance with JSON data
            var segment = PythonEngineManager.DataScheduleSegmentClass(jsonString);

            // Assert: verify the values are correctly set
            Assert.That(3, Is.EqualTo(segment.index), "Expected index to be 3.");
            Assert.That(12.5, Is.EqualTo(segment.height), "Expected height to be 12.5.");
        }

        [Test]
        public void InitializeWithPartialJson_ShouldUseDefaultsForMissingValues()
        {
            // Arrange: JSON data with only the height field
            var jsonString = JsonConvert.SerializeObject(new { height = 9.8 });

            // Act: initialize instance with partial JSON data
            var segment = PythonEngineManager.DataScheduleSegmentClass(jsonString);

            // Assert: height should be set from JSON, index should use default
            Assert.That(0, Is.EqualTo(segment.index), "Expected default index of 0.");
            Assert.That(9.8, Is.EqualTo(segment.height), "Expected height to be 9.8.");
        }

        [Test]
        public void InitializeWithEmptyJson_ShouldUseDefaultValues()
        {
            // Arrange: an empty JSON object
            var jsonString = JsonConvert.SerializeObject(new { });

            // Act: initialize instance with empty JSON
            var segment = PythonEngineManager.DataScheduleSegmentClass(jsonString);

            // Assert: index and height should use default values
            Assert.That(0, Is.EqualTo(segment.index), "Expected default index of 0.");
            Assert.That(0.0, Is.EqualTo(segment.height), "Expected default height of 0.0.");
        }

        [Test]
        public void InitializeWithInvalidJsonType_ShouldThrowValueError()
        {
            // Arrange: JSON with a string instead of an integer for index
            var jsonString = JsonConvert.SerializeObject(new { index = "invalid", height = 15.2 });
            Console.WriteLine(jsonString);
            // Act & Assert: expect initialization to throw an error
            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.DataScheduleSegmentClass(jsonString));
            Assert.That(ex.Message, Does.Contain("Node schedule segment failed to initialise with: index needs to be of type int"));
        }

        [Test]
        public void InitializeWithNonJsonString_ShouldThrowValueError()
        {
            // Arrange: an invalid JSON string
            var jsonString = "non-json string";

            // Act & Assert: expect initialization to throw an error
            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.DataScheduleSegmentClass(jsonString));
            Assert.That(ex.Message, Does.Contain("Expecting value:"));
        }

        [Test]
        public void EqualInstances_ShouldReturnTrue()
        {
            // Arrange: create JSON representation for identical objects
            var jsonString = CreateJson(1, 10.5);

            // Act: initialize two instances with the same JSON data
            var segmentA = PythonEngineManager.DataScheduleSegmentClass(jsonString);
            var segmentB = PythonEngineManager.DataScheduleSegmentClass(jsonString);

            // Assert: the two instances are equal
            Assert.That(segmentA == segmentB, Is.True, "Expected equal instances to return true.");
        }

        [Test]
        public void NonEqualInstances_ShouldReturnFalse()
        {
            // Arrange: create JSON representation for different objects
            var jsonA = CreateJson(1, 10.5);
            var jsonB = CreateJson(2, 15.0);

            // Act: initialize two instances with different JSON data
            var segmentA = PythonEngineManager.DataScheduleSegmentClass(jsonA);
            var segmentB = PythonEngineManager.DataScheduleSegmentClass(jsonB);

            // Assert: the two instances are not equal
            Assert.That(segmentA != segmentB, Is.True, "Expected non-equal instances to return true.");
        }

        [Test]
        public void SameIndexDifferentHeight_ShouldReturnFalse()
        {
            // Arrange: create JSON for instances with the same index but different height
            var jsonA = CreateJson(1, 10.5);
            var jsonB = CreateJson(1, 20.0);

            // Act: initialize two instances with these properties
            var segmentA = PythonEngineManager.DataScheduleSegmentClass(jsonA);
            var segmentB = PythonEngineManager.DataScheduleSegmentClass(jsonB);

            // Assert: the two instances should not be equal
            Assert.That(segmentA != segmentB, Is.True, "Expected instances with different heights to be unequal.");
        }

        [Test]
        public void DifferentIndexSameHeight_ShouldReturnFalse()
        {
            // Arrange: create JSON for instances with different indexes but the same height
            var jsonA = CreateJson(1, 10.5);
            var jsonB = CreateJson(2, 10.5);

            // Act: initialize two instances with these properties
            var segmentA = PythonEngineManager.DataScheduleSegmentClass(jsonA);
            var segmentB = PythonEngineManager.DataScheduleSegmentClass(jsonB);

            Console.WriteLine(segmentA.to_json_ordered());
            Console.WriteLine(segmentB.to_json_ordered());

            // Assert: the two instances should not be equal
            Assert.That(segmentA != segmentB, Is.True, "Expected instances with different indexes to be unequal.");
        }

        [Test]
        public void EqualInstances_WithDefaultValues_ShouldReturnTrue()
        {
            // Arrange: create two instances with no JSON data (using default values)
            var segmentA = PythonEngineManager.DataScheduleSegmentClass();
            var segmentB = PythonEngineManager.DataScheduleSegmentClass();

            // Assert: the two instances should be equal (default values)
            Assert.That(segmentA == segmentB, Is.True, "Expected default instances to be equal.");
        }

    }
}
