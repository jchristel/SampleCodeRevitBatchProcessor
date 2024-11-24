using IronPython.Runtime.Exceptions;
using PythonTests.Setup;

namespace PythonTests.UtilitiesTests
{
    public class FileBOMTests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.BOMValueClass,Is.Not.Null, "FileEncodingBOM should be loaded.");
        }

        [Test]
        public void UTF8Value_IsCorrect()
        {
            dynamic bomValue = PythonEngineManager.BOMValueClass();
            byte[] expected = new byte[] { 0xef, 0xbb, 0xbf };
            Assert.That(bomValue.UTF_8, Is.EqualTo(expected));
        }

        [Test]
        public void UTF16Value_IsCorrect()
        {
            dynamic bomValue = PythonEngineManager.BOMValueClass();
            byte[] expected = new byte[] { 0xfe, 0xff };
            Assert.That(bomValue.UTF_16, Is.EqualTo(expected));
        }

        [Test]
        public void UTF16LittleEndianValue_IsCorrect()
        {
            dynamic bomValue = PythonEngineManager.BOMValueClass();
            byte[] expected = new byte[] { 0xff, 0xfe };
            Assert.That(bomValue.UTF_16_LITTLE_ENDIAN, Is.EqualTo(expected));
        }

        [Test]
        public void UTF16BigEndianValue_IsCorrect()
        {
            dynamic bomValue = PythonEngineManager.BOMValueClass();
            byte[] expected = new byte[] { 0xfe, 0xff };
            Assert.That(bomValue.UTF_16_BIG_ENDIAN, Is.EqualTo(expected));
        }

        [Test]
        public void UTF32Value_IsCorrect()
        {
            dynamic bomValue = PythonEngineManager.BOMValueClass();
            byte[] expected = new byte[] { 0x00, 0x00, 0xfe, 0xff };
            Assert.That(bomValue.UTF_32, Is.EqualTo(expected));
        }

        [Test]
        public void UTF32LittleEndianValue_IsCorrect()
        {
            dynamic bomValue = PythonEngineManager.BOMValueClass();
            byte[] expected = new byte[] { 0xff, 0xfe, 0x00, 0x00 };
            Assert.That(bomValue.UTF_32_LITTLE_ENDIAN, Is.EqualTo(expected));
        }

        [Test]
        public void UTF32BigEndianValue_IsCorrect()
        {
            dynamic bomValue = PythonEngineManager.BOMValueClass();
            byte[] expected = new byte[] { 0x00, 0x00, 0xfe, 0xff };
            Assert.That(bomValue.UTF_32_BIG_ENDIAN, Is.EqualTo(expected));
        }
    }
}
