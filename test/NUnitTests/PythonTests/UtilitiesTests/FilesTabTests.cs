using PythonTests.Setup;

namespace PythonTests.UtilitiesTests
{
    public class FilesTabTests
    {
        private string tempDirectory;

        /// <summary>
        /// Delegate for writing report data.
        /// </summary>
        /// <param name="parameters">A dictionary containing the parameters for the write_report_data function.</param>
        /// <returns>A dynamic result object containing the status and message of the write operation.</returns>
        private static readonly WriteReportDataDelegate writeReportDataDelegate = parameters =>
        {
            dynamic fileWriter = PythonEngineManager.FilesTabModule;

            return fileWriter.write_report_data_as_tab_separated_file(
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

        /// <summary>
        /// Delegate for reading report data.
        /// </summary>
        /// <param name="parameters">A dictionary containing the parameters for the write_report_data function.</param>
        /// <returns>A dynamic result object containing the status and message of the write operation.</returns>
        private static readonly ReadReportDataDelegate readReportDataDelegate = parameters =>
        {
            dynamic fileReader = PythonEngineManager.FilesTabModule;

            return fileReader.read_tab_separated_file(
                file_path: (string)parameters["file_path"],
                increase_max_field_size_limit: (bool)parameters["increase_max_field_size_limit"]
            );
        };

        /// <summary>
        /// Delegate for reading first row data encoded.
        /// </summary>
        /// <param name="parameters">A dictionary containing the parameters for the write_report_data function.</param>
        /// <returns>A dynamic result object containing the status and message of the write operation.</returns>
        private static readonly ReadReportDataDelegate readFirstRowEncodedDelegate = parameters =>
        {
            dynamic fileReader = PythonEngineManager.FilesTabModule;

            return fileReader.get_first_row_in_tab_separated_file(
                file_path: (string)parameters["file_path"]
            );
        };

        /// <summary>
        /// Delegate for combining report data files.
        /// </summary>
        /// <param name="parameters">A dictionary containing the parameters for the write_report_data function.</param>
        /// <returns>A dynamic result object containing the status and message of the write operation.</returns>
        private static readonly CombineReportDataDelegate combineReportDataDelegate = parameters =>
        {
            dynamic fileCombiner = PythonEngineManager.FilesTabModule;

            return fileCombiner.combine_tab_separated_files(
                folder_path: (string)parameters["folder_path"],
                file_prefix: (string)parameters["file_prefix"],
                file_suffix: (string)parameters["file_suffix"],
                file_extension: (string)parameters["file_extension"],
                output_file_name: (string)parameters["output_file_name"]
            );
            //folder_path,file_prefix="",file_suffix = "",file_extension = ".csv",output_file_name = "result.csv",file_getter = get_files_single_directory,quoting = csv.QUOTE_MINIMAL
        };

        /// <summary>
        /// Delegate for combining report data files header independent.
        /// </summary>
        /// <param name="parameters">A dictionary containing the parameters for the write_report_data function.</param>
        /// <returns>A dynamic result object containing the status and message of the write operation.</returns>
        private static readonly CombineReportDataDelegate combineReportDataHeaderIndependentDelegate = parameters =>
        {
            dynamic fileCombiner = PythonEngineManager.FilesTabModule;

            return fileCombiner.combine_tab_separated_files_header_independent(
                folder_path: (string)parameters["folder_path"],
                file_prefix: (string)parameters["file_prefix"],
                file_suffix: (string)parameters["file_suffix"],
                file_extension: (string)parameters["file_extension"],
                output_file_name: (string)parameters["output_file_name"],
                overwrite_existing: (bool)parameters["overwrite_existing"]
            );

            // folder_path,file_prefix = "",file_suffix = "",file_extension = ".csv",output_file_name = "csv.txt",overwrite_existing = False,
        };

        /// <summary>
        /// Delegate for appending report data files.
        /// </summary>
        /// <param name="parameters">A dictionary containing the parameters for the write_report_data function.</param>
        /// <returns>A dynamic result object containing the status and message of the write operation.</returns>
        private static readonly CombineReportDataDelegate appendReportDataDelegate = parameters =>
        {
            dynamic fileCombiner = PythonEngineManager.FilesTabModule;

            return fileCombiner.append_tab_separated_file(
                source_file: (string)parameters["source_file"],
                append_file: (string)parameters["append_file"],
                ignore_first_row: (bool)parameters["ignore_first_row"]
            );

            //(source_file, append_file, ignore_first_row=False, quoting=csv.QUOTE_MINIMAL)
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
            Assert.That(PythonEngineManager.FilesTabModule, Is.Not.Null, "file_tab should be loaded.");
        }

        [Test]
        public void WriteReportData_CreatesFileWithLatinEncoding_HeaderAndData()
        {
            _CommonFilesBaseWriteTests.WriteReportDataAs_CreatesFileWithLatinEncoding_HeaderAndData(tempDirectory, "\t", writeReportDataDelegate);
        }

        [Test]
        public void WriteReportData_CreatesReportFile_HeaderAndData()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFile_HeaderAndData(tempDirectory, "\t", writeReportDataDelegate);
        }

        [Test]
        public void WriteReportData_CreatesReportFile_HeaderOnly()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFile_HeaderOnly(tempDirectory, "\t", writeReportDataDelegate);
        }

        [Test]
        public void WriteReportData_CreatesReportFile_DataOnly()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFile_DataOnly(tempDirectory, "\t", writeReportDataDelegate);
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithDelimiter_HeaderAndData()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFileWithDelimiter_HeaderAndData(tempDirectory, "\t", writeReportDataDelegate);
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithDelimiter_HeaderOnly()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFileWithDelimiter_HeaderOnly(tempDirectory, "\t", writeReportDataDelegate);
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithDelimiter_DataOnly()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFileWithDelimiter_DataOnly(tempDirectory, "\t", writeReportDataDelegate);
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithNonUtf8_HeaderAndData()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFileWithNonUtf8_HeaderAndData(tempDirectory, "\t", writeReportDataDelegate);
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithNonUtf8_HeaderOnly()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFileWithNonUtf8_HeaderOnly(tempDirectory, "\t", writeReportDataDelegate);
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithNonUtf8_DataOnly()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFileWithNonUtf8_DataOnly(tempDirectory, "\t", writeReportDataDelegate);
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithNonUtf8AndDelimiter_HeaderAndData()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFileWithNonUtf8AndDelimiter_HeaderAndData(tempDirectory, "\t", writeReportDataDelegate);
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithNonUtf8AndDelimiter_HeaderOnly()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFileWithNonUtf8AndDelimiter_HeaderOnly(tempDirectory, "\t", writeReportDataDelegate);
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithNonUtf8AndDelimiter_DataOnly()
        {

            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFileWithNonUtf8AndDelimiter_DataOnly(
                tempDirectory,
                "\t",
                writeReportDataDelegate
            );
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithNonAsciiDataAndEnforceAscii()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFileWithNonAsciiDataAndEnforceAscii(tempDirectory,
                "\t",
                writeReportDataDelegate
            );
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithBOM()
        {
            _CommonFilesBaseWriteTests.WriteReportData_CreatesReportFileWithBOM(tempDirectory, "\t", writeReportDataDelegate);
        }

        # region WriteAndReadWithEncodingReportData

        // the csv reader function attempts to read the file with the encoding utf-8 and utf-16 first if that fails it will try to read the file without any ewncoding
        // tests below ensures that the file is written with utf-8 encoding and therefore the read function will be able to read the file with utf-8 encoding

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFile_HeaderAndData()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFile_HeaderAndData(
                tempDirectory,
                "\t",
                writeReportDataDelegate,
                readReportDataDelegate
            );
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFile_HeaderOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFile_HeaderOnly(
                tempDirectory,
                "\t",
                writeReportDataDelegate,
                readReportDataDelegate
            );
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFile_DataOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsReportFile_DataOnly(tempDirectory, "\t", writeReportDataDelegate, readReportDataDelegate);
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithDelimiter_HeaderAndData()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithDelimiter_HeaderAndData(tempDirectory, "\t", writeReportDataDelegate, readReportDataDelegate);
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithDelimiter_HeaderOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithDelimiter_HeaderOnly(tempDirectory, "\t", writeReportDataDelegate, readReportDataDelegate);
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithDelimiter_DataOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithDelimiter_DataOnly(tempDirectory, "\t", writeReportDataDelegate, readReportDataDelegate);
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_HeaderAndData()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_HeaderAndData(tempDirectory, "\t", writeReportDataDelegate, readReportDataDelegate);
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_HeaderOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_HeaderOnly(tempDirectory, "\t", writeReportDataDelegate, readReportDataDelegate);
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_DataOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_DataOnly(tempDirectory, "\t", writeReportDataDelegate, readReportDataDelegate);
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_HeaderAndData()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_HeaderAndData(tempDirectory, "\t", writeReportDataDelegate, readReportDataDelegate);
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_HeaderOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_HeaderOnly(tempDirectory, "\t", writeReportDataDelegate, readReportDataDelegate);
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_DataOnly()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_DataOnly(tempDirectory, "\t", writeReportDataDelegate, readReportDataDelegate);
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithMaxFieldSizeLimit()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsReportFileWithMaxFieldSizeLimit_HeaderAndData(tempDirectory, "\t", writeReportDataDelegate, readReportDataDelegate);
        }

        #endregion WriteAndReadWithoutEncodingReportData


        #region WriteAndReadWithEncodingFirstRow

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsFirstRow_HeaderAndData()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsFirstRow_HeaderAndData(tempDirectory, "\t", writeReportDataDelegate, readFirstRowEncodedDelegate);
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsFirstRowDelimited_HeaderAndData()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsFirstRowWithDelimiter_HeaderAndData(tempDirectory, "\t", writeReportDataDelegate, readFirstRowEncodedDelegate);
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsFirstRowNonUTF8AndDelimited_HeaderAndData()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsFirstRowWithUTF8AndDelimiter_HeaderAndData(tempDirectory, "\t", writeReportDataDelegate, readFirstRowEncodedDelegate);
        }

        [Test]
        public void WriteAndReadWithEncodingReportData_CreatesAndReadsFirstRow_EmptyFile()
        {
            _CommonFilesBaseReadTests.WriteAndReadWithEncodingReportData_CreatesAndReadsFirstRow_EmptyFile(tempDirectory, "\t", writeReportDataDelegate, readFirstRowEncodedDelegate);
        }

        #endregion WriteAndReadWithEncodingFirstRow

        #region combine files

        [Test]
        public void CombineFiles_CreatesCombinedFile()
        {
            _CommonFilesBaseCombineTests.CombineFiles_CreatesCombinedFile(tempDirectory, "\t", combineReportDataDelegate);
        }

        [Test]
        public void CombineFiles_CreatesCombinedFileWithFourFilesAndMultipleRows()
        {
            _CommonFilesBaseCombineTests.CombineFiles_CreatesCombinedFileWithFourFilesAndMultipleRows(tempDirectory, "\t", combineReportDataDelegate);
        }

        [Test]
        public void CombineFiles_CreatesCombinedFileWithSuffix()
        {
            _CommonFilesBaseCombineTests.CombineFiles_CreatesCombinedFileWithSuffix(tempDirectory, "\t", combineReportDataDelegate);
        }

        [Test]
        public void CombineFiles_CreatesCombinedFileWithPrefix()
        {
            _CommonFilesBaseCombineTests.CombineFiles_CreatesCombinedFileWithPrefix(tempDirectory, "\t", combineReportDataDelegate);
        }
        [Test]
        public void CombineFiles_CreatesCombinedFileWithPrefixAndSuffix()
        {
            _CommonFilesBaseCombineTests.CombineFiles_CreatesCombinedFileWithPrefixAndSuffix(tempDirectory, "\t", combineReportDataDelegate);
        }

        [Test]
        public void CombineFiles_CreatesCombinedFileWithDifferentExtension()
        {
            _CommonFilesBaseCombineTests.CombineFiles_CreatesCombinedFileWithDifferentExtension(tempDirectory, "\t", combineReportDataDelegate);
        }

        [Test]
        public void CombineFiles_CreatesCombinedFileWithMissingNewline()
        {
            _CommonFilesBaseCombineTests.CombineFiles_CreatesCombinedFileWithMissingNewline(tempDirectory, "\t", combineReportDataDelegate);
        }

        [Test]
        public void AppendToFile_AppendsContent()
        {
            _CommonFilesBaseCombineTests.AppendToFile_AppendsContent(tempDirectory, "\t", appendReportDataDelegate);
        }

        [Test]
        public void AppendToFile_AppendsContentWithMissingNewline()
        {
            _CommonFilesBaseCombineTests.AppendToFile_AppendsContentWithMissingNewline(tempDirectory, "\t", appendReportDataDelegate);

        }

        [Test]
        public void AppendToFile_AppendsContentWithMissingNewlineWithoutIgnoringFirstRow()
        {
            _CommonFilesBaseCombineTests.AppendToFile_AppendsContentWithMissingNewlineWithoutIgnoringFirstRow(tempDirectory, "\t", appendReportDataDelegate);
        }

        [Test]
        public void CombineFilesHeaderIndependent_CreatesCombinedFile()
        {
            _CommonFilesBaseCombineTests.CombineFilesHeaderIndependent_CreatesCombinedFile(tempDirectory, "\t", combineReportDataHeaderIndependentDelegate);

        }

        [Test]
        public void CombineFilesHeaderIndependent_CreatesCombinedFileWithFourFiles()
        {
            _CommonFilesBaseCombineTests.CombineFilesHeaderIndependent_CreatesCombinedFileWithFourFiles(tempDirectory, "\t", combineReportDataHeaderIndependentDelegate);
        }

        [Test]
        public void CombineFilesHeaderIndependent_CreatesCombinedFileWithFourFilesAndMultipleRows()
        {
            _CommonFilesBaseCombineTests.CombineFilesHeaderIndependent_CreatesCombinedFileWithFourFilesAndMultipleRows(tempDirectory, "\t", combineReportDataHeaderIndependentDelegate);
        }
        #endregion combine files
    }
}
