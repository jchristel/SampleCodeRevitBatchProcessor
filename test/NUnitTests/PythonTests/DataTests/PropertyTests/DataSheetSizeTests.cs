using PythonTests.Setup;
using IronPython.Runtime.Exceptions;
namespace PythonTests.DataTests.PropertyTests
{
    public class DataSheetSizeTests
    {

        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.DataSheetSizeClass, Is.Not.Null, "DataSheetSize should be loaded.");
        }

        [Test]
        public void DataSheetSize_Initialize_ValidValues_ShouldSetProperties()
        {
            string name = "A4";
            double width = 210.0;
            double height = 297.0;

            dynamic dataSheetSize = PythonEngineManager.DataSheetSizeClass(name, width, height);

            Assert.That(name, Is.EqualTo(dataSheetSize.name), "Name property is not set correctly.");
            Assert.That(width, Is.EqualTo(dataSheetSize.width), "Width property is not set correctly.");
            Assert.That(height, Is.EqualTo(dataSheetSize.height), "Height property is not set correctly.");
        }

        [Test]
        public void DataSheetSize_Initialize_InvalidName_ShouldThrowException()
        {
            double width = 210.0;
            double height = 297.0;

            Assert.Throws<ValueErrorException>(() =>
            {
                PythonEngineManager.DataSheetSizeClass(123, width, height); // Invalid name
            });
        }

        [Test]
        public void DataSheetSize_Initialize_InvalidWidth_ShouldThrowException()
        {
            string name = "A4";
            double height = 297.0;

            Assert.Throws<ValueErrorException>(() =>
            {
                PythonEngineManager.DataSheetSizeClass(name, "invalid_width", height); // Invalid width
            });
        }

        [Test]
        public void DataSheetSize_Initialize_InvalidHeight_ShouldThrowException()
        {
            string name = "A4";
            double width = 210.0;

            Assert.Throws<ValueErrorException>(() =>
            {
                PythonEngineManager.DataSheetSizeClass(name, width, "invalid_height"); // Invalid height
            });
        }

        [Test]
        public void DataSheetSize_IsMatchingSize_WithinTolerance_ShouldReturnTrue()
        {
            string name = "A4";
            double width = 210.0;
            double height = 297.0;

            dynamic dataSheetSize = PythonEngineManager.DataSheetSizeClass(name, width, height);

            bool result = dataSheetSize.is_matching_size(215.0, 295.0); // Within 10mm tolerance
            Assert.That(result, Is.True, "is_matching_size failed for values within tolerance.");
        }

        [Test]
        public void DataSheetSize_IsMatchingSize_OutsideTolerance_ShouldReturnFalse()
        {
            string name = "A4";
            double width = 210.0;
            double height = 297.0;

            dynamic dataSheetSize = PythonEngineManager.DataSheetSizeClass(name, width, height);

            bool result = dataSheetSize.is_matching_size(230.0, 280.0); // Outside 10mm tolerance
            Assert.That(result, Is.False, "is_matching_size returned true for values outside tolerance.");
        }

        [Test]
        public void DataSheetSize_Equals_SameValues_ShouldReturnTrue()
        {
            string name = "A4";
            double width = 210.0;
            double height = 297.0;

            dynamic dataSheetSize1 = PythonEngineManager.DataSheetSizeClass(name, width, height);
            dynamic dataSheetSize2 = PythonEngineManager.DataSheetSizeClass(name, width, height);

            Assert.That(dataSheetSize1 == dataSheetSize2, Is.True, "Equality failed for same values.");
        }

        [Test]
        public void DataSheetSize_Equals_DifferentValues_ShouldReturnFalse()
        {
            dynamic dataSheetSize1 = PythonEngineManager.DataSheetSizeClass("A4", 210.0, 297.0);
            dynamic dataSheetSize2 = PythonEngineManager.DataSheetSizeClass("A3", 297.0, 420.0);

            Assert.That(dataSheetSize1 == dataSheetSize2, Is.False, "Equality returned true for different values.");
        }

        [Test]
        public void DataSheetSize_NotEquals_SameValues_ShouldReturnFalse()
        {
            dynamic dataSheetSize1 = PythonEngineManager.DataSheetSizeClass("A4", 210.0, 297.0);
            dynamic dataSheetSize2 = PythonEngineManager.DataSheetSizeClass("A4", 210.0, 297.0);

            Assert.That(dataSheetSize1 != dataSheetSize2, Is.False, "Inequality returned true for same values.");
        }

        [Test]
        public void DataSheetSize_NotEquals_DifferentValues_ShouldReturnTrue()
        {
            dynamic dataSheetSize1 = PythonEngineManager.DataSheetSizeClass("A4", 210.0, 297.0);
            dynamic dataSheetSize2 = PythonEngineManager.DataSheetSizeClass("A3", 297.0, 420.0);

            Assert.That(dataSheetSize1 != dataSheetSize2, Is.True, "Inequality returned false for different values.");
        }

        [Test]
        public void DataSheetSize_Initialize_WithJson_ShouldSetProperties()
        {
            string json = @"{""name"": ""A4"", ""width"": 210.0, ""height"": 297.0}";

            dynamic dataSheetSize = PythonEngineManager.DataSheetSizeClass(j: json);

            Assert.That("A4", Is.EqualTo(dataSheetSize.name), "Name from JSON is not set correctly.");
            Assert.That(210.0, Is.EqualTo(dataSheetSize.width), "Width from JSON is not set correctly.");
            Assert.That(297.0, Is.EqualTo(dataSheetSize.height), "Height from JSON is not set correctly.");
        }
    }
}
