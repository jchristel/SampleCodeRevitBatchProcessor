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
        /// Delegate for reading report data not encoded.
        /// </summary>
        /// <param name="parameters">A dictionary containing the parameters for the write_report_data function.</param>
        /// <returns>A dynamic result object containing the status and message of the write operation.</returns>
        private static readonly ReadReportDataDelegate readReportDataNoEncodingDelegate = parameters =>
        {
            dynamic fileReader = PythonEngineManager.FilesBaseReadModule;

            return fileReader.read_column_based_text_file_without_encoding(
                file_path: (string)parameters["file_path"],
                increase_max_field_size_limit: (bool)parameters["increase_max_field_size_limit"],
                delimiter: (string)parameters["delimiter"]
            );
        };

        /// <summary>
        /// Delegate for reading report data encoded.
        /// </summary>
        /// <param name="parameters">A dictionary containing the parameters for the write_report_data function.</param>
        /// <returns>A dynamic result object containing the status and message of the write operation.</returns>
        private static readonly ReadReportDataDelegate readReportDataEncodedDelegate = parameters =>
        {
            dynamic fileReader = PythonEngineManager.FilesBaseReadModule;

            return fileReader.read_column_based_text_file_with_encoding(
                file_path: (string)parameters["file_path"],
                increase_max_field_size_limit: (bool)parameters["increase_max_field_size_limit"],
                delimiter: (string)parameters["delimiter"]
            );
        };

        /// <summary>
        /// Delegate for reading first row data encoded.
        /// </summary>
        /// <param name="parameters">A dictionary containing the parameters for the write_report_data function.</param>
        /// <returns>A dynamic result object containing the status and message of the write operation.</returns>
        private static readonly ReadReportDataDelegate readFirstRowEncodedDelegate = parameters =>
        {
            dynamic fileReader = PythonEngineManager.FilesBaseReadModule;

            return fileReader.get_first_row_in_column_based_text_file(
                file_path: (string)parameters["file_path"],
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
                readReportDataNoEncodingDelegate
            );
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFile_HeaderOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFile_HeaderOnly(
                tempDirectory,
                ";",
                writeReportDataDelegate,
                readReportDataNoEncodingDelegate
            );
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFile_DataOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFile_DataOnly(tempDirectory, ";", writeReportDataDelegate, readReportDataNoEncodingDelegate);
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiter_HeaderAndData()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiter_HeaderAndData(tempDirectory, ";", writeReportDataDelegate, readReportDataNoEncodingDelegate);
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiter_HeaderOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiter_HeaderOnly(tempDirectory, ";", writeReportDataDelegate, readReportDataNoEncodingDelegate);
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiter_DataOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiter_DataOnly(tempDirectory, ";", writeReportDataDelegate, readReportDataNoEncodingDelegate);
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_HeaderAndData()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_HeaderAndData(tempDirectory, ";", writeReportDataDelegate, readReportDataNoEncodingDelegate);
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_HeaderOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_HeaderOnly(tempDirectory, ";", writeReportDataDelegate, readReportDataNoEncodingDelegate);
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_DataOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_DataOnly(tempDirectory, ";", writeReportDataDelegate, readReportDataNoEncodingDelegate);
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_HeaderAndData()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_HeaderAndData(tempDirectory, ";", writeReportDataDelegate, readReportDataNoEncodingDelegate);
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_HeaderOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_HeaderOnly(tempDirectory, ";", writeReportDataDelegate, readReportDataNoEncodingDelegate);
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_DataOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_DataOnly(tempDirectory, ";", writeReportDataDelegate, readReportDataNoEncodingDelegate);
        }

        [Test]
        public void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithMaxFieldSizeLimit()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithMaxFieldSizeLimit_HeaderAndData(tempDirectory, ";", writeReportDataDelegate, readReportDataNoEncodingDelegate);
        }
        #endregion WriteAndReadWithoutEncodingReportData

        #region WriteAndReadWithEncodingReportData
        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFile_HeaderAndData()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsReportFile_HeaderAndData(
                tempDirectory,
                ";",
                writeReportDataDelegate,
                readReportDataEncodedDelegate
            );
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFile_HeaderOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsReportFile_HeaderOnly(
                tempDirectory,
                ";",
                writeReportDataDelegate,
                readReportDataEncodedDelegate
            );
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFile_DataOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsReportFile_DataOnly(
                tempDirectory, 
                ";", 
                writeReportDataDelegate, 
                readReportDataEncodedDelegate
             );
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithDelimiter_HeaderAndData()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithDelimiter_HeaderAndData(
                tempDirectory, 
                ";", 
                writeReportDataDelegate,
                readReportDataEncodedDelegate
            );
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithDelimiter_HeaderOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithDelimiter_HeaderOnly(
                tempDirectory, 
                ";", 
                writeReportDataDelegate, 
                readReportDataEncodedDelegate
            );
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithDelimiter_DataOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithDelimiter_DataOnly(
                tempDirectory, 
                ";", 
                writeReportDataDelegate, 
                readReportDataEncodedDelegate
            );
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_HeaderAndData()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_HeaderAndData(
                tempDirectory, 
                ";", 
                writeReportDataDelegate, 
                readReportDataEncodedDelegate
            );
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_HeaderOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_HeaderOnly(
                tempDirectory, 
                ";", 
                writeReportDataDelegate, readReportDataEncodedDelegate
            );
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_DataOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_DataOnly(
                tempDirectory, 
                ";",
                writeReportDataDelegate, 
                readReportDataEncodedDelegate
            );
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_HeaderAndData()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_HeaderAndData(
                tempDirectory, 
                ";", 
                writeReportDataDelegate, readReportDataEncodedDelegate
            );
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_HeaderOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_HeaderOnly(
                tempDirectory, 
                ";", 
                writeReportDataDelegate, 
                readReportDataEncodedDelegate
            );
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_DataOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_DataOnly(
                tempDirectory, 
                ";", 
                writeReportDataDelegate, readReportDataEncodedDelegate
             );
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithMaxFieldSizeLimit()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithMaxFieldSizeLimit_HeaderAndData(tempDirectory, ";", writeReportDataDelegate, readReportDataNoEncodingDelegate);
        }
        #endregion WriteAndReadWithEncodingReportData

        #region WriteAndReadWithEncodingFirstRow

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsFirstRow_HeaderAndData()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsFirstRow_HeaderAndData(tempDirectory, ";", writeReportDataDelegate, readFirstRowEncodedDelegate);
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsFirstRowDelimited_HeaderAndData()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsFirstRowWithDelimiter_HeaderAndData(tempDirectory, ";", writeReportDataDelegate, readFirstRowEncodedDelegate);
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsFirstRowNonUTF8AndDelimited_HeaderAndData()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsFirstRowWithUTF8AndDelimiter_HeaderAndData(tempDirectory, ";", writeReportDataDelegate, readFirstRowEncodedDelegate);
        }

        [Test]

        public void WriteAndReadWithEncodingReportData_CreatesAndReadsFirstRow_EmptyFile()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsFirstRow_EmptyFile(tempDirectory, ";", writeReportDataDelegate, readFirstRowEncodedDelegate);
        }

        #endregion WriteAndReadWithEncodingFirstRow
    }


}
