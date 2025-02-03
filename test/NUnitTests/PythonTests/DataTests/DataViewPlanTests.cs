using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;

namespace PythonTests.DataTests
{
    public class DataViewPlanTests
    {
        private string validJsonString;
        private Dictionary<string, object> validJsonDictionary;

        [SetUp]
        public void SetUp()
        {
            // Sample valid JSON for testing DataSheetViewPort
            validJsonDictionary = new Dictionary<string, object>
            {
                { "data_type", "view_plan" },
                { "id", 101 },
                { "bounding_box", new Dictionary<string, object>
                    {
                        { "DataType", "bounding box 2" },
                        { "min_x", 0.0 },
                        { "max_x", 10.0 },
                        { "min_y", 0.0 },
                        { "max_y", 10.0 },
                           
                        { "rotation_coord", new Dictionary<string, object>
                            {
                                { "data", new List<List<double>> { new List<double> { 0.0, 0.0, 0.0 }, new List<double> { 0.0, 0.0, 0.0 }, new List<double> { 0.0, 0.0, 0.0 } } },
                                { "rows", 3 },
                                { "columns", 3 }
                            }
                        },
                        { "translation_coord", new Dictionary<string, object>
                            {
                                { "x", 0.0 },
                                { "y", 0.0 },
                                { "z", 0.0 },
                                { "json_ini", null }
                            }
                        }
                    }
                },
                { "tags", new List<Dictionary<string, object>>
                    {
                        new Dictionary<string, object>
                        {
                            { "data_type", "tag" },
                            { "bounding_box", new Dictionary<string, object>
                                {
                                    { "DataType", "bounding box 2" },
                                    { "min_x", 1.0 },
                                    { "max_x", 11.0 },
                                    { "min_y", 1.0 },
                                    { "max_y", 11.0 },
                                }
                            },

                            { "point", new Dictionary<string, object> { { "x", 5.0 }, { "y", 5.0 }, { "z", 5.0 } } },
                            { "elbow_location", new Dictionary<string, object> { { "x", 1.0 }, { "y", 1.0 }, { "z", 1.0 } } },
                            { "leader_end", "end_point" },
                            { "leader_reference", "reference_point" },
                            { "leader_element_reference_id", 123 }
                        }
                    }
                }
            };


            validJsonString = JsonConvert.SerializeObject(validJsonDictionary);
        }

        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.DataViewPlanClass, Is.Not.Null, "DataTypeProperties should be loaded.");
        }

        // Helper method to create JSON strings
        private string CreateJson(Dictionary<string, object> properties)
        {
            return Newtonsoft.Json.JsonConvert.SerializeObject(properties);
        }

        [Test]
        public void DataViewPlan_Constructor_ValidJson_ShouldInitializeCorrectly()
        {

            // Act
            var dataViewPlan = PythonEngineManager.DataViewPlanClass(validJsonString);

            // Assert
            Assert.That("view_plan", Is.EqualTo(dataViewPlan.data_type));
            Assert.That(101, Is.EqualTo(dataViewPlan.id));
            Assert.That(dataViewPlan.bounding_box, Is.Not.Null);
            Assert.That(0.0, Is.EqualTo(dataViewPlan.bounding_box.min_x));
            Assert.That(10.0, Is.EqualTo(dataViewPlan.bounding_box.max_x));
            Assert.That(0.0, Is.EqualTo(dataViewPlan.bounding_box.min_y));
            Assert.That(10.0, Is.EqualTo(dataViewPlan.bounding_box.max_y));
            Assert.That(dataViewPlan.tags, Is.Not.Null);
            Assert.That(1, Is.EqualTo(dataViewPlan.tags.Count));
            Assert.That("tag", Is.EqualTo(dataViewPlan.tags[0].data_type));
        }

        [Test]
        public void DataViewPlan_Constructor_EmptyJson_ShouldInitializeWithDefaults()
        {
            // Act
            var dataViewPlan = PythonEngineManager.DataViewPlanClass();

            // Assert
            Assert.That("view_plan", Is.EqualTo(dataViewPlan.data_type));
            Assert.That(-1, Is.EqualTo(dataViewPlan.id));
            Assert.That(dataViewPlan.bounding_box, Is.Not.Null);
            Assert.That(0.0, Is.EqualTo(dataViewPlan.bounding_box.min_x));
            Assert.That(0.0, Is.EqualTo(dataViewPlan.bounding_box.max_x));
            Assert.That(0.0, Is.EqualTo(dataViewPlan.bounding_box.min_y));
            Assert.That(0.0, Is.EqualTo(dataViewPlan.bounding_box.max_y));
            Assert.That(dataViewPlan.tags, Is.Not.Null);
            Assert.That(0, Is.EqualTo(dataViewPlan.tags.Count));
        }

        [Test]
        public void DataViewPlan_Constructor_InvalidJson_ShouldThrowException()
        {
            // Arrange
            var invalidJsonString = "Invalid JSON String";

            // Act & Assert
            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.DataViewPlanClass(invalidJsonString));
            Assert.That(ex.Message, Does.Contain("Expecting value: line 1"));
        }

        [Test]
        public void DataViewPlan_Equals_ValidComparison_ShouldReturnTrue()
        {
            
            // Arrange
            var dataViewPlan1 = PythonEngineManager.DataViewPlanClass(validJsonString);
            var dataViewPlan2 = PythonEngineManager.DataViewPlanClass(validJsonString);


            Console.WriteLine(dataViewPlan1.to_json_ordered());
            Console.WriteLine(dataViewPlan2.to_json_ordered());
            // Act
            var areEqual = dataViewPlan1==dataViewPlan2;

            // Assert
            Assert.That(areEqual, Is.True);
        }

        [Test]
        public void DataViewPlan_Equals_InvalidComparison_ShouldReturnFalse()
        {
            
            // Arrange
            var dataViewPlan1 = PythonEngineManager.DataViewPlanClass(validJsonString);
            var dataViewPlan2 = PythonEngineManager.DataViewPlanClass(); // Empty object

            // Act
            var areEqual = dataViewPlan1==dataViewPlan2;

            // Assert
            Assert.That(areEqual, Is.False);
        }

        [Test]
        public void DataViewPlan_Equals_NonDataViewPlan_ShouldReturnNotImplemented()
        {
            // Arrange
            var dataViewPlan = PythonEngineManager.DataViewPlanClass(validJsonString);
            var nonDataViewPlan = new object();

            // Act
            var areEqual = dataViewPlan == nonDataViewPlan;

            // Assert
            Assert.That(areEqual, Is.False);
        }

        [Test]
        public void DataViewPlan_Nequality_Comparison_ShouldReturnTrueForNonEqualObjects()
        {
           

            // Arrange
            var dataViewPlan1 = PythonEngineManager.DataViewPlanClass(validJsonString);
            var dataViewPlan2 = PythonEngineManager.DataViewPlanClass(); // Empty object

            // Act
            var areNotEqual = dataViewPlan1 != dataViewPlan2;

            // Assert
            Assert.That(areNotEqual, Is.True);
        }

        [Test]
        public void DataViewPlan_Constructor_InvalidJsonType_ShouldThrowException()
        {
            // Arrange
            var invalidJson = new List<string> { "invalid", "json" };

            // Act & Assert
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataViewPlanClass(invalidJson));
            Assert.That(ex.Message, Does.Contain("Argument j supplied must be of type string or type dictionary"));
        }
    }
}
