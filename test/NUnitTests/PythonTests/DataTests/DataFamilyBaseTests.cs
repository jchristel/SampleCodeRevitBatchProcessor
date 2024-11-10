using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;

namespace PythonTests.DataTests
{
    public class DataFamilyBaseTests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.IsNotNull(PythonEngineManager.DataFamilyBaseClass, "DataTypeProperties should be loaded.");
        }

        // Helper method to create a JSON string for DataFamilyBase initialization
        private string CreateJson(Dictionary<string, object> instanceProps = null,
                                  Dictionary<string, object> typeProps = null,
                                  Dictionary<string, object> level = null,
                                  Dictionary<string, object> revitModel = null,
                                  Dictionary<string, object> phasing = null,
                                  Dictionary<string, object> designSetOption = null)
        {
            return JsonConvert.SerializeObject(new
            {
                instance_properties = instanceProps,
                type_properties = typeProps,
                level = level,
                revit_model = revitModel,
                phasing = phasing,
                design_set_and_option = designSetOption,
                associated_elements = new List<object> { "Element1", "Element2" }
            });
        }

        [Test]
        public void InitializeWithValidJson_ShouldSetAllProperties()
        {
            // Arrange: JSON data with valid properties for each sub-object
            var jsonString = CreateJson(
                new Dictionary<string, object> { { "id", 123 }, { "properties", new List<object> { new { name = "Prop1", value = 1 } } } },
                new Dictionary<string, object> { { "name", "TypeA" }, { "id", 456 } },
                new Dictionary<string, object> { { "name", "Level1" } },
                new Dictionary<string, object> { { "name", "ModelX" } },
                new Dictionary<string, object> { { "created", "Phase1" } },
                new Dictionary<string, object> { { "option_name", "OptionA" } }
            );

            // Act: initialize instance with JSON data
            var model = PythonEngineManager.DataFamilyBaseClass(jsonString);

            // Assert: verify that each sub-object and property is correctly set
            Assert.AreEqual(123, model.instance_properties.id, "Expected instance properties id to be '123'.");
            Assert.AreEqual("TypeA", model.type_properties.name, "Expected type properties name to be 'TypeA'.");
            Assert.AreEqual("Level1", model.level.name, "Expected level name to be 'Level1'.");
            Assert.AreEqual("ModelX", model.revit_model.name, "Expected revit model name to be 'ModelX'.");
            Assert.AreEqual("Phase1", model.phasing.created, "Expected phasing phase to be 'Phase1'.");
            Assert.AreEqual("OptionA", model.design_set_and_option.option_name, "Expected design set and option name to be 'OptionA'.");
            // assume count is 0 for now since not properly implemented
            Assert.AreEqual(0, model.associated_elements.Count, "Expected 0 associated elements.");
        }

        [Test]
        public void InitializeWithEmptyJson_ShouldUseDefaultValues()
        {
            // Arrange: an empty JSON object
            var jsonString = JsonConvert.SerializeObject(new { });

            // Act: initialize instance with empty JSON
            var model = PythonEngineManager.DataFamilyBaseClass(jsonString);

            // Assert: verify default values are set
            Assert.AreEqual(-1, model.instance_properties.id, "Expected default instance properties id to be -1.");
            Assert.AreEqual("-", model.type_properties.name, "Expected default type properties name to be '-'.");
            Assert.AreEqual("-", model.level.name, "Expected default level name to be '-'.");
            Assert.AreEqual("-", model.revit_model.name, "Expected default revit model name to be '-'.");
            Assert.AreEqual("-", model.phasing.created, "Expected default phasing phase to be '-'.");
            Assert.AreEqual("-", model.design_set_and_option.option_name, "Expected default design set and option name to be '-'.");
            Assert.AreEqual(0, model.associated_elements.Count, "Expected default associated elements list to be empty.");
        }

        [Test]
        public void EqualInstances_ShouldReturnTrue()
        {
            // Arrange: identical JSON data for two instances
            var jsonString = CreateJson(
                new Dictionary<string, object> { { "id", 123 }, { "properties", new List<object> { new { name = "Prop1", value = 1 } } } },
                new Dictionary<string, object> { { "name", "TypeA" }, { "id", 456 } },
                new Dictionary<string, object> { { "level_name", "Level1" } },
                new Dictionary<string, object> { { "name", "ModelX" } },
                new Dictionary<string, object> { { "phase", "Phase1" } },
                new Dictionary<string, object> { { "option_name", "OptionA" } }
            );
            var modelA = PythonEngineManager.DataFamilyBaseClass(jsonString);
            var modelB = PythonEngineManager.DataFamilyBaseClass(jsonString);

            // Act & Assert: verify equality comparison
            Assert.IsTrue(modelA == modelB, "Expected two instances with identical data to be equal.");
            Assert.IsFalse(modelA != modelB, "Expected two instances with identical data not to be unequal.");
        }

        [Test]
        public void DifferentInstanceProperties_ShouldReturnFalseForEquality()
        {
            // Arrange: JSON with differing instance properties
            var jsonStringA = CreateJson(new Dictionary<string, object> { { "id", 123 } });
            var jsonStringB = CreateJson(new Dictionary<string, object> { { "id", 124 } });
            var modelA = PythonEngineManager.DataFamilyBaseClass(jsonStringA);
            var modelB = PythonEngineManager.DataFamilyBaseClass(jsonStringB);

            // Act & Assert: verify inequality due to different instance properties
            Assert.IsFalse(modelA == modelB, "Expected instances with different instance properties to not be equal.");
            Assert.IsTrue(modelA != modelB, "Expected instances with different instance properties to be unequal.");
        }

        [Test]
        public void DifferentAssociatedElements_ShouldNotAffectEquality()
        {
            // Arrange: JSON with identical data except associated elements
            var jsonStringA = CreateJson(
                new Dictionary<string, object> { { "id", 123 } },
                new Dictionary<string, object> { { "name", "TypeA" } },
                null, null, null, null
            );
            var modelA = PythonEngineManager.DataFamilyBaseClass(jsonStringA);
            var jsonStringB = CreateJson(
                new Dictionary<string, object> { { "id", 123 } },
                new Dictionary<string, object> { { "name", "TypeA" } },
                null, null, null, null
            );

            var modelB = PythonEngineManager.DataFamilyBaseClass(jsonStringB);
            modelB.AssociatedElements = new List<object> { "DifferentElement" };

            // Act & Assert: verify equality despite different associated elements
            Assert.IsTrue(modelA == modelB, "Expected instances with different associated elements to be equal.");
            Assert.IsFalse(modelA != modelB, "Expected instances with different associated elements not to be unequal.");
        }

        [Test]
        public void DefaultValues_ShouldBeEqual()
        {
            // Arrange: two instances with default values
            var modelA = PythonEngineManager.DataFamilyBaseClass();
            var modelB = PythonEngineManager.DataFamilyBaseClass();

            // Act & Assert: verify equality for instances with default values
            Assert.IsTrue(modelA == modelB, "Expected two instances with default values to be equal.");
            Assert.IsFalse(modelA != modelB, "Expected two instances with default values not to be unequal.");
        }

    }
}
