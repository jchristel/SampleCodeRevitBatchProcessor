using PythonTests.Setup;

namespace PythonTests.UtilitiesTests
{
    public static class _CommonFilesBaseReadTests
    {
        private static void WriteTestFileBase(string fileName, List<string> header, List<List<string>> data, int quoting, string delimiter, string encoding, bool enforce_ascii, string write_type)
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

        # region WriteAndReadWithoutEncodingReportData
        
        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFile_HeaderAndData(string tempDirectory, string delimiter)
        { 
            dynamic fileReader = PythonEngineManager.FilesBaseReadModule;
            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.StandardTestData_HeaderAndData(tempDirectory, delimiter);

            // Act - Write data to file
            WriteTestFileBase(fileName, header, data, 3, ";", "utf-8", false,"w"); // csv.QUOTE_NONE

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

        
        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFile_HeaderOnly(string tempDirectory, string delimiter)
        {
            dynamic fileReader = PythonEngineManager.FilesBaseReadModule;

            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.StandardTestData_HeaderOnly(tempDirectory, delimiter);

            // Act - Write data to file
            WriteTestFileBase(fileName, header, data, 3, ";", "utf-8", false, "w"); // csv.QUOTE_NONE

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

        
        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFile_DataOnly(string tempDirectory, string delimiter)
        {
            dynamic fileReader = PythonEngineManager.FilesBaseReadModule;

            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.StandardTestData_DataOnly(tempDirectory, delimiter);

            // Act - Write data to file
            WriteTestFileBase(fileName, header, data, 3, ";", "utf-8", false, "w"); // csv.QUOTE_NONE

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
            Assert.That(readData[0], Is.EqualTo(data[0]));
            Assert.That(readData[1], Is.EqualTo(data[1]));
        }


        
        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiter_HeaderAndData(string tempDirectory, string delimiter)
        {
            dynamic fileReader = PythonEngineManager.FilesBaseReadModule;

            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.DelimitedTestData_HeaderAndData(tempDirectory, delimiter);

            // Act - Write data to file
            WriteTestFileBase(fileName, header, data, 0, ";", "utf-8", false, "w"); // csv.QUOTE_MINIMAL

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

        
        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiter_HeaderOnly(string tempDirectory, string delimiter)
        {
            dynamic fileReader = PythonEngineManager.FilesBaseReadModule;
            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.DelimitedTestData_HeaderOnly(tempDirectory, delimiter);

            // Act - Write data to file
            WriteTestFileBase(fileName, header, data, 0, ";", "utf-8", false, "w"); // csv.QUOTE_MINIMAL

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
            Assert.That(readData.Count, Is.EqualTo(data.Count + headerCount)); // 1 header row

            // Check for the content
            Assert.That(readData[0], Is.EqualTo(header));
        }

        
        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiter_DataOnly(string tempDirectory, string delimiter)
        {
            dynamic fileReader = PythonEngineManager.FilesBaseReadModule;

            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.DelimitedTestData_DataOnly(tempDirectory, delimiter);

            // Act - Write data to file
            WriteTestFileBase(fileName, header, data, 0, ";", "utf-8", false, "w"); // csv.QUOTE_MINIMAL

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
            Assert.That(readData.Count, Is.EqualTo(data.Count + headerCount)); // 2 data rows

            // Check for the content
            Assert.That(readData[0], Is.EqualTo(data[0]));
            Assert.That(readData[1], Is.EqualTo(data[1]));
        }

        
        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_HeaderAndData(string tempDirectory, string delimiter)
        {
            //data read back will not match the data written due to non-utf8 characters

            dynamic fileReader = PythonEngineManager.FilesBaseReadModule;

            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.NonUTF8TestData_HeaderAndData(tempDirectory, delimiter);

            // Act - Write data to file
            WriteTestFileBase(fileName, header, data, 0, ";", "utf-8", false, "w"); // csv.QUOTE_MINIMAL

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
            Assert.That(readData[0], Is.Not.EqualTo(header)); // Non-UTF-8 characters in header
            Assert.That(readData[1], Is.EqualTo(data[0])); // no non-utf8 characters in data
            Assert.That(readData[2], Is.Not.EqualTo(data[1])); // Non-UTF-8 character in data
        }


        
        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_HeaderOnly(string tempDirectory, string delimiter)
        {
            //header read back will not match the heade written due to non-utf8 characters

            dynamic fileReader = PythonEngineManager.FilesBaseReadModule;

            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.NonUTF8TestData_HeaderOnly(tempDirectory, delimiter);

            // Act - Write data to file
            WriteTestFileBase(fileName, header, data, 0, ";", "utf-8", false, "w"); // csv.QUOTE_MINIMAL

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
            Assert.That(readData.Count, Is.EqualTo(data.Count + headerCount)); // 1 header row

            // Check for the content
            Assert.That(readData[0], Is.Not.EqualTo(header));
        }


        
        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_DataOnly(string tempDirectory, string delimiter)
        {
            //data read back will not match the data written due to non-utf8 characters

            dynamic fileReader = PythonEngineManager.FilesBaseReadModule;

            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.NonUTF8TestData_DataOnly(tempDirectory, delimiter);

            // Act - Write data to file
            WriteTestFileBase(fileName, header, data, 0, ";", "utf-8", false, "w"); // csv.QUOTE_MINIMAL

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
            Assert.That(readData.Count, Is.EqualTo(data.Count + headerCount)); // 2 data rows

            // Check for the content
            Assert.That(readData[0], Is.EqualTo(data[0]));
            Assert.That(readData[1], Is.Not.EqualTo(data[1]));
        }

        
        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_HeaderAndData(string tempDirectory, string delimiter)
        {
            //data read back will not match the data written due to non-utf8 characters

            dynamic fileReader = PythonEngineManager.FilesBaseReadModule;

            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.NonUTF8AndDelimitedTestData_HeaderAndData(tempDirectory, delimiter);

            // Act - Write data to file
            WriteTestFileBase(fileName, header, data, 0, ";", "utf-8", false, "w"); // csv.QUOTE_MINIMAL

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
            Assert.That(readData[0], Is.Not.EqualTo(header)); // Non-UTF-8 characters in header
            Assert.That(readData[1], Is.EqualTo(data[0]));
            Assert.That(readData[2], Is.Not.EqualTo(data[1])); // Non-UTF-8 character in data
        }

        
        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_DataOnly(string tempDirectory, string delimiter)
        {
            //data read back will not match the data written due to non-utf8 characters

            dynamic fileReader = PythonEngineManager.FilesBaseReadModule;

            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.NonUTF8AndDelimitedTestData_DataOnly(tempDirectory, delimiter);

            // Act - Write data to file
            WriteTestFileBase(fileName, header, data, 0, ";", "utf-8", false, "w"); // csv.QUOTE_MINIMAL

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
            Assert.That(readData.Count, Is.EqualTo(data.Count + headerCount)); // 2 data rows

            // Check for the content
            Assert.That(readData[0], Is.EqualTo(data[0]));
            Assert.That(readData[1], Is.Not.EqualTo(data[1])); // Non-UTF-8 character in data
        }

        
        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_HeaderOnly(string tempDirectory, string delimiter)
        {
            //data read back will not match the data written due to non-utf8 characters

            dynamic fileReader = PythonEngineManager.FilesBaseReadModule;

            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.NonUTF8AndDelimitedTestData_HeaderOnly(tempDirectory, delimiter);

            // Act - Write data to file
            WriteTestFileBase(fileName, header, data, 0, ";", "utf-8", false, "w"); // csv.QUOTE_MINIMAL

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
            Assert.That(readData.Count, Is.EqualTo(data.Count + headerCount)); // 1 header row

            // Check for the content
            Assert.That(readData[0], Is.Not.EqualTo(header)); // Non-UTF-8 characters in header
        }

        
        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithMaxFieldSizeLimit(string tempDirectory, string delimiter)
        {
            //data read back will not match the data written due to non-utf8 characters

            dynamic fileReader = PythonEngineManager.FilesBaseReadModule;

            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.ArrangeMaxFieldSizeTestData(tempDirectory, delimiter);
            // Act - Write data to file
            WriteTestFileBase(fileName, header, data, 3, ";", "utf-8", false, "w"); // csv.QUOTE_MINIMAL

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

    #endregion WriteAndReadWithoutEncodingReportData
}
