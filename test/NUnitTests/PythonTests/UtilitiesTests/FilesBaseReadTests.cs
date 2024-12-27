using PythonTests.Setup;

namespace PythonTests.UtilitiesTests
{
    public class FilesBaseReadTests
    {
        private string tempDirectory;

        [SetUp]
        public void SetUp()
        {
            tempDirectory = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
            Directory.CreateDirectory(tempDirectory);
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
            Assert.That(PythonEngineManager.FilesBaseReadModule, Is.Not.Null, "file_base_read should be loaded.");
        }

        # region WriteAndReadWithoutEncodingReportData

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFile_HeaderAndData()
        { 
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFile_HeaderAndData(tempDirectory,";");
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFile_HeaderOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFile_HeaderOnly(tempDirectory, ";");
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFile_DataOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFile_DataOnly(tempDirectory, ";");
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiter_HeaderAndData()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiter_HeaderAndData(tempDirectory, ";");
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiter_HeaderOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiter_HeaderOnly(tempDirectory, ";");
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiter_DataOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiter_DataOnly(tempDirectory, ";");
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_HeaderAndData()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_HeaderAndData(tempDirectory, ";");
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_HeaderOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_HeaderOnly(tempDirectory, ";");
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_DataOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_DataOnly(tempDirectory, ";");
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_HeaderAndData()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_HeaderAndData(tempDirectory, ";");
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_HeaderOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_HeaderOnly(tempDirectory, ";");
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_DataOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_DataOnly(tempDirectory, ";");
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithMaxFieldSizeLimit()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithMaxFieldSizeLimit(tempDirectory,";");
        }
    }

    #endregion WriteAndReadWithoutEncodingReportData
}
