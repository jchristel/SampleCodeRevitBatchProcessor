using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;

namespace PythonTests.DataTests
{
    public class DaaLevelBuildingTests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.IsNotNull(PythonEngineManager.DataLevelBuildingClass, "DataTypeProperties should be loaded.");
        }
    }
}
