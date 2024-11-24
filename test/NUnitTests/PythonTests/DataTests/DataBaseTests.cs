using IronPython.Runtime.Exceptions;
using PythonTests.Setup;

namespace PythonTests.DataTests
{
    public class DataBaseTests
    {

        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.DataBaseClass, Is.Not.Null, "DataTypeProperties should be loaded."); // Change IsNotNull to NotNull
        }


        [Test]
        public void Constructor_WithValidDataType_ShouldSetDataTypeCorrectly()
        {
            // Arrange
            string dataType = "example_type";

            // Act
            dynamic instance = PythonEngineManager.DataBaseClass(dataType);

            // Assert
            Assert.That(dataType,Is.EqualTo( instance.DataType));
        }

        [Test]
        public void DataType_Property_ShouldReturnCorrectDataType()
        {
            // Arrange
            string dataType = "test_type";
            dynamic instance = PythonEngineManager.DataBaseClass(dataType);

            // Act
            string result = instance.DataType;

            // Assert
            Assert.That(result, Is.EqualTo("test_type"));
        }

        [Test]
        public void Constructor_WithEmptyStringDataType_ShouldSetDataTypeCorrectly()
        {
            // Arrange
            string dataType = "";

            // Act
            dynamic instance = PythonEngineManager.DataBaseClass(dataType);

            // Assert
            Assert.That(dataType, Is.EqualTo(instance.DataType));
        }

        [Test]
        public void Constructor_WithNullDataType_ShouldThrowTypeError()
        {
            // Act & Assert
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.DataBaseClass(null));
            Assert.That(ex.Message, Does.Contain("data_type must be a string, got"));
        }
    }
}
