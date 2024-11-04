using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;

namespace PythonTests.DataTests.PropertyTests
{
    public class DataLevelBase
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.IsNotNull(PythonEngineManager.DataLevelBaseClass, "DataLevelBase should be loaded.");
        }

        [Test]
        public void DefaultInitialization_ShouldSetDefaultValues()
        {
            dynamic dataLevel = PythonEngineManager.DataLevelBaseClass();

            // Check if default values are set correctly
            Assert.AreEqual("-", dataLevel.name, "Expected default name to be '-'.");
            Assert.AreEqual(-1, dataLevel.id, "Expected default id to be -1.");
        }

        [Test]
        public void InitializeWithValidJson_ShouldSetProperties()
        {
            // Sample JSON input
            var jsonString = JsonConvert.SerializeObject(new { name = "Level 1", id = 123 });
            var dataLevelFromJson = PythonEngineManager.DataLevelBaseClass(jsonString);

            Assert.AreEqual("Level 1", dataLevelFromJson.name, "Expected name to be 'Level 1'.");
            Assert.AreEqual(123, dataLevelFromJson.id, "Expected id to be 123.");
        }

        [Test]
        public void InitializeWithInvalidJson_ShouldRaiseTypeError()
        {
            var invalidJsonString = JsonConvert.SerializeObject(new { name = 12345, id = "Level A" });

            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataLevelBaseClass(invalidJsonString));
            StringAssert.Contains("Expected 'name' to be a string", ex.Message, "Expected TypeError for invalid name type.");
        }

        [Test]
        public void InitializeWithInvalidType_ShouldRaiseTypeError()
        {
            // Non-dictionary or string input (e.g., integer)
            var invalidInput = 12345;

            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataLevelBaseClass(invalidInput));
            StringAssert.Contains("Argument j supplied must be of type string or type dictionary", ex.Message, "Expected TypeError for non-string, non-dict input.");
        }

        [Test]
        public void InitializeWithPartialJson_ShouldUseDefaultsForMissingProperties()
        {
            // JSON with only the 'name' property
            var jsonString = JsonConvert.SerializeObject(new { name = "Partial Level" });
            var dataLevelPartial = PythonEngineManager.DataLevelBaseClass(jsonString);

            Assert.AreEqual("Partial Level", dataLevelPartial.name, "Expected name to be 'Partial Level'.");
            Assert.AreEqual(-1, dataLevelPartial.id, "Expected id to remain the default value of -1.");
        }

        [Test]
        public void EqualityComparison_SameProperties_ShouldReturnTrue()
        {
            var jsonString = JsonConvert.SerializeObject(new { name = "Level 1", id = 100 });
            var dataLevelA = PythonEngineManager.DataLevelBaseClass(jsonString);
            var dataLevelB = PythonEngineManager.DataLevelBaseClass(jsonString);

            Assert.IsTrue(dataLevelA == dataLevelB, "Expected identical properties to result in equality.");
        }

        [Test]
        public void InequalityComparison_DifferentProperties_ShouldReturnTrue()
        {
            var jsonStringA = JsonConvert.SerializeObject(new { name = "Level 1", id = 100 });
            var jsonStringB = JsonConvert.SerializeObject(new { name = "Level 2", id = 200 });

            var dataLevelA = PythonEngineManager.DataLevelBaseClass(jsonStringA);
            var dataLevelB = PythonEngineManager.DataLevelBaseClass(jsonStringB);

            Assert.IsTrue(dataLevelA != dataLevelB, "Expected different properties to result in inequality.");
        }
    }
}
