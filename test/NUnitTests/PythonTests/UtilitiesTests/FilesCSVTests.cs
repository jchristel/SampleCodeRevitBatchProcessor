using PythonTests.Setup;

namespace PythonTests.UtilitiesTests
{
    public class FilesCSVTests
    {
        private string tempDirectory;

        /// <summary>
        /// Delegate for writing report data.
        /// </summary>
        /// <param name="parameters">A dictionary containing the parameters for the write_report_data function.</param>
        /// <returns>A dynamic result object containing the status and message of the write operation.</returns>
        private static readonly WriteReportDataDelegate writeReportDataDelegate = parameters =>
        {
            dynamic fileWriter = PythonEngineManager.FilesCSVModule;

            return fileWriter.write_report_data(
                file_name: (string)parameters["file_name"],
                header: (List<string>)parameters["header"],
                data: (List<List<string>>)parameters["data"],
                write_type: (string)parameters["write_type"],
                enforce_ascii: (bool)parameters["enforce_ascii"],
                encoding: (string)parameters["encoding"],
                bom: (object)parameters["bom"],
                quoting: (int)parameters["quoting"]
            );
        };


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
            Assert.That(PythonEngineManager.FilesCSVModule, Is.Not.Null, "file_csv should be loaded.");
        }

        [Test]
        public void WriteReportDataAsCsv_CreatesCsvFileWithLatinEncoding_HeaderAndData()
        {
            _CommonFilesBaseWriteTests.WriteReportDataAs_CreatesFileWithLatinEncoding_HeaderAndData(tempDirectory, ",", writeReportDataDelegate);
        }

        [Test]
        public void WriteReportData_CreatesReportFile_HeaderAndData()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFile_HeaderAndData(tempDirectory, ",", writeReportDataDelegate);
        }

        [Test]
        public void WriteReportData_CreatesReportFile_HeaderOnly()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFile_HeaderOnly(tempDirectory, ",", writeReportDataDelegate);
        }

        [Test]
        public void WriteReportData_CreatesReportFile_DataOnly()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFile_DataOnly(tempDirectory, ",", writeReportDataDelegate);
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithDelimiter_HeaderAndData()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFileWithDelimiter_HeaderAndData(tempDirectory, ",", writeReportDataDelegate);
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithDelimiter_HeaderOnly()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFileWithDelimiter_HeaderOnly(tempDirectory, ",", writeReportDataDelegate);
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithDelimiter_DataOnly()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFileWithDelimiter_DataOnly(tempDirectory, ",", writeReportDataDelegate);
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithNonUtf8_HeaderAndData()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFileWithNonUtf8_HeaderAndData(tempDirectory, ",", writeReportDataDelegate);
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithNonUtf8_HeaderOnly()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFileWithNonUtf8_HeaderOnly(tempDirectory, ",", writeReportDataDelegate);
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithNonUtf8_DataOnly()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFileWithNonUtf8_DataOnly(tempDirectory, ",", writeReportDataDelegate);
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithNonUtf8AndDelimiter_HeaderAndData()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFileWithNonUtf8AndDelimiter_HeaderAndData(tempDirectory, ",", writeReportDataDelegate);
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithNonUtf8AndDelimiter_HeaderOnly()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFileWithNonUtf8AndDelimiter_HeaderOnly(tempDirectory, ",", writeReportDataDelegate);
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithNonUtf8AndDelimiter_DataOnly()
        {

            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFileWithNonUtf8AndDelimiter_DataOnly(
                tempDirectory,
                ",",
                writeReportDataDelegate
            );
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithNonAsciiDataAndEnforceAscii()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFileWithNonAsciiDataAndEnforceAscii(tempDirectory,
                ",",
                writeReportDataDelegate
            );
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithBOM()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFileWithBOM(tempDirectory, ",", writeReportDataDelegate);
        }
    }
}
