using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;

namespace PythonTests.DataTests
{
    public class DataLevelBuildingTests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.DataLevelBuildingClass, Is.Not.Null, "DataTypeProperties should be loaded.");
        }

        // Helper method to create a JSON string for DataLevelBuilding initialization
        private string CreateJson(object elevation = null, Dictionary<string, object> revitModelProps = null)
        {
            return JsonConvert.SerializeObject(new
            {
                elevation = elevation,
                revit_model = revitModelProps
            });
        }

        [Test]
        public void InitializeWithValidJson_ShouldSetAllProperties()
        {
            // Arrange: valid JSON with elevation and revit_model data
            var jsonString = CreateJson(
                12.5,
                new Dictionary<string, object> { { "name", "ModelA" } }
            );

            // Act: initialize the instance
            var levelBuilding = PythonEngineManager.DataLevelBuildingClass(jsonString);

            // Assert: verify each property is correctly set
            Assert.That(12.5, Is.EqualTo(levelBuilding.elevation), "Expected elevation to be '12.5'.");
            Assert.That("ModelA", Is.EqualTo(levelBuilding.revit_model.name), "Expected revit model name to be 'ModelA'.");
        }

        [Test]
        public void InitializeWithEmptyJson_ShouldUseDefaultValues()
        {
            // Arrange: empty JSON string
            var jsonString = JsonConvert.SerializeObject(new { });

            // Act: initialize the instance with empty JSON
            var levelBuilding = PythonEngineManager.DataLevelBuildingClass(jsonString);

            // Assert: verify default values are applied
            Assert.That(0.0,Is.EqualTo(levelBuilding.elevation), "Expected default elevation to be '0.0'.");
            Assert.That("-", Is.EqualTo(levelBuilding.revit_model.name), "Expected default revit model name to be '-'.");
        }

        [Test]
        public void EqualInstances_ShouldReturnTrue()
        {
            // Arrange: identical JSON data for two instances
            var jsonString = CreateJson(
                12.5,
                new Dictionary<string, object> { { "name", "ModelA" }, { "id", 123 } }
            );
            var levelBuildingA = PythonEngineManager.DataLevelBuildingClass(jsonString);
            var levelBuildingB = PythonEngineManager.DataLevelBuildingClass(jsonString);

            // Act & Assert: verify equality between identical instances
            Assert.That(levelBuildingA == levelBuildingB, Is.True, "Expected two instances with identical data to be equal.");
            Assert.That(levelBuildingA != levelBuildingB, Is.False, "Expected two instances with identical data not to be unequal.");
        }

        [Test]
        public void DifferentElevation_ShouldReturnFalseForEquality()
        {
            // Arrange: two instances with different elevation values
            var jsonStringA = CreateJson(12.5);
            var jsonStringB = CreateJson(15.0);
            var levelBuildingA = PythonEngineManager.DataLevelBuildingClass(jsonStringA);
            var levelBuildingB = PythonEngineManager.DataLevelBuildingClass(jsonStringB);

            // Act & Assert: verify inequality due to different elevations
            Assert.That(levelBuildingA == levelBuildingB, Is.False, "Expected instances with different elevations to not be equal.");
            Assert.That(levelBuildingA != levelBuildingB, Is.True, "Expected instances with different elevations to be unequal.");
        }

        [Test]
        public void DifferentRevitModel_ShouldReturnFalseForEquality()
        {
            // Arrange: two instances with different RevitModel properties
            var jsonStringA = CreateJson(12.5, new Dictionary<string, object> { { "name", "ModelA" }, { "id", 123 } });
            var jsonStringB = CreateJson(12.5, new Dictionary<string, object> { { "name", "ModelB" }, { "id", 456 } });
            var levelBuildingA = PythonEngineManager.DataLevelBuildingClass(jsonStringA);
            var levelBuildingB = PythonEngineManager.DataLevelBuildingClass(jsonStringB);

            // Act & Assert: verify inequality due to different RevitModel data
            Assert.That(levelBuildingA == levelBuildingB, Is.False, "Expected instances with different revit model properties to not be equal.");
            Assert.That(levelBuildingA != levelBuildingB, Is.True, "Expected instances with different revit model properties to be unequal.");
        }

        [Test]
        public void DefaultValues_ShouldBeEqual()
        {
            // Arrange: two instances initialized with default values
            var levelBuildingA = PythonEngineManager.DataLevelBuildingClass();
            var levelBuildingB = PythonEngineManager.DataLevelBuildingClass();

            // Act & Assert: verify equality with default values
            Assert.That(levelBuildingA == levelBuildingB, Is.True, "Expected two instances with default values to be equal.");
            Assert.That(levelBuildingA != levelBuildingB, Is.False, "Expected two instances with default values not to be unequal.");
        }

        [Test]
        public void InitializeWithInvalidElevationType_ShouldThrowTypeError()
        {
            // Arrange: valid JSON with elevation and revit_model data
            var jsonString = CreateJson(
                "invalid elevation",
                new Dictionary<string, object> { { "name", "ModelA" } }
            );


            //var levelBuildingB = PythonEngineManager.DataLevelBuildingClass(jsonString);
            //Console.WriteLine(jsonString);

            // Act & Assert: initialization should throw a TypeError
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataLevelBuildingClass(jsonString));
            Assert.That(ex.Message,Does.Contain( "Node level failed to initialise with: Expected 'elevation' to be a float"), "Expected TypeError for non float input.");
        }
    }
}
