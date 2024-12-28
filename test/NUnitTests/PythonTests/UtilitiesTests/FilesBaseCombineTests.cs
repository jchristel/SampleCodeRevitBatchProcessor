using PythonTests.Setup;
using System.Collections.Generic;


namespace PythonTests.UtilitiesTests
{
    public class FilesBaseCombineTests
    {
        private string tempDirectory;

        /// <summary>
        /// Delegate for combining report data files.
        /// </summary>
        /// <param name="parameters">A dictionary containing the parameters for the write_report_data function.</param>
        /// <returns>A dynamic result object containing the status and message of the write operation.</returns>
        private static readonly CombineReportDataDelegate combineReportDataDelegate = parameters =>
        {
            dynamic fileCombiner = PythonEngineManager.FilesBaseCombineModule;

            return fileCombiner.combine_files(
                folder_path: (string)parameters["folder_path"],
                file_prefix: (string)parameters["file_prefix"],
                file_suffix: (string)parameters["file_suffix"],
                file_extension: (string)parameters["file_extension"],
                output_file_name: (string)parameters["output_file_name"],
                delimiter: (string)parameters["delimiter"]
            );
        };

        /// <summary>
        /// Delegate for combining report data files header independent.
        /// </summary>
        /// <param name="parameters">A dictionary containing the parameters for the write_report_data function.</param>
        /// <returns>A dynamic result object containing the status and message of the write operation.</returns>
        private static readonly CombineReportDataDelegate combineReportDataHeaderIndependentDelegate = parameters =>
        {
            dynamic fileCombiner = PythonEngineManager.FilesBaseCombineModule;

            return fileCombiner.combine_files_header_independent(
                folder_path: (string)parameters["folder_path"],
                file_prefix: (string)parameters["file_prefix"],
                file_suffix: (string)parameters["file_suffix"],
                file_extension: (string)parameters["file_extension"],
                output_file_name: (string)parameters["output_file_name"],
                overwrite_existing: (bool)parameters["overwrite_existing"],
                delimiter: (string)parameters["delimiter"]
            );
        };

        /// <summary>
        /// Delegate for appending report data files.
        /// </summary>
        /// <param name="parameters">A dictionary containing the parameters for the write_report_data function.</param>
        /// <returns>A dynamic result object containing the status and message of the write operation.</returns>
        private static readonly CombineReportDataDelegate appendReportDataDelegate = parameters =>
        {
            dynamic fileCombiner = PythonEngineManager.FilesBaseCombineModule;

            return fileCombiner.append_to_file(
                source_file: (string)parameters["source_file"],
                append_file: (string)parameters["append_file"],
                ignore_first_row: (bool)parameters["ignore_first_row"],
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
            Assert.That(PythonEngineManager.FilesBaseCombineModule, Is.Not.Null, "file_combine should be loaded.");
        }

        [Test]
        public void CombineFiles_CreatesCombinedFile()
        {
            _CommonFilesBaseCombineTests.CombineFiles_CreatesCombinedFile(tempDirectory,";", combineReportDataDelegate);
        }

        [Test]
        public void CombineFiles_CreatesCombinedFileWithFourFilesAndMultipleRows()
        {
            _CommonFilesBaseCombineTests.CombineFiles_CreatesCombinedFileWithFourFilesAndMultipleRows(tempDirectory, ";", combineReportDataDelegate);
        }

        [Test]
        public void CombineFiles_CreatesCombinedFileWithSuffix()
        {
            _CommonFilesBaseCombineTests.CombineFiles_CreatesCombinedFileWithSuffix(tempDirectory, ";", combineReportDataDelegate);
        }

        [Test]
        public void CombineFiles_CreatesCombinedFileWithPrefix()
        {
            _CommonFilesBaseCombineTests.CombineFiles_CreatesCombinedFileWithPrefix(tempDirectory, ";", combineReportDataDelegate);
        }
        [Test]
        public void CombineFiles_CreatesCombinedFileWithPrefixAndSuffix()
        {
            _CommonFilesBaseCombineTests.CombineFiles_CreatesCombinedFileWithPrefixAndSuffix(tempDirectory, ";", combineReportDataDelegate);
        }

        [Test]
        public void CombineFiles_CreatesCombinedFileWithDifferentExtension()
        {
            _CommonFilesBaseCombineTests.CombineFiles_CreatesCombinedFileWithDifferentExtension(tempDirectory, ";", combineReportDataDelegate);
        }

        [Test]
        public void CombineFiles_CreatesCombinedFileWithMissingNewline()
        {
            _CommonFilesBaseCombineTests.CombineFiles_CreatesCombinedFileWithMissingNewline(tempDirectory, ";", combineReportDataDelegate);
        }

        [Test]
        public void AppendToFile_AppendsContent()
        {
            _CommonFilesBaseCombineTests.AppendToFile_AppendsContent(tempDirectory, ";", appendReportDataDelegate);
        }

        [Test]
        public void AppendToFile_AppendsContentWithMissingNewline()
        {
            _CommonFilesBaseCombineTests.AppendToFile_AppendsContentWithMissingNewline(tempDirectory, ";", appendReportDataDelegate);
            
        }

        [Test]
        public void AppendToFile_AppendsContentWithMissingNewlineWithoutIgnoringFirstRow()
        {
            _CommonFilesBaseCombineTests.AppendToFile_AppendsContentWithMissingNewlineWithoutIgnoringFirstRow(tempDirectory, ";", appendReportDataDelegate);
        }

        [Test]
        public void CombineFilesHeaderIndependent_CreatesCombinedFile()
        {
            _CommonFilesBaseCombineTests.CombineFilesHeaderIndependent_CreatesCombinedFile(tempDirectory, ";", combineReportDataHeaderIndependentDelegate);

        }

        [Test]
        public void CombineFilesHeaderIndependent_CreatesCombinedFileWithFourFiles()
        {
            _CommonFilesBaseCombineTests.CombineFilesHeaderIndependent_CreatesCombinedFileWithFourFiles(tempDirectory, ";", combineReportDataHeaderIndependentDelegate);
        }

        [Test]
        public void CombineFilesHeaderIndependent_CreatesCombinedFileWithFourFilesAndMultipleRows()
        {
            _CommonFilesBaseCombineTests.CombineFilesHeaderIndependent_CreatesCombinedFileWithFourFilesAndMultipleRows(tempDirectory, ";", combineReportDataHeaderIndependentDelegate);
        }
    }
}
