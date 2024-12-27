using PythonTests.Setup;
using System.Text;

namespace PythonTests.UtilitiesTests
{
    public class FilesBaseWriteTests
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
            Assert.That(PythonEngineManager.FilesBaseWriteModule, Is.Not.Null, "file_base_write should be loaded.");
        }

        [Test]
        public void WriteReportData_CreatesReportFile_HeaderAndData()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;
            string delimiter = ";";
            // Arrange
            var (fileName, header, data) = FileBaseTestsData.StandardTestData_HeaderAndData(tempDirectory, delimiter);

            // Act
            var result = fileWriter.write_report_data(
                file_name: fileName,
                header: header,
                data: data,
                write_type: "w",
                enforce_ascii: false,
                encoding: "utf-8",
                bom: null,
                quoting: 3, // csv.QUOTE_NONE
                delimiter: delimiter
            );
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            Assert.That(File.Exists(fileName), Is.True);
            string reportContent = File.ReadAllText(fileName);
            string[] lines = reportContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Determine header count
            int headerCount = header.Count > 0 ? 1 : 0;

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(data.Count + headerCount)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, header)));
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, data[0])));
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, data[1])));
        }

        [Test]
        public void WriteReportData_CreatesReportFile_HeaderOnly()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;
            string delimiter = ";";
            // Arrange
            var (fileName, header, data) = FileBaseTestsData.StandardTestData_HeaderOnly(tempDirectory,delimiter);

            // Act
            var result = fileWriter.write_report_data(
                file_name: fileName,
                header: header,
                data: data,
                write_type: "w",
                enforce_ascii: false,
                encoding: "utf-8",
                bom: null,
                quoting: 3, // csv.QUOTE_NONE
                delimiter: delimiter
            );
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            Assert.That(File.Exists(fileName), Is.True);
            string reportContent = File.ReadAllText(fileName);
            string[] lines = reportContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Determine header count
            int headerCount = header.Count > 0 ? 1 : 0;

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(data.Count + headerCount)); // 1 header row

            // Check for the content
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, header)));
        }

        [Test]
        public void WriteReportData_CreatesReportFile_DataOnly()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;
            string delimiter = ";";
            // Arrange
            var (fileName, header, data) = FileBaseTestsData.StandardTestData_DataOnly(tempDirectory, delimiter);

            // Act
            var result = fileWriter.write_report_data(
                file_name: fileName,
                header: header,
                data: data,
                write_type: "w",
                enforce_ascii: false,
                encoding: "utf-8",
                bom: null,
                quoting: 3, // csv.QUOTE_NONE
                delimiter: delimiter
            );
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            Assert.That(File.Exists(fileName), Is.True);
            string reportContent = File.ReadAllText(fileName);
            string[] lines = reportContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Determine header count
            int headerCount = header.Count > 0 ? 1 : 0;

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(data.Count + headerCount)); // 2 data rows

            // Check for the content
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, data[0])));
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, data[1])));
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithDelimiter_HeaderAndData()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;

            // Arrange
            var (fileName, header, data) = FileBaseTestsData.DelimitedTestData_HeaderAndData(tempDirectory);

            // Act
            var result = fileWriter.write_report_data(
                file_name: fileName,
                header: header,
                data: data,
                write_type: "w",
                enforce_ascii: false,
                encoding: "utf-8",
                bom: null,
                quoting: 0, // csv.QUOTE_MINIMAL
                delimiter: ";"
            );
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            Assert.That(File.Exists(fileName), Is.True);
            string reportContent = File.ReadAllText(fileName, Encoding.GetEncoding("utf-8"));
            string[] lines = reportContent.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Determine header count
            int headerCount = header.Count > 0 ? 1 : 0;

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(data.Count + headerCount)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(reportContent, Does.Contain(string.Join(";", header.Select(d => d.Contains(";") ? $"\"{d}\"" : d)))); //wrap string already containing a delimiter
            Assert.That(reportContent, Does.Contain(string.Join(";", data[0].Select(d => d.Contains(";") ? $"\"{d}\"" : d)))); //wrap string already containing a delimiter
            Assert.That(reportContent, Does.Contain(string.Join(";", data[1].Select(d => d.Contains(";") ? $"\"{d}\"" : d)))); //wrap string already containing a delimiter
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithDelimiter_DataOnly()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;

            // Arrange
            var (fileName, header, data) = FileBaseTestsData.DelimitedTestData_DataOnly(tempDirectory);

            // Act
            var result = fileWriter.write_report_data(
                file_name: fileName,
                header: header,
                data: data,
                write_type: "w",
                enforce_ascii: false,
                encoding: "utf-8",
                bom: null,
                quoting: 0, // csv.QUOTE_MINIMAL
                delimiter: ";"
            );
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            Assert.That(File.Exists(fileName), Is.True);
            string reportContent = File.ReadAllText(fileName, Encoding.GetEncoding("utf-8"));
            string[] lines = reportContent.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Determine header count
            int headerCount = header.Count > 0 ? 1 : 0;

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(data.Count + headerCount)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(reportContent, Does.Contain(string.Join(";", header.Select(d => d.Contains(";") ? $"\"{d}\"" : d)))); //wrap string already containing a delimiter
            Assert.That(reportContent, Does.Contain(string.Join(";", data[0].Select(d => d.Contains(";") ? $"\"{d}\"" : d)))); //wrap string already containing a delimiter
            Assert.That(reportContent, Does.Contain(string.Join(";", data[1].Select(d => d.Contains(";") ? $"\"{d}\"" : d)))); //wrap string already containing a delimiter
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithDelimiter_DataOnly()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;
            string delimiter = ";";
            // Arrange
            var (fileName, header, data) = FileBaseTestsData.DelimitedTestData_DataOnly(tempDirectory, delimiter);
            
            // Act
            var result = fileWriter.write_report_data(
                file_name: fileName,
                header: header,
                data: data,
                write_type: "w",
                enforce_ascii: false,
                encoding: "utf-8",
                bom: null,
                quoting: 0, // csv.QUOTE_MINIMAL
                delimiter: delimiter
            );
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            Assert.That(File.Exists(fileName), Is.True);
            string reportContent = File.ReadAllText(fileName);
            string[] lines = reportContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Determine header count
            int headerCount = header.Count > 0 ? 1 : 0;

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(data.Count + headerCount)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, header)));
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, data[0].Select(d => d.Contains(delimiter) ? $"\"{d}\"" : d)))); //wrap string already containing a ;
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, data[1].Select(d => d.Contains(delimiter) ? $"\"{d}\"" : d)))); //wrap string already containing a ;
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithDelimiter_HeaderOnly()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;
            string delimiter = ";";
            // Arrange
            var (fileName, header, data) = FileBaseTestsData.DelimitedTestData_HeaderOnly(tempDirectory,delimiter);
            
            // Act
            var result = fileWriter.write_report_data(
                file_name: fileName,
                header: header,
                data: data,
                write_type: "w",
                enforce_ascii: false,
                encoding: "utf-8",
                bom: null,
                quoting: 0, // csv.QUOTE_MINIMAL
                delimiter: delimiter
            );
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            Assert.That(File.Exists(fileName), Is.True);
            string reportContent = File.ReadAllText(fileName);
            string[] lines = reportContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Determine header count
            int headerCount = header.Count > 0 ? 1 : 0;

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(data.Count + headerCount)); // 1 header row

            // Check for the content
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, header.Select(d => d.Contains(delimiter) ? $"\"{d}\"" : d)))); //wrap string already containing a ;
        }



        [Test]
        public void WriteReportData_CreatesReportFileWithNonUtf8_HeaderAndData()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;
            string delimiter = ";";
            // Arrange
            var (fileName, header, data) = FileBaseTestsData.NonUTF8TestData_HeaderAndData(tempDirectory);

            // Act
            var result = fileWriter.write_report_data(
                file_name: fileName,
                header: header,
                data: data,
                write_type: "w",
                enforce_ascii: false,
                encoding: "utf-8", // Using a different encoding
                bom: null,
                quoting: 3, // csv.QUOTE_NONE
                delimiter: delimiter
            );
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            Assert.That(File.Exists(fileName), Is.True);
            string reportContent = File.ReadAllText(fileName, Encoding.GetEncoding("utf-8"));
            string[] lines = reportContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Determine header count
            int headerCount = header.Count > 0 ? 1 : 0;

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(data.Count + headerCount)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(reportContent, Does.Contain(string.Join(";", header.Select(d => d.Contains(";") ? $"\"{d}\"" : d)))); //wrap string already containing a and Non-UTF-8 character should be preserved
            Assert.That(reportContent, Does.Contain(string.Join(";", data[0].Select(d => d.Contains(";") ? $"\"{d}\"" : d))));
            Assert.That(reportContent, Does.Contain(string.Join(";", data[1].Select(d => d.Contains(";") ? $"\"{d}\"" : d)))); //wrap string already containing a and Non-UTF-8 character should be preserved
        }


        [Test]
        public void WriteReportData_CreatesReportFileWithNonUtf8_HeaderOnly()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;

            // Arrange
            var (fileName, header, data) = FileBaseTestsData.NonUTF8TestData_HeaderOnly(tempDirectory);

            // Act
            var result = fileWriter.write_report_data(
                file_name: fileName,
                header: header,
                data: data,
                write_type: "w",
                enforce_ascii: false,
                encoding: "utf-8", // Using a different encoding
                bom: null,
                quoting: 3, // csv.QUOTE_NONE
                delimiter: ";"
            );
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            Assert.That(File.Exists(fileName), Is.True);
            string reportContent = File.ReadAllText(fileName, Encoding.GetEncoding("utf-8"));
            string[] lines = reportContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Determine header count
            int headerCount = header.Count > 0 ? 1 : 0;

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(data.Count + headerCount)); // 1 header row

            // Check for the content
            Assert.That(reportContent, Does.Contain(string.Join(";", header))); // Non-UTF-8 characters in header should be preserved
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithNonUtf8_DataOnly()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;
            string delimiter = ";";
            // Arrange
            var (fileName, header, data) = FileBaseTestsData.NonUTF8TestData_DataOnly(tempDirectory, delimiter);

            // Act
            var result = fileWriter.write_report_data(
                file_name: fileName,
                header: header,
                data: data,
                write_type: "w",
                enforce_ascii: false,
                encoding: "utf-8", // Using a different encoding
                bom: null,
                quoting: 3, // csv.QUOTE_NONE
                delimiter: delimiter
            );
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            Assert.That(File.Exists(fileName), Is.True);
            string reportContent = File.ReadAllText(fileName, Encoding.GetEncoding("utf-8"));
            string[] lines = reportContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Determine header count
            int headerCount = header.Count > 0 ? 1 : 0;

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(data.Count + headerCount)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, header)));
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, data[0].Select(d => d.Contains(delimiter) ? $"\"{d}\"" : d)))); //wrap string already containing a ;
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, data[1].Select(d => d.Contains(delimiter) ? $"\"{d}\"" : d)))); //wrap string already containing a and Non-UTF-8 character should be preserved
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithNonUtf8AndDelimiter_HeaderAndData()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;
            string delimiter = ";";
            // Arrange
            var (fileName, header, data) = FileBaseTestsData.NonUTF8AndDelimitedTestData_HeaderAndData(tempDirectory);


            // Act
            var result = fileWriter.write_report_data(
                file_name: fileName,
                header: header,
                data: data,
                write_type: "w",
                enforce_ascii: false,
                encoding: "utf-8", // Using a different encoding
                bom: null,
                quoting: 0, // csv.QUOTE_MINIMAL
                delimiter: delimiter
            );
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            Assert.That(File.Exists(fileName), Is.True);
            string reportContent = File.ReadAllText(fileName, Encoding.GetEncoding("utf-8"));
            string[] lines = reportContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Determine header count
            int headerCount = header.Count > 0 ? 1 : 0;

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(data.Count + headerCount)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(reportContent, Does.Contain(string.Join(";", header.Select(d => d.Contains(";") ? $"\"{d}\"" : d)))); //wrap string already containing a delimiter, Non-UTF-8 characters and delimiter in header should be preserved and quoted
            Assert.That(reportContent, Does.Contain(string.Join(";", data[0])));
            Assert.That(reportContent, Does.Contain(string.Join(";", data[1].Select(d => d.Contains(";") ? $"\"{d}\"" : d)))); //wrap string already containing a and Non-UTF-8 character should be preserved
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithNonUtf8AndDelimiter_DataOnly()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;
            string delimiter = ";";
            // Arrange
            var (fileName, header, data) = FileBaseTestsData.NonUTF8AndDelimitedTestData_DataOnly(tempDirectory);
            

            // Act
            var result = fileWriter.write_report_data(
                file_name: fileName,
                header: header,
                data: data,
                write_type: "w",
                enforce_ascii: false,
                encoding: "utf-8", // Using a different encoding
                bom: null,
                quoting: 0, // csv.QUOTE_MINIMAL
                delimiter: ";"
            );
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            Assert.That(File.Exists(fileName), Is.True);
            string reportContent = File.ReadAllText(fileName, Encoding.GetEncoding("utf-8"));
            string[] lines = reportContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Determine header count
            int headerCount = header.Count > 0 ? 1 : 0;

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(data.Count + headerCount)); // 2 data rows

            // Check for the content
            Assert.That(reportContent, Does.Contain(string.Join(";", data[0])));
            Assert.That(reportContent, Does.Contain(string.Join(";", data[1].Select(d => d.Contains(";") ? $"\"{d}\"" : d)))); //wrap string already containing a and Non-UTF-8 character should be preserved
        }


        [Test]
        public void WriteReportData_CreatesReportFileWithNonUtf8AndDelimiter_HeaderOnly()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;
            string delimiter = ";";
            // Arrange
            var (fileName, header, data) = FileBaseTestsData.NonUTF8AndDelimitedTestData_HeaderOnly(tempDirectory);

            // Act
            var result = fileWriter.write_report_data(
                file_name: fileName,
                header: header,
                data: data,
                write_type: "w",
                enforce_ascii: false,
                encoding: "utf-8", // Using a different encoding
                bom: null,
                quoting: 0, // csv.QUOTE_MINIMAL
                delimiter: delimiter
            );
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            Assert.That(File.Exists(fileName), Is.True);
            string reportContent = File.ReadAllText(fileName, Encoding.GetEncoding("utf-8"));
            string[] lines = reportContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Determine header count
            int headerCount = header.Count > 0 ? 1 : 0;

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(data.Count + headerCount)); // 1 header row

            // Check for the content
            Assert.That(reportContent, Does.Contain(string.Join(";", header.Select(d => d.Contains(";") ? $"\"{d}\"" : d)))); //wrap string already containing a delimiter, Non-UTF-8 characters and delimiter in header should be preserved and quoted
        }


        [Test]
        public void WriteReportData_CreatesReportFileWithNonAsciiDataAndEnforceAscii()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;

            // Arrange
            var (fileName, header, data) = FileBaseTestsData.NonASCIITestData(tempDirectory);

            // Act
            var result = fileWriter.write_report_data(
                file_name: fileName,
                header: header,
                data: data,
                write_type: "w",
                enforce_ascii: true,
                encoding: "utf-8",
                bom: null,
                quoting: 3, // csv.QUOTE_NONE
                delimiter: ";"
            );
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            Assert.That(File.Exists(fileName), Is.True);
            string reportContent = File.ReadAllText(fileName);
            string[] lines = reportContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Determine header count
            int headerCount = header.Count > 0 ? 1 : 0;

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(data.Count + headerCount)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(reportContent, Does.Contain(string.Join(";", header)));
            Assert.That(reportContent, Does.Contain(string.Join(";", data[0].Select(d => FileBaseTestsData.StripNonAscii(d)))));
            Assert.That(reportContent, Does.Contain(string.Join(";", data[1].Select(d => FileBaseTestsData.StripNonAscii(d)))));
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithBOM()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;
            string delimiter = ";";
            // Arrange
            var (fileName, header, data) = FileBaseTestsData.StandardTestData_HeaderAndData(tempDirectory,delimiter);

            dynamic bomValue = PythonEngineManager.BOMValueClass();
            var bom = bomValue.UTF_8;
            
            // Act
            var result = fileWriter.write_report_data(
                file_name: fileName,
                header: header,
                data: data,
                write_type: "w",
                enforce_ascii: false,
                encoding: "utf-8",
                bom: bom,
                quoting: 3, // csv.QUOTE_NONE
                delimiter: delimiter
            );
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            Assert.That(File.Exists(fileName), Is.True);

            // Check if BOM is present at the beginning of the file
            byte[] fileBytes = File.ReadAllBytes(fileName);
            byte[] expected = new byte[] { 0xef, 0xbb, 0xbf }; //utf-8 BOM
            Assert.That(fileBytes.Take(expected.Length).SequenceEqual(expected), Is.True);

            string reportContent = File.ReadAllText(fileName);
            string[] lines = reportContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Determine header count
            int headerCount = header.Count > 0 ? 1 : 0;

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(data.Count + headerCount)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, header)));
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, data[0])));
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, data[1])));
        }
    }
}
