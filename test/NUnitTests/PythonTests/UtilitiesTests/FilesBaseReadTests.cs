using PythonTests.Setup;

namespace PythonTests.UtilitiesTests
{
    public class FilesBaseReadTests
    {
        private string tempDirectory;

        /// <summary>
        /// Delegate for writing report data.
        /// </summary>
        /// <param name="parameters">A dictionary containing the parameters for the write_report_data function.</param>
        /// <returns>A dynamic result object containing the status and message of the write operation.</returns>
        private static readonly WriteReportDataDelegate writeReportDataDelegate = parameters =>
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;

            return fileWriter.write_report_data(
                file_name: (string)parameters["file_name"],
                header: (List<string>)parameters["header"],
                data: (List<List<string>>)parameters["data"],
                write_type: (string)parameters["write_type"],
                enforce_ascii: (bool)parameters["enforce_ascii"],
                encoding: (string)parameters["encoding"],
                bom: (object)parameters["bom"],
                quoting: (int)parameters["quoting"],
                delimiter: (string)parameters["delimiter"]
            );
        };

        /// <summary>
        /// Delegate for reading report data.
        /// </summary>
        /// <param name="parameters">A dictionary containing the parameters for the write_report_data function.</param>
        /// <returns>A dynamic result object containing the status and message of the write operation.</returns>
        private static readonly ReadReportDataDelegate readReportDataDelegate = parameters =>
        {
            dynamic fileReader = PythonEngineManager.FilesBaseReadModule;

            return fileReader.read_column_based_text_file_without_encoding(
                file_path: (string)parameters["file_path"],
                increase_max_field_size_limit: (bool)parameters["increase_max_field_size_limit"],
                delimiter: (string)parameters["delimiter"]
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
            Assert.That(PythonEngineManager.FilesBaseReadModule, Is.Not.Null, "file_base_read should be loaded.");
        }

        # region WriteAndReadWithoutEncodingReportData

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFile_HeaderAndData()
        { 
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFile_HeaderAndData(
                tempDirectory,
                ";", 
                writeReportDataDelegate, 
                readReportDataDelegate
            );
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFile_HeaderOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFile_HeaderOnly(
                tempDirectory,
                ";",
                writeReportDataDelegate,
                readReportDataDelegate
            );
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFile_DataOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFile_DataOnly(tempDirectory, ";", writeReportDataDelegate, readReportDataDelegate);
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiter_HeaderAndData()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiter_HeaderAndData(tempDirectory, ";", writeReportDataDelegate, readReportDataDelegate);
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiter_HeaderOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiter_HeaderOnly(tempDirectory, ";", writeReportDataDelegate, readReportDataDelegate);
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiter_DataOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiter_DataOnly(tempDirectory, ";", writeReportDataDelegate, readReportDataDelegate);
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_HeaderAndData()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_HeaderAndData(tempDirectory, ";", writeReportDataDelegate, readReportDataDelegate);
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_HeaderOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_HeaderOnly(tempDirectory, ";", writeReportDataDelegate, readReportDataDelegate);
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_DataOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_DataOnly(tempDirectory, ";", writeReportDataDelegate, readReportDataDelegate);
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_HeaderAndData()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_HeaderAndData(tempDirectory, ";", writeReportDataDelegate, readReportDataDelegate);
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_HeaderOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_HeaderOnly(tempDirectory, ";", writeReportDataDelegate, readReportDataDelegate);
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_DataOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_DataOnly(tempDirectory, ";", writeReportDataDelegate, readReportDataDelegate);
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithMaxFieldSizeLimit()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithMaxFieldSizeLimit_HeaderAndData(tempDirectory, ";", writeReportDataDelegate, readReportDataDelegate);
        }
        #endregion WriteAndReadWithoutEncodingReportData
    }


}
