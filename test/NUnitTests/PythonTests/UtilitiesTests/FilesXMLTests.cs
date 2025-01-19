using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using PythonTests.Setup;

namespace PythonTests.UtilitiesTests
{
    public class FilesXMLTests
    {

        private string tempDirectory;

        private string dataTestDirectory;


        [SetUp]
        public void SetUp()
        {
            tempDirectory = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
            Directory.CreateDirectory(tempDirectory);

            dataTestDirectory = PythonTests.PythonRunner.GetTestDataPath();

        }

        [TearDown]
        public void TearDown()
        {
            if (Directory.Exists(tempDirectory))
            {
                Directory.Delete(tempDirectory, true);
            }
        }

        [Test]
        public void ModuleShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.FilesXMLModule, Is.Not.Null, "file_xml should be loaded.");
        }

        [Test]
        public void ReadXMLFile_InvalidPath()
        {
            dynamic xmlReader = PythonEngineManager.FilesXMLModule;

            // Arrange
            string invalidFileName = Path.Combine(tempDirectory, @"NonExistentFile.xml");

            // Act
            var result = xmlReader.read_xml_file(file_path: invalidFileName);

            // Assert
            Assert.That(result.status, Is.False, "no file found");
        }

        [Test]
        public void ReadXMLFile_ValidPath()
        {
            dynamic xmlReader = PythonEngineManager.FilesXMLModule;

            // Arrange
            string fileName = Path.Combine(dataTestDirectory, @"XMLData_01\Sample_Family_Five.xml");

            // Act
            var result = xmlReader.read_xml_file(file_path: fileName);

            // Assert
            Assert.That(result.status, Is.True);
            Assert.That(result.result, Is.Not.Null);
        }

    }
}
