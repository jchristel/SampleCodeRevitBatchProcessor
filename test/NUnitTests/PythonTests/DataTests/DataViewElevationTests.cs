using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;

namespace PythonTests.DataTests
{
    public class DataViewElevationTests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.IsNotNull(PythonEngineManager.DataViewElevationClass, "DataTypeProperties should be loaded.");
        }
    }
}
