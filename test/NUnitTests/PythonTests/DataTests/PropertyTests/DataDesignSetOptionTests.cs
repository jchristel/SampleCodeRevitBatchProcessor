using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Scripting.Hosting;
using IronPython.Runtime.Exceptions;
using PythonTests.Setup;

namespace PythonTests
{
    public class DataDesignSetOptionTests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.IsNotNull(PythonEngineManager.DataDesingSetOptionClass, "DataDesignSetOption should be loaded.");
        }

        [Test]
        public void Initialize_WithNoArguments_ShouldSetDefaultValues()
        {
            // Initialize without JSON data
            dynamic dataOption = PythonEngineManager.DataDesingSetOptionClass();

            Assert.AreEqual("-", dataOption.set_name);
            Assert.AreEqual("-", dataOption.option_name);
            Assert.IsTrue(dataOption.is_primary);
        }

        [Test]
        public void Initialize_WithValidJson_ShouldSetPropertiesFromJson()
        {
            // JSON input string
            string json = "{\"set_name\": \"Set1\", \"option_name\": \"OptionA\", \"is_primary\": false}";

            // Initialize with JSON data
            dynamic dataOption = PythonEngineManager.DataDesingSetOptionClass(json);

            Assert.AreEqual("Set1", dataOption.set_name);
            Assert.AreEqual("OptionA", dataOption.option_name);
            Assert.IsFalse(dataOption.is_primary);
        }

        [Test]
        public void DataTypeProperty_ShouldReturnCorrectDataType()
        {
            // Initialize without JSON data
            dynamic dataOption = PythonEngineManager.DataDesingSetOptionClass();

            Assert.AreEqual("design_set", dataOption.DataType);
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
