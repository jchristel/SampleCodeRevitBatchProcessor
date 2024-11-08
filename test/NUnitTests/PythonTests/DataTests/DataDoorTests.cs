using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;

namespace PythonTests.DataTests
{
    public class DataDoorTests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.IsNotNull(PythonEngineManager.DataDoorClass, "DataTypeProperties should be loaded.");
        }
    }
}
