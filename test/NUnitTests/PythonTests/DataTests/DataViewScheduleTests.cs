using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;

namespace PythonTests.DataTests
{
    public class DataViewScheduleTests
    {
        private string validJsonString;
        private Dictionary<string, object> validJsonDictionary;

        [SetUp]
        public void SetUp()
        {
            // Sample valid JSON for testing
            validJsonDictionary = new Dictionary<string, object>
            {
                { "data_type", "view_schedule" },
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
                { "total_number_of_rows", 10 },
                { "segments", new List<Dictionary<string, object>>
                    {
                         new Dictionary<string, object>
                        {
                            { "index", 0 },
                            { "height", 12.0 },
                        },
                        new Dictionary<string, object>
                        {
                            { "index", 1 },
                            { "height", 13.0 },
                        }
                    }
                }
            };

                validJsonString = JsonConvert.SerializeObject(validJsonDictionary);
        }

        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.DataViewScheduleClass, Is.Not.Null, "DataTypeProperties should be loaded.");
        }

        // Helper method to create JSON strings
        private static string CreateJson(Dictionary<string, object> properties)
        {
            return Newtonsoft.Json.JsonConvert.SerializeObject(properties);
        }

        [Test]
        public void DataViewSchedule_Constructor_ValidJson_ShouldInitializeCorrectly()
        {

            // Act
            var dataViewSchedule = PythonEngineManager.DataViewScheduleClass(validJsonString);

            // Assert
            Assert.That("view_schedule", Is.EqualTo(dataViewSchedule.data_type));
            Assert.That(101, Is.EqualTo(dataViewSchedule.id));
            Assert.That(dataViewSchedule.bounding_box, Is.Not.Null);
            Assert.That(0.0, Is.EqualTo(dataViewSchedule.bounding_box.min_x));
            Assert.That(10.0, Is.EqualTo(dataViewSchedule.bounding_box.max_x));
            Assert.That(0.0, Is.EqualTo(dataViewSchedule.bounding_box.min_y));
            Assert.That(10.0, Is.EqualTo(dataViewSchedule.bounding_box.max_y)   );
            Assert.That(10, Is.EqualTo(dataViewSchedule.total_number_of_rows));
            Assert.That(dataViewSchedule.segments, Is.Not.Null);
            Assert.That(2, Is.EqualTo(dataViewSchedule.segments.Count));
            Assert.That(0, Is.EqualTo(dataViewSchedule.segments[0].index));
            Assert.That(12, Is.EqualTo(dataViewSchedule.segments[0].height));
            Assert.That(1, Is.EqualTo(dataViewSchedule.segments[1].index));
            Assert.That(13, Is.EqualTo(dataViewSchedule.segments[1].height));
        }

        [Test]
        public void DataViewSchedule_Constructor_EmptyJson_ShouldInitializeWithDefaults()
        {
            // Act
            var dataViewSchedule = PythonEngineManager.DataViewScheduleClass();

            // Assert
            Assert.That("view_schedule", Is.EqualTo(dataViewSchedule.data_type));
            Assert.That(0, Is.EqualTo(dataViewSchedule.total_number_of_rows));
            Assert.That(dataViewSchedule.bounding_box, Is.Not.Null);
            Assert.That(0.0, Is.EqualTo(dataViewSchedule.bounding_box.min_x));
            Assert.That(0.0, Is.EqualTo(dataViewSchedule.bounding_box.max_x));
            Assert.That(0.0, Is.EqualTo(dataViewSchedule.bounding_box.min_y));
            Assert.That(0.0, Is.EqualTo(dataViewSchedule.bounding_box.max_y));
            Assert.That(dataViewSchedule.segments, Is.Not.Null);
            Assert.That(0, Is.EqualTo(dataViewSchedule.segments.Count));
        }

        [Test]
        public void DataViewSchedule_Constructor_InvalidJson_ShouldThrowException()
        {
            // Arrange
            var invalidJsonString = "Invalid JSON String";

            // Act & Assert
            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.DataViewScheduleClass(invalidJsonString));
            Assert.That(ex.Message, Does.Contain("Expecting value: line 1 "));
        }

        [Test]
        public void DataViewSchedule_Constructor_InvalidTotalNumberOfRows_ShouldThrowException()
        {
            // Arrange
            var invalidJson = CreateJson(new Dictionary<string, object>
            {
                { "data_type", "view_schedule" },
                { "total_number_of_rows", "invalid_value" }  // Invalid type
            });

            // Act & Assert
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataViewScheduleClass(invalidJson));
            Assert.That(ex.Message, Does.Contain("Expected 'total_number_of_rows' to be an int"));
        }

        [Test]
        public void DataViewSchedule_Equals_ValidComparison_ShouldReturnTrue()
        {
            // Arrange
            var dataViewSchedule1 = PythonEngineManager.DataViewScheduleClass(validJsonString);
            var dataViewSchedule2 = PythonEngineManager.DataViewScheduleClass(validJsonString);

            // Act
            var areEqual = dataViewSchedule1==dataViewSchedule2;

            // Assert
            Assert.That(areEqual, Is.True);
        }

        [Test]
        public void DataViewSchedule_Equals_InvalidComparison_ShouldReturnFalse()
        {
            // Arrange
            var dataViewSchedule1 = PythonEngineManager.DataViewScheduleClass(validJsonString);
            var dataViewSchedule2 = PythonEngineManager.DataViewScheduleClass(); // Empty object

            // Act
            var areEqual = dataViewSchedule1.Equals(dataViewSchedule2);

            // Assert
            Assert.That(areEqual, Is.False);
        }

        [Test]
        public void DataViewSchedule_Equals_NonDataViewSchedule_ShouldReturnNotImplemented()
        {
            // Arrange
            var dataViewSchedule = PythonEngineManager.DataViewScheduleClass(validJsonString);
            var nonDataViewSchedule = new object();

            // Act
            var areEqual = dataViewSchedule == nonDataViewSchedule;

            // Assert
            Assert.That(areEqual,Is.False);
        }

        [Test]
        public void DataViewSchedule_Nequality_Comparison_ShouldReturnTrueForNonEqualObjects()
        {
            // Arrange
            var dataViewSchedule1 = PythonEngineManager.DataViewScheduleClass(validJsonString);
            var dataViewSchedule2 = PythonEngineManager.DataViewScheduleClass(); // Empty object

            // Act
            var areNotEqual = dataViewSchedule1 != dataViewSchedule2;

            // Assert
            Assert.That(areNotEqual, Is.True);
        }

        [Test]
        public void DataViewSchedule_Constructor_InvalidJsonType_ShouldThrowException()
        {
            // Arrange
            //var invalidJson = CreateJson("test");

            // Act & Assert
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataViewScheduleClass(123));
            Assert.That(ex.Message, Does.Contain("Argument j supplied must be of type string or type dictionary"));
        }
    }
}
