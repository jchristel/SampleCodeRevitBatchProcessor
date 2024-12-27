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

        private void WriteTestFile(string fileName, List<string> header, List<List<string>> data, int quoting, string delimiter, string encoding, bool enforce_ascii, string write_type)
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;

            var writeResult = fileWriter.write_report_data(
                file_name: fileName,
                header: header,
                data: data,
                write_type: write_type,
                enforce_ascii: enforce_ascii,
                encoding: encoding,
                bom: null,
                quoting: quoting,
                delimiter: delimiter
            );
            Console.WriteLine(writeResult.message);

            Assert.That(writeResult.status, Is.True);
            Assert.That(File.Exists(fileName), Is.True);
        }

        [Test]
        public void WriteAndReadReportData_CreatesAndReadsReportFile()
        { 
            dynamic fileReader = PythonEngineManager.FilesBaseReadModule;
            string delimiter = ";";
            // Arrange
            var (fileName, header, data) = FileBaseTestsData.StandardTestData_HeaderAndData(tempDirectory);

            // Act - Write data to file
            WriteTestFile(fileName, header, data, 3, ";", "utf-8", false,"w"); // csv.QUOTE_NONE

            // Act - Read data from file
            var readResult = fileReader.read_column_based_text_file_without_encoding(
                file_path: fileName,
                increase_max_field_size_limit: false,
                delimiter: ";"
            );
            Console.WriteLine(readResult.message);

            // Assert - Check read result
            Assert.That(readResult.status, Is.True);
            var readData = readResult.result;

            // Determine header count
            int headerCount = header.Count > 0 ? 1 : 0;

            // Check for the number of rows
            Assert.That(readData.Count, Is.EqualTo(data.Count + headerCount)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(readData[0], Is.EqualTo(header));
            Assert.That(readData[1], Is.EqualTo(data[0]));
            Assert.That(readData[2], Is.EqualTo(data[1]));
        }

        [Test]
        public void WriteAndReadReportData_CreatesAndReadsReportFileWithDelimiterInData()
        {
            dynamic fileReader = PythonEngineManager.FilesBaseReadModule;
            string delimiter = ";";
            // Arrange
            var (fileName, header, data) = FileBaseTestsData.DelimitedTestData_DataOnly(tempDirectory);

            // Act - Write data to file
            WriteTestFile(fileName, header, data, 0, ";", "utf-8", false, "w"); // csv.QUOTE_MINIMAL

            // Act - Read data from file
            var readResult = fileReader.read_column_based_text_file_without_encoding(
                file_path: fileName,
                increase_max_field_size_limit: false,
                delimiter: ";"
            );
            Console.WriteLine(readResult.message);

            // Assert - Check read result
            Assert.That(readResult.status, Is.True);
            var readData = readResult.result;

            // Determine header count
            int headerCount = header.Count > 0 ? 1 : 0;

            // Check for the number of rows
            Assert.That(readData.Count, Is.EqualTo(data.Count + headerCount)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(readData[0], Is.EqualTo(header));
            Assert.That(readData[1], Is.EqualTo(data[0]));
            Assert.That(readData[2], Is.EqualTo(data[1]));
        }

        [Test]
        public void WriteAndReadReportData_CreatesAndReadsReportFileWithDelimiterInHeader()
        {
            dynamic fileReader = PythonEngineManager.FilesBaseReadModule;
            string delimiter = ";";
            // Arrange
            var (fileName, header, data) = FileBaseTestsData.DelimitedTestData_HeaderOnly(tempDirectory);

            // Act - Write data to file
            WriteTestFile(fileName, header, data, 0, ";", "utf-8", false, "w"); // csv.QUOTE_MINIMAL

            // Act - Read data from file
            var readResult = fileReader.read_column_based_text_file_without_encoding(
                file_path: fileName,
                increase_max_field_size_limit: false,
                delimiter: ";"
            );
            Console.WriteLine(readResult.message);

            // Assert - Check read result
            Assert.That(readResult.status, Is.True);
            var readData = readResult.result;

            // Determine header count
            int headerCount = header.Count > 0 ? 1 : 0;

            // Check for the number of rows
            Assert.That(readData.Count, Is.EqualTo(data.Count + headerCount)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(readData[0], Is.EqualTo(header));
        }

        [Test]
        public void WriteAndReadReportData_CreatesAndReadsReportFileWithDelimiterInHeaderAndData()
        {
            dynamic fileReader = PythonEngineManager.FilesBaseReadModule;
            string delimiter = ";";
            // Arrange
            var (fileName, header, data) = FileBaseTestsData.DelimitedTestData_HeaderAndData(tempDirectory);

            // Act - Write data to file
            WriteTestFile(fileName, header, data, 0, ";", "utf-8", false, "w"); // csv.QUOTE_MINIMAL

            // Act - Read data from file
            var readResult = fileReader.read_column_based_text_file_without_encoding(
                file_path: fileName,
                increase_max_field_size_limit: false,
                delimiter: ";"
            );
            Console.WriteLine(readResult.message);

            // Assert - Check read result
            Assert.That(readResult.status, Is.True);
            var readData = readResult.result;

            // Determine header count
            int headerCount = header.Count > 0 ? 1 : 0;

            // Check for the number of rows
            Assert.That(readData.Count, Is.EqualTo(data.Count + headerCount)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(readData[0], Is.EqualTo(header));
            Assert.That(readData[1], Is.EqualTo(data[0]));
            Assert.That(readData[2], Is.EqualTo(data[1]));
        }


        [Test]
        public void WriteAndReadReportData_CreatesAndReadsReportFileWithMaxFieldSizeLimit()
        {
            dynamic fileReader = PythonEngineManager.FilesBaseReadModule;
            string delimiter = ";";
            // Arrange
            var (fileName, header, data) = FileBaseTestsData.ArrangeMaxFieldSizeTestData(tempDirectory);
            // Act - Write data to file
            WriteTestFile(fileName, header, data, 3, ";", "utf-8", false, "w"); // csv.QUOTE_MINIMAL

            // Act - Read data from file with increased max field size limit
            var readResult = fileReader.read_column_based_text_file_without_encoding(
                file_path: fileName,
                increase_max_field_size_limit: true,
                delimiter: ";"
            );
            Console.WriteLine(readResult.message);

            // Assert - Check read result
            Assert.That(readResult.status, Is.True);
            var readData = readResult.result;

            // Determine header count
            int headerCount = header.Count > 0 ? 1 : 0;

            // Check for the number of rows
            Assert.That(readData.Count, Is.EqualTo(data.Count + headerCount)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(readData[0], Is.EqualTo(header));
            Assert.That(readData[1], Is.EqualTo(data[0]));
            Assert.That(readData[2], Is.EqualTo(data[1]));
        }
    }
}
