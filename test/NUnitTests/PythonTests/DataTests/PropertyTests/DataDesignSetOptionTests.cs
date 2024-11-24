using IronPython.Runtime.Exceptions;
using PythonTests.Setup;

namespace PythonTests.DataTests.PropertyTests
{
    public class DataDesignSetOptionTests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.DataDesingSetOptionClass, Is.Not.Null, "DataDesignSetOption should be loaded.");
        }

        [Test]
        public void Initialize_WithNoArguments_ShouldSetDefaultValues()
        {
            // Initialize without JSON data
            dynamic dataOption = PythonEngineManager.DataDesingSetOptionClass();

            Assert.That("-", Is.EqualTo(dataOption.set_name));
            Assert.That("-", Is.EqualTo(dataOption.option_name));
            Assert.That(dataOption.is_primary, Is.True);
        }

        [Test]
        public void Initialize_WithValidJson_ShouldSetPropertiesFromJson()
        {
            // JSON input string
            string json = "{\"set_name\": \"Set1\", \"option_name\": \"OptionA\", \"is_primary\": false}";

            // Initialize with JSON data
            dynamic dataOption = PythonEngineManager.DataDesingSetOptionClass(json);

            Assert.That("Set1", Is.EqualTo(dataOption.set_name));
            Assert.That("OptionA", Is.EqualTo(dataOption.option_name));
            Assert.That(dataOption.is_primary, Is.False);
        }

        [Test]
        public void DataTypeProperty_ShouldReturnCorrectDataType()
        {
            // Initialize without JSON data
            dynamic dataOption = PythonEngineManager.DataDesingSetOptionClass();

            Assert.That("design_set_and_option", Is.EqualTo(dataOption.DataType));
        }

        [Test]
        public void Initialize_WithInvalidJsonType_ShouldThrowTypeError()
        {
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataDesingSetOptionClass(12345));
            Assert.That(ex.Message, Does.Contain("Argument j supplied must be of type string or type dictionary"));
        }

        [Test]
        public void Initialize_WithInvalidJsonString_ShouldThrowValueError()
        {
            string invalidJson = "{\"set_name\": \"Set1\", \"option_name\": \"OptionA\", \"is_primary\": \"invalid_bool\"}";

            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataDesingSetOptionClass(invalidJson));
            Assert.That(ex.Message, Does.Contain("Expected 'is_primary' to be a boolean"));
        }
    }
}
