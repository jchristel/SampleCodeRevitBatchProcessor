using PythonTests.Setup;
using IronPython.Runtime.Exceptions;

namespace PythonTests.DataTests.PropertyTests
{
    public class DataSheetSizeNamesTests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.DataSheetSizeNamesClass, Is.Not.Null, "DataSheetSizeNames should be loaded.");
        }
        [Test]
        public void DataSheetSizeNames_A3_ShouldHaveCorrectAttributes()
        {
            dynamic dataSheetSizeNames = PythonEngineManager.DataSheetSizeNamesClass();
            dynamic a3 = dataSheetSizeNames.A3;

            Assert.That("A3", Is.EqualTo(a3.name), "A3 name is incorrect.");
            Assert.That(420.0, Is.EqualTo(a3.width), "A3 width is incorrect.");
            Assert.That(297.0, Is.EqualTo(a3.height), "A3 height is incorrect.");
        }

        [Test]
        public void DataSheetSizeNames_A2_ShouldHaveCorrectAttributes()
        {
            dynamic dataSheetSizeNames = PythonEngineManager.DataSheetSizeNamesClass();
            dynamic a2 = dataSheetSizeNames.A2;

            Assert.That("A2", Is.EqualTo(a2.name), "A2 name is incorrect.");
            Assert.That(594.0, Is.EqualTo(a2.width), "A2 width is incorrect.");
            Assert.That(420.0, Is.EqualTo(a2.height), "A2 height is incorrect.");
        }

        [Test]
        public void DataSheetSizeNames_A1_ShouldHaveCorrectAttributes()
        {
            dynamic dataSheetSizeNames = PythonEngineManager.DataSheetSizeNamesClass();
            dynamic a1 = dataSheetSizeNames.A1;

            Assert.That("A1", Is.EqualTo(a1.name), "A1 name is incorrect.");
            Assert.That(841.0, Is.EqualTo(a1.width), "A1 width is incorrect.");
            Assert.That(594.0, Is.EqualTo(a1.height), "A1 height is incorrect.");
        }

        [Test]
        public void DataSheetSizeNames_A0_ShouldHaveCorrectAttributes()
        {
            dynamic dataSheetSizeNames = PythonEngineManager.DataSheetSizeNamesClass();
            dynamic a0 = dataSheetSizeNames.A0;

            Assert.That("A0", Is.EqualTo(a0.name), "A0 name is incorrect.");
            Assert.That(1189.0, Is.EqualTo(a0.width), "A0 width is incorrect.");
            Assert.That(841.0, Is.EqualTo(a0.height), "A0 height is incorrect.");
        }

        [Test]
        public void DataSheetSizeNames_GetAllSupportedSizes_ShouldReturnCorrectList()
        {
            dynamic dataSheetSizeNames = PythonEngineManager.DataSheetSizeNamesClass();
            dynamic supportedSizes = dataSheetSizeNames.get_all_supported_sizes();

            Assert.That(4, Is.EqualTo(supportedSizes.Count), "Supported sizes count is incorrect.");

            Assert.That("A0", Is.EqualTo(supportedSizes[0].name), "First size in supported sizes is not A0.");
            Assert.That("A1", Is.EqualTo(supportedSizes[1].name), "Second size in supported sizes is not A1.");
            Assert.That("A2", Is.EqualTo(supportedSizes[2].name), "Third size in supported sizes is not A2.");
            Assert.That("A3", Is.EqualTo(supportedSizes[3].name), "Fourth size in supported sizes is not A3.");
        }

        [Test]
        public void DataSheetSizeNames_GetAllSupportedSizes_ShouldMatchAttributes()
        {
            dynamic dataSheetSizeNames = PythonEngineManager.DataSheetSizeNamesClass();
            dynamic supportedSizes = dataSheetSizeNames.get_all_supported_sizes();

            var expectedSizes = new[]
            {
            new { Name = "A0", Width = 1189.0, Height = 841.0 },
            new { Name = "A1", Width = 841.0, Height = 594.0 },
            new { Name = "A2", Width = 594.0, Height = 420.0 },
            new { Name = "A3", Width = 420.0, Height = 297.0 }
        };

            for (int i = 0; i < expectedSizes.Length; i++)
            {
                Assert.That(expectedSizes[i].Name, Is.EqualTo(supportedSizes[i].name), $"Name of size {i} is incorrect.");
                Assert.That(expectedSizes[i].Width, Is.EqualTo(supportedSizes[i].width), $"Width of size {i} is incorrect.");
                Assert.That(expectedSizes[i].Height, Is.EqualTo(supportedSizes[i].height), $"Height of size {i} is incorrect.");
            }
        }
    }
}
