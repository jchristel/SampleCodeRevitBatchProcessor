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
        public void WriteReportData_CreatesReportFile()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;

            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> { "Header1", "Header2" };
            List<List<string>> data = new List<List<string>>
                {
                    new List<string> { "Value1", "Value2" },
                    new List<string> { "Value3", "Value4" }
                };

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

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(3)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(reportContent, Does.Contain("Header1;Header2"));
            Assert.That(reportContent, Does.Contain("Value1;Value2"));
            Assert.That(reportContent, Does.Contain("Value3;Value4"));
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithHeaderOnly()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;

            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> { "Header1", "Header2" };
            List<List<string>> data = new List<List<string>>(); // No data rows

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

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(1)); // 1 header row

            // Check for the content
            Assert.That(reportContent, Does.Contain("Header1;Header2"));
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithDataOnly()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;

            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string>(); // No header
            List<List<string>> data = new List<List<string>>
            {
                new List<string> { "Value1", "Value2" },
                new List<string> { "Value3", "Value4" }
            };

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

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(2)); // 2 data rows

            // Check for the content
            Assert.That(reportContent, Does.Contain("Value1;Value2"));
            Assert.That(reportContent, Does.Contain("Value3;Value4"));
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithQuotedData()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;

            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> { "Header1", "Header2" };
            List<List<string>> data = new List<List<string>>
            {
                new List<string> { "Value1 ; delim", "Value2" },
                new List<string> { "Value3", "delim ; Value4" }
            };

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
            string reportContent = File.ReadAllText(fileName);
            string[] lines = reportContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(3)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(reportContent, Does.Contain("Header1;Header2"));
            Assert.That(reportContent, Does.Contain("\"Value1 ; delim\";Value2"));
            Assert.That(reportContent, Does.Contain("Value3;\"delim ; Value4\""));
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithHeaderContainingDelimiter()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;

            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> { "Header1;Part1", "Header2;Part2" };
            List<List<string>> data = new List<List<string>>(); // No data rows

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
            string reportContent = File.ReadAllText(fileName);
            string[] lines = reportContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(1)); // 1 header row

            // Check for the content
            Assert.That(reportContent, Does.Contain("\"Header1;Part1\";\"Header2;Part2\""));
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithNonAsciiDataAndEnforceAscii()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;

            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> { "Header1", "Header2" };
            List<List<string>> data = new List<List<string>>
            {
                new List<string> { "Välue1", "Välue2" },
                new List<string> { "Välue3", "Välue4" }
            };

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

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(3)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(reportContent, Does.Contain("Header1;Header2"));
            Assert.That(reportContent, Does.Contain("Vlue1;Vlue2")); // Non-ASCII characters should be removed
            Assert.That(reportContent, Does.Contain("Vlue3;Vlue4")); // Non-ASCII characters should be removed
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithNonUtf8Data()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;

            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> { "Header1", "Header2" };
            List<List<string>> data = new List<List<string>>
            {
                new List<string> { "Value1", "Value2" },
                new List<string> { "Value3", "Välue4" } // Non-UTF-8 character
            };

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

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(3)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(reportContent, Does.Contain("Header1;Header2"));
            Assert.That(reportContent, Does.Contain("Value1;Value2"));
            Assert.That(reportContent, Does.Contain("Value3;Välue4")); // Non-UTF-8 character should be preserved
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithNonUtf8DataAndDelimiterInData()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;

            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> { "Header1", "Header2" };
            List<List<string>> data = new List<List<string>>
    {
        new List<string> { "Value1", "Value2" },
        new List<string> { "Value3", "Välue4;Part" } // Non-UTF-8 character and delimiter in data
    };

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

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(3)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(reportContent, Does.Contain("Header1;Header2"));
            Assert.That(reportContent, Does.Contain("Value1;Value2"));
            Assert.That(reportContent, Does.Contain("Value3;\"Välue4;Part\"")); // Non-UTF-8 character and delimiter in data should be preserved and quoted
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithNonUtf8HeaderAndData()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;

            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> { "Hëader1", "Hëader2" }; // Non-UTF-8 characters in header
            List<List<string>> data = new List<List<string>>
            {
                new List<string> { "Value1", "Value2" },
                new List<string> { "Value3", "Välue4" } // Non-UTF-8 character in data
            };

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

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(3)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(reportContent, Does.Contain("Hëader1;Hëader2")); // Non-UTF-8 characters in header should be preserved
            Assert.That(reportContent, Does.Contain("Value1;Value2"));
            Assert.That(reportContent, Does.Contain("Value3;Välue4")); // Non-UTF-8 character in data should be preserved
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithHeaderAndDataContainingDelimiter()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;

            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> { "Header1;Part1", "Header2;Part2" }; // Header containing delimiter
            List<List<string>> data = new List<List<string>>
    {
        new List<string> { "Value1;Part1", "Value2;Part2" }, // Data containing delimiter
        new List<string> { "Value3;Part3", "Value4;Part4" }  // Data containing delimiter
    };

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

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(3)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(reportContent, Does.Contain("\"Header1;Part1\";\"Header2;Part2\"")); // Header containing delimiter should be quoted
            Assert.That(reportContent, Does.Contain("\"Value1;Part1\";\"Value2;Part2\"")); // Data containing delimiter should be quoted
            Assert.That(reportContent, Does.Contain("\"Value3;Part3\";\"Value4;Part4\"")); // Data containing delimiter should be quoted
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithNonUtf8HeaderOnly()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;

            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> { "Hëader1", "Hëader2" }; // Non-UTF-8 characters in header
            List<List<string>> data = new List<List<string>>(); // No data rows

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

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(1)); // 1 header row

            // Check for the content
            Assert.That(reportContent, Does.Contain("Hëader1;Hëader2")); // Non-UTF-8 characters in header should be preserved
        }

        [Test]
        public void WriteReportData_CreatesReportFileWithNonUtf8HeaderContainingDelimiter()
        {
            dynamic fileWriter = PythonEngineManager.FilesBaseWriteModule;

            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> { "Hëader1;Part1", "Hëader2;Part2" }; // Non-UTF-8 characters and delimiter in header
            List<List<string>> data = new List<List<string>>(); // No data rows

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

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(1)); // 1 header row

            // Check for the content
            Assert.That(reportContent, Does.Contain("\"Hëader1;Part1\";\"Hëader2;Part2\"")); // Non-UTF-8 characters and delimiter in header should be preserved and quoted
        }
    }
}
