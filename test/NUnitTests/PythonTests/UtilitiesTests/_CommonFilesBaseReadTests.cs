using PythonTests.Setup;
using static IronPython.Runtime.Profiler;

namespace PythonTests.UtilitiesTests
{
    public static class _CommonFilesBaseReadTests
    {
        private static void WriteTestFileBase(
            WriteReportDataDelegate writeReportData,
            Dictionary<string, object> parameters)
        {
            var writeResult = writeReportData(parameters);
            Console.WriteLine(writeResult.message);

            Assert.That(writeResult.status, Is.True);
            Assert.That(File.Exists(parameters["file_name"].ToString()), Is.True);
        }


#region WriteAndReadWithoutEncodingReportData

public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFile_HeaderAndData(
            string tempDirectory, 
            string delimiter, 
            WriteReportDataDelegate writeReportData,
            ReadReportDataDelegate readReportData)
        { 
            
            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.StandardTestData_HeaderAndData(tempDirectory, delimiter);

            // Act - Write data to file
            var parametersWrite = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", false },
                { "encoding", "utf-8" },
                { "bom", null },
                { "quoting", 3 }, //  csv.QUOTE_NONE
                { "delimiter", delimiter }
            };

            // Act - Write data to file
            WriteTestFileBase(writeReportData, parametersWrite); // csv.QUOTE_NONE

            // set up parameters for read
            var parametersRead = new Dictionary<string, object>
            {
                { "file_path", fileName },
                { "increase_max_field_size_limit", false },
                { "delimiter", delimiter }
            };

            // Act - Read data from file
            var readResult = readReportData(parametersRead);
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

        
        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFile_HeaderOnly(
            string tempDirectory,
            string delimiter,
            WriteReportDataDelegate writeReportData,
            ReadReportDataDelegate readReportData)
        {
           
            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.StandardTestData_HeaderOnly(tempDirectory, delimiter);

            // Act - Write data to file
            var parametersWrite = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", false },
                { "encoding", "utf-8" },
                { "bom", null },
                { "quoting", 3 }, //  csv.QUOTE_NONE
                { "delimiter", delimiter }
            };

            // Act - Write data to file
            WriteTestFileBase(writeReportData, parametersWrite); // csv.QUOTE_NONE

            // set up parameters for read
            var parametersRead = new Dictionary<string, object>
            {
                { "file_path", fileName },
                { "increase_max_field_size_limit", false },
                { "delimiter", delimiter }
            };

            // Act - Read data from file
            var readResult = readReportData(parametersRead);
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

        
        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFile_DataOnly(
            string tempDirectory,
            string delimiter,
            WriteReportDataDelegate writeReportData,
            ReadReportDataDelegate readReportData)
        {
           
            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.StandardTestData_DataOnly(tempDirectory, delimiter);

            // Act - Write data to file
            var parametersWrite = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", false },
                { "encoding", "utf-8" },
                { "bom", null },
                { "quoting", 3 }, //  csv.QUOTE_NONE
                { "delimiter", delimiter }
            };

            // Act - Write data to file
            WriteTestFileBase(writeReportData, parametersWrite); // csv.QUOTE_NONE

            // set up parameters for read
            var parametersRead = new Dictionary<string, object>
            {
                { "file_path", fileName },
                { "increase_max_field_size_limit", false },
                { "delimiter", delimiter }
            };

            // Act - Read data from file
            var readResult = readReportData(parametersRead);
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

        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiter_HeaderAndData(
            string tempDirectory,
            string delimiter,
            WriteReportDataDelegate writeReportData,
            ReadReportDataDelegate readReportData)
        {
            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.DelimitedTestData_HeaderAndData(tempDirectory, delimiter);

            // Act - Write data to file
            var parametersWrite = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", false },
                { "encoding", "utf-8" },
                { "bom", null },
                { "quoting", 0 }, //  csv.QUOTE_MINIMAL
                { "delimiter", delimiter }
            };

            // Act - Write data to file
            WriteTestFileBase(writeReportData, parametersWrite); // csv.QUOTE_MINIMAL

            // set up parameters for read
            var parametersRead = new Dictionary<string, object>
            {
                { "file_path", fileName },
                { "increase_max_field_size_limit", false },
                { "delimiter", delimiter }
            };

            // Act - Read data from file
            var readResult = readReportData(parametersRead);
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

        
        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiter_HeaderOnly(
            string tempDirectory,
            string delimiter,
            WriteReportDataDelegate writeReportData,
            ReadReportDataDelegate readReportData)
        {
            
            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.DelimitedTestData_HeaderOnly(tempDirectory, delimiter);

            // Act - Write data to file
            var parametersWrite = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", false },
                { "encoding", "utf-8" },
                { "bom", null },
                { "quoting", 0 }, //  csv.QUOTE_MINIMAL
                { "delimiter", delimiter }
            };

            // Act - Write data to file
            WriteTestFileBase(writeReportData, parametersWrite); // csv.QUOTE_MINIMAL

            // set up parameters for read
            var parametersRead = new Dictionary<string, object>
            {
                { "file_path", fileName },
                { "increase_max_field_size_limit", false },
                { "delimiter", delimiter }
            };

            // Act - Read data from file
            var readResult = readReportData(parametersRead);
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

        
        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiter_DataOnly(
            string tempDirectory,
            string delimiter,
            WriteReportDataDelegate writeReportData,
            ReadReportDataDelegate readReportData)
        {

            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.DelimitedTestData_DataOnly(tempDirectory, delimiter);

            // Act - Write data to file
            var parametersWrite = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", false },
                { "encoding", "utf-8" },
                { "bom", null },
                { "quoting", 0 }, //  csv.QUOTE_MINIMAL
                { "delimiter", delimiter }
            };

            // Act - Write data to file
            WriteTestFileBase(writeReportData, parametersWrite); // csv.QUOTE_MINIMAL

            // set up parameters for read
            var parametersRead = new Dictionary<string, object>
            {
                { "file_path", fileName },
                { "increase_max_field_size_limit", false },
                { "delimiter", delimiter }
            };

            // Act - Read data from file
            var readResult = readReportData(parametersRead);
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

        
        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_HeaderAndData(
            string tempDirectory,
            string delimiter,
            WriteReportDataDelegate writeReportData,
            ReadReportDataDelegate readReportData)
        {

            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.NonUTF8TestData_HeaderAndData(tempDirectory, delimiter);

            // Act - Write data to file
            var parametersWrite = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", false },
                { "encoding", "utf-8" },
                { "bom", null },
                { "quoting", 0 }, //  csv.QUOTE_MINIMAL
                { "delimiter", delimiter }
            };

            // Act - Write data to file
            WriteTestFileBase(writeReportData, parametersWrite); // csv.QUOTE_MINIMAL

            // set up parameters for read
            var parametersRead = new Dictionary<string, object>
            {
                { "file_path", fileName },
                { "increase_max_field_size_limit", false },
                { "delimiter", delimiter }
            };

            // Act - Read data from file
            var readResult = readReportData(parametersRead);
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


        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_HeaderOnly(
            string tempDirectory,
            string delimiter,
            WriteReportDataDelegate writeReportData,
            ReadReportDataDelegate readReportData)
        {

            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.NonUTF8TestData_HeaderOnly(tempDirectory, delimiter);
            // Act - Write data to file
            var parametersWrite = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", false },
                { "encoding", "utf-8" },
                { "bom", null },
                { "quoting", 0 }, //  csv.QUOTE_MINIMAL
                { "delimiter", delimiter }
            };

            // Act - Write data to file
            WriteTestFileBase(writeReportData, parametersWrite); // csv.QUOTE_MINIMAL

            // set up parameters for read
            var parametersRead = new Dictionary<string, object>
            {
                { "file_path", fileName },
                { "increase_max_field_size_limit", false },
                { "delimiter", delimiter }
            };

            // Act - Read data from file
            var readResult = readReportData(parametersRead);
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


        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithNonUtf8_DataOnly(
            string tempDirectory,
            string delimiter,
            WriteReportDataDelegate writeReportData,
            ReadReportDataDelegate readReportData)
        {

            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.NonUTF8TestData_DataOnly(tempDirectory, delimiter);
            // Act - Write data to file
            var parametersWrite = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", false },
                { "encoding", "utf-8" },
                { "bom", null },
                { "quoting", 0 }, //  csv.QUOTE_MINIMAL
                { "delimiter", delimiter }
            };

            // Act - Write data to file
            WriteTestFileBase(writeReportData, parametersWrite); // csv.QUOTE_MINIMAL

            // set up parameters for read
            var parametersRead = new Dictionary<string, object>
            {
                { "file_path", fileName },
                { "increase_max_field_size_limit", false },
                { "delimiter", delimiter }
            };

            // Act - Read data from file
            var readResult = readReportData(parametersRead);
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

        
        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_HeaderAndData(
            string tempDirectory,
            string delimiter,
            WriteReportDataDelegate writeReportData,
            ReadReportDataDelegate readReportData)
        {

            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.NonUTF8AndDelimitedTestData_HeaderAndData(tempDirectory, delimiter);
            // Act - Write data to file
            var parametersWrite = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", false },
                { "encoding", "utf-8" },
                { "bom", null },
                { "quoting", 0 }, //  csv.QUOTE_MINIMAL
                { "delimiter", delimiter }
            };

            // Act - Write data to file
            WriteTestFileBase(writeReportData, parametersWrite); // csv.QUOTE_MINIMAL

            // set up parameters for read
            var parametersRead = new Dictionary<string, object>
            {
                { "file_path", fileName },
                { "increase_max_field_size_limit", false },
                { "delimiter", delimiter }
            };

            // Act - Read data from file
            var readResult = readReportData(parametersRead);
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


        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_HeaderOnly(
            string tempDirectory,
            string delimiter,
            WriteReportDataDelegate writeReportData,
            ReadReportDataDelegate readReportData)
        {

            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.NonUTF8AndDelimitedTestData_HeaderOnly(tempDirectory, delimiter);
            // Act - Write data to file
            var parametersWrite = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", false },
                { "encoding", "utf-8" },
                { "bom", null },
                { "quoting", 0 }, //  csv.QUOTE_MINIMAL
                { "delimiter", delimiter }
            };

            // Act - Write data to file
            WriteTestFileBase(writeReportData, parametersWrite); // csv.QUOTE_MINIMAL

            // set up parameters for read
            var parametersRead = new Dictionary<string, object>
            {
                { "file_path", fileName },
                { "increase_max_field_size_limit", false },
                { "delimiter", delimiter }
            };

            // Act - Read data from file
            var readResult = readReportData(parametersRead);
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


        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithDelimiterAndUtf8_DataOnly(
            string tempDirectory,
            string delimiter,
            WriteReportDataDelegate writeReportData,
            ReadReportDataDelegate readReportData)
        {

            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.NonUTF8AndDelimitedTestData_DataOnly(tempDirectory, delimiter);
            
            // Act - Write data to file
            var parametersWrite = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", false },
                { "encoding", "utf-8" },
                { "bom", null },
                { "quoting", 0 }, //  csv.QUOTE_MINIMAL
                { "delimiter", delimiter }
            };

            // Act - Write data to file
            WriteTestFileBase(writeReportData, parametersWrite); // csv.QUOTE_MINIMAL

            // set up parameters for read
            var parametersRead = new Dictionary<string, object>
            {
                { "file_path", fileName },
                { "increase_max_field_size_limit", false },
                { "delimiter", delimiter }
            };

            // Act - Read data from file
            var readResult = readReportData(parametersRead);
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

        
        public static void WriteAndReadWithoutEncodingReportData_CreatesAndReadsReportFileWithMaxFieldSizeLimit_HeaderAndData(
            string tempDirectory,
            string delimiter,
            WriteReportDataDelegate writeReportData,
            ReadReportDataDelegate readReportData)
        {

            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.ArrangeMaxFieldSizeTestData_HeaderAndData(tempDirectory, delimiter);

            // Act - Write data to file
            var parametersWrite = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", false },
                { "encoding", "utf-8" },
                { "bom", null },
                { "quoting", 3 }, //  csv.QUOTE_NONE
                { "delimiter", delimiter }
            };

            // Act - Write data to file
            WriteTestFileBase(writeReportData, parametersWrite); // csv.QUOTE_MINIMAL

            // set up parameters for read
            var parametersRead = new Dictionary<string, object>
            {
                { "file_path", fileName },
                { "increase_max_field_size_limit", true }, // Increase max field size limit
                { "delimiter", delimiter }
            };

            // Act - Read data from file
            var readResult = readReportData(parametersRead);
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
