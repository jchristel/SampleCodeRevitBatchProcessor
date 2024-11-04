using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;


namespace PythonTests.DataTests.PropertyTests
{
    public class DataLevel
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.IsNotNull(PythonEngineManager.DataLevelClass, "DataLevel should be loaded.");
        }

        [Test]
        public void DefaultInitialization_ShouldSetDefaultValues()
        {
            dynamic dataLevel = PythonEngineManager.DataLevelClass();
            // Verify default values are set
            Assert.AreEqual("-", dataLevel.name, "Expected default name to be '-'.");
            Assert.AreEqual(-1, dataLevel.id, "Expected default id to be -1.");
            Assert.AreEqual(0.0, dataLevel.offset_from_level, "Expected default offset_from_level to be 0.0.");
        }

        [Test]
        public void InitializeWithValidJson_ShouldSetProperties()
        {
            // Sample JSON input
            var jsonString = JsonConvert.SerializeObject(new { name = "Level 1", id = 123, offset_from_level = 10.5 });
            var dataLevelFromJson = PythonEngineManager.DataLevelClass(jsonString);

            Assert.AreEqual("Level 1", dataLevelFromJson.name, "Expected name to be 'Level 1'.");
            Assert.AreEqual(123, dataLevelFromJson.id, "Expected id to be 123.");
            Assert.AreEqual(10.5, dataLevelFromJson.offset_from_level, "Expected offset_from_level to be 10.5.");
        }

        [Test]
        public void InitializeWithInvalidJson_ShouldRaiseTypeError()
        {
            var invalidJsonString = JsonConvert.SerializeObject(new { name = 12345, id = "Level A", offset_from_level = "Offset" });

            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataLevelClass(invalidJsonString));
            StringAssert.Contains("Node level failed to initialise with: Expected 'name' to be a string,", ex.Message, "Expected TypeError for invalid offset_from_level type.");
        }

        [Test]
        public void InitializeWithInvalidType_ShouldRaiseTypeError()
        {
            // Non-dictionary or string input (e.g., integer)
            var invalidInput = 12345;

            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataLevelClass(invalidInput));
            StringAssert.Contains("Argument j supplied must be of type string or type dictionary", ex.Message, "Expected TypeError for non-string, non-dict input.");
        }

        [Test]
        public void InitializeWithPartialJson_ShouldUseDefaultsForMissingProperties()
        {
            // JSON with only the 'name' and 'id' properties
            var jsonString = JsonConvert.SerializeObject(new { name = "Partial Level", id = 50 });
            var dataLevelPartial = PythonEngineManager.DataLevelClass(jsonString);

            Assert.AreEqual("Partial Level", dataLevelPartial.name, "Expected name to be 'Partial Level'.");
            Assert.AreEqual(50, dataLevelPartial.id, "Expected id to be 50.");
            Assert.AreEqual(0.0, dataLevelPartial.offset_from_level, "Expected offset_from_level to remain the default value of 0.0.");
        }

        [Test]
        public void EqualityComparison_SameProperties_ShouldReturnTrue()
        {
            var jsonString = JsonConvert.SerializeObject(new { name = "Level 1", id = 100, offset_from_level = 15.0 });
            var dataLevelA = PythonEngineManager.DataLevelClass(jsonString);
            var dataLevelB = PythonEngineManager.DataLevelClass(jsonString);

            Assert.IsTrue(dataLevelA == dataLevelB, "Expected identical properties to result in equality.");
        }

        [Test]
        public void InequalityComparison_DifferentProperties_ShouldReturnTrue()
        {
            var jsonStringA = JsonConvert.SerializeObject(new { name = "Level 1", id = 100, offset_from_level = 15.0 });
            var jsonStringB = JsonConvert.SerializeObject(new { name = "Level 2", id = 200, offset_from_level = 20.0 });

            var dataLevelA = PythonEngineManager.DataLevelClass(jsonStringA);
            var dataLevelB = PythonEngineManager.DataLevelClass(jsonStringB);

            Assert.IsTrue(dataLevelA != dataLevelB, "Expected different properties to result in inequality.");
        }
    }
}
