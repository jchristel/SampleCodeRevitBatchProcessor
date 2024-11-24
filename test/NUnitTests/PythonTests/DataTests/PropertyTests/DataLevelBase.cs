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
            Assert.That(PythonEngineManager.DataLevelBaseClass, Is.Not.Null, "DataLevelBase should be loaded.");
        }

        [Test]
        public void DefaultInitialization_ShouldSetDefaultValues()
        {
            dynamic dataLevel = PythonEngineManager.DataLevelBaseClass();

            // Check if default values are set correctly
            Assert.That("-", Is.EqualTo(dataLevel.name), "Expected default name to be '-'.");
            Assert.That(-1, Is.EqualTo(dataLevel.id), "Expected default id to be -1.");
        }

        [Test]
        public void InitializeWithValidJson_ShouldSetProperties()
        {
            // Sample JSON input
            var jsonString = JsonConvert.SerializeObject(new { name = "Level 1", id = 123 });
            var dataLevelFromJson = PythonEngineManager.DataLevelBaseClass(jsonString);

            Assert.That("Level 1", Is.EqualTo(dataLevelFromJson.name), "Expected name to be 'Level 1'.");
            Assert.That(123, Is.EqualTo(dataLevelFromJson.id), "Expected id to be 123.");
        }

        [Test]
        public void InitializeWithInvalidJson_ShouldRaiseTypeError()
        {
            var invalidJsonString = JsonConvert.SerializeObject(new { name = 12345, id = "Level A" });

            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataLevelBaseClass(invalidJsonString));
            Assert.That(ex.Message, Does.Contain("Expected 'name' to be a string"), "Expected TypeError for invalid name type.");
        }

        [Test]
        public void InitializeWithInvalidType_ShouldRaiseTypeError()
        {
            // Non-dictionary or string input (e.g., integer)
            var invalidInput = 12345;

            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataLevelBaseClass(invalidInput));
            Assert.That(ex.Message, Does.Contain("Argument j supplied must be of type string or type dictionary"), "Expected TypeError for non-string, non-dict input.");
        }

        [Test]
        public void InitializeWithPartialJson_ShouldUseDefaultsForMissingProperties()
        {
            // JSON with only the 'name' property
            var jsonString = JsonConvert.SerializeObject(new { name = "Partial Level" });
            var dataLevelPartial = PythonEngineManager.DataLevelBaseClass(jsonString);

            Assert.That("Partial Level", Is.EqualTo(dataLevelPartial.name), "Expected name to be 'Partial Level'.");
            Assert.That(-1, Is.EqualTo(dataLevelPartial.id), "Expected id to remain the default value of -1.");
        }

        [Test]
        public void EqualityComparison_SameProperties_ShouldReturnTrue()
        {
            var jsonString = JsonConvert.SerializeObject(new { name = "Level 1", id = 100 });
            var dataLevelA = PythonEngineManager.DataLevelBaseClass(jsonString);
            var dataLevelB = PythonEngineManager.DataLevelBaseClass(jsonString);

            Assert.That(dataLevelA == dataLevelB, Is.True, "Expected identical properties to result in equality.");
        }

        [Test]
        public void InequalityComparison_DifferentProperties_ShouldReturnTrue()
        {
            var jsonStringA = JsonConvert.SerializeObject(new { name = "Level 1", id = 100 });
            var jsonStringB = JsonConvert.SerializeObject(new { name = "Level 2", id = 200 });

            var dataLevelA = PythonEngineManager.DataLevelBaseClass(jsonStringA);
            var dataLevelB = PythonEngineManager.DataLevelBaseClass(jsonStringB);

            Assert.That(dataLevelA != dataLevelB, Is.True, "Expected different properties to result in inequality.");
        }
    }
}
