using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;

namespace PythonTests.DataTests.PropertyTests
{
    public class DataPhasingTests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.IsNotNull(PythonEngineManager.DataPhasingClass, "DataPhasing should be loaded.");
        }

        [Test]
        public void DefaultInitialization_ShouldSetDefaultValues()
        {
            dynamic dataPhasing = PythonEngineManager.DataPhasingClass();
            // Verify default values are set
            Assert.AreEqual("-", dataPhasing.created, "Expected default created phase to be '-'.");
            Assert.AreEqual("-", dataPhasing.demolished, "Expected default demolished phase to be '-'.");
        }

        [Test]
        public void InitializeWithValidJson_ShouldSetProperties()
        {
            // Sample JSON input
            var jsonString = JsonConvert.SerializeObject(new { created = "2022-01-01", demolished = "2023-01-01" });
            var dataPhasingFromJson = PythonEngineManager.DataPhasingClass(jsonString);

            Assert.AreEqual("2022-01-01", dataPhasingFromJson.created, "Expected created phase to be '2022-01-01'.");
            Assert.AreEqual("2023-01-01", dataPhasingFromJson.demolished, "Expected demolished phase to be '2023-01-01'.");
        }

        [Test]
        public void InitializeWithInvalidType_ShouldRaiseTypeError()
        {
            // Non-dictionary or string input (e.g., integer)
            var invalidInput = 12345;

            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataPhasingClass(invalidInput));
            StringAssert.Contains("Argument j supplied must be of type string or type dictionary", ex.Message, "Expected TypeError for non-string, non-dict input.");
        }

        [Test]
        public void InitializeWithPartialJson_ShouldUseDefaultsForMissingProperties()
        {
            // JSON with only the 'created' property
            var jsonString = JsonConvert.SerializeObject(new { created = "2022-01-01" });
            var dataPhasingPartial = PythonEngineManager.DataPhasingClass(jsonString);

            Assert.AreEqual("2022-01-01", dataPhasingPartial.created, "Expected created phase to be '2022-01-01'.");
            Assert.AreEqual("-", dataPhasingPartial.demolished, "Expected demolished phase to remain the default value of '-'.");
        }

        [Test]
        public void EqualityComparison_SameProperties_ShouldReturnTrue()
        {
            var jsonString = JsonConvert.SerializeObject(new { created = "2022-01-01", demolished = "2023-01-01" });
            var dataPhasingA = PythonEngineManager.DataPhasingClass(jsonString);
            var dataPhasingB = PythonEngineManager.DataPhasingClass(jsonString);

            Assert.IsTrue(dataPhasingA == dataPhasingB, "Expected identical properties to result in equality.");
        }

        [Test]
        public void InequalityComparison_DifferentProperties_ShouldReturnTrue()
        {
            var jsonStringA = JsonConvert.SerializeObject(new { created = "2022-01-01", demolished = "2023-01-01" });
            var jsonStringB = JsonConvert.SerializeObject(new { created = "2021-01-01", demolished = "2022-01-01" });

            var dataPhasingA = PythonEngineManager.DataPhasingClass(jsonStringA);
            var dataPhasingB = PythonEngineManager.DataPhasingClass(jsonStringB);

            Assert.IsTrue(dataPhasingA != dataPhasingB, "Expected different properties to result in inequality.");
        }

        [Test]
        public void EqualityComparison_DifferentType_ShouldThrowException()
        {
            var jsonString = JsonConvert.SerializeObject(new { created = "2022-01-01", demolished = "2023-01-01" });
            var dataPhasingA = PythonEngineManager.DataPhasingClass(jsonString);
            var otherObject = "Some String";

            var ex = Assert.Throws<ValueErrorException>(() => { var comp = dataPhasingA == otherObject; });
            StringAssert.Contains("other needs to be of type DataPhasing", ex.Message, "Expected ValueError for comparison with different type.");
        }
    }
}
