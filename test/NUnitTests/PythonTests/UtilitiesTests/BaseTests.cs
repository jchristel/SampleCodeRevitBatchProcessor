using IronPython.Runtime.Exceptions;
using PythonTests.Setup;

namespace PythonTests.UtilitiesTests
{
    public class BaseTests
    {
        private dynamic _baseInstance;
       

        [SetUp]
        public void SetUp()
        {
            _baseInstance = PythonEngineManager.BaseClass();
        }


        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.BaseClass, Is.Not.Null, "Base should be loaded.");
        }

        [Test]
        public void BaseClass_ToJson_ShouldReturnValidJson()
        {
            string json = _baseInstance.to_json();
            Assert.That(json, Is.Not.Null, "JSON output should not be null.");
            Assert.That(json.StartsWith("{") && json.EndsWith("}"), Is.True, "Output should be a JSON object.");
        }

        [Test]
        public void BaseClass_ToJsonUtf_ShouldHandleUtfEncoding()
        {
            string jsonUtf = _baseInstance.to_json_utf();
            Assert.That(jsonUtf, Is.Not.Null, "UTF-8 JSON output should not be null.");
            Assert.That(jsonUtf.StartsWith("{") && jsonUtf.EndsWith("}"), Is.True, "Output should be a JSON object.");
        }

        [Test]
        public void BaseClass_Equality_ShouldReturnTrueForSameTypeInstances()
        {
            var anotherBaseInstance = PythonEngineManager.BaseClass();
            Assert.That(_baseInstance == anotherBaseInstance, Is.True, "Instances of the same type should be equal.");
        }

        [Test]
        public void BaseClass_IsPrimitive_ShouldIdentifyPrimitivesCorrectly()
        {
            Assert.That(_baseInstance._is_primitive(123), Is.True, "Integer should be identified as a primitive.");
            Assert.That(_baseInstance._is_primitive("test"), Is.True, "String should be identified as a primitive.");
        }

        [Test]
        public void BaseClass_Hash_ShouldBeConsistent()
        {
            int hash1 = _baseInstance.GetHashCode();
            int hash2 = _baseInstance.GetHashCode();
            Assert.That(hash1,Is.EqualTo( hash2), "Hash code should be consistent across calls.");
        }
    }
}
