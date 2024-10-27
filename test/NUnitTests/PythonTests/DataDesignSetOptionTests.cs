using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Scripting.Hosting;
using IronPython.Runtime.Exceptions;

namespace PythonTests
{
    public class DataDesignSetOptionTests
    {
        ScriptEngine _engine;
        ScriptScope _scope;

        private dynamic dataDesignSetOptionClass;

        [SetUp]
        public void Setup()
        {
            // get a python engine
            ScriptEngine engine = PythonRunner.SetupEngine();
            _scope = engine.CreateScope();

            // get the repository path
            string repoPath = PythonRunner.GetRepositoryPath();

            // set path to bounding box 2 class
            var pythonFilePath_dataDesignSetOption = Path.Combine(repoPath, @"duHast\Data\Objects\Properties\data_design_set_option.py");
           
            //run the file
            engine.ExecuteFile(pythonFilePath_dataDesignSetOption, _scope);

            dataDesignSetOptionClass = _scope.GetVariable("DataDesignSetOption");
           
            //store the engine instance
            _engine = engine;
        }

        [Test]
        public void Initialize_WithNoArguments_ShouldSetDefaultValues()
        {
            // Initialize without JSON data
            dynamic dataOption = dataDesignSetOptionClass();

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
            dynamic dataOption = dataDesignSetOptionClass(json);

            Assert.AreEqual("Set1", dataOption.set_name);
            Assert.AreEqual("OptionA", dataOption.option_name);
            Assert.IsFalse(dataOption.is_primary);
        }

        [Test]
        public void DataTypeProperty_ShouldReturnCorrectDataType()
        {
            // Initialize without JSON data
            dynamic dataOption = dataDesignSetOptionClass();

            Assert.AreEqual("design_set", dataOption.DataType);
        }

        [Test]
        public void Initialize_WithInvalidJsonType_ShouldThrowTypeError()
        {
            var ex = Assert.Throws<TypeErrorException>(() => dataDesignSetOptionClass(12345));
            Assert.That(ex.Message, Does.Contain("Argument j supplied must be of type string or type dictionary"));
        }

        [Test]
        public void Initialize_WithInvalidJsonString_ShouldThrowValueError()
        {
            string invalidJson = "{\"set_name\": \"Set1\", \"option_name\": \"OptionA\", \"is_primary\": \"invalid_bool\"}";

            var ex = Assert.Throws<ValueErrorException>(() => dataDesignSetOptionClass(invalidJson));
            Assert.That(ex.Message, Does.Contain("failed to initialise"));
        }
    }
}
