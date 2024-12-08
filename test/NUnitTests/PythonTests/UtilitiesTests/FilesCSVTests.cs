using PythonTests.Setup;

namespace PythonTests.UtilitiesTests
{
    public class FilesCSVTests
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
            Assert.That(PythonEngineManager.FilesCSVModule, Is.Not.Null, "file_csv should be loaded.");
        }

        [Test]
        public void WriteReportDataAsCsv_CreatesCsvFileWithHeaderOnly()
        {
            dynamic filesCSV = PythonEngineManager.FilesCSVModule;

            // Arrange
            string fileName = Path.Combine(tempDirectory, "report_header_only.csv");
            List<string> header = new List<string> { "Header1", "Header2" };
            List<List<string>> data = new List<List<string>>(); // No data rows

            // Act
            var result = filesCSV.write_report_data_as_csv(file_name: fileName, header: header, data: data);

            // Assert
            Assert.That(File.Exists(fileName), Is.True);
            string combinedContent = File.ReadAllText(fileName);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' });

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(1)); // Only 1 header row

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Header1,Header2"));
        }

        [Test]
        public void WriteReportDataAsCsv_CreatesCsvFileWithOutHeader()
        {
            dynamic filesCSV = PythonEngineManager.FilesCSVModule;

            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string>(); // No header row
            List<List<string>> data = new List<List<string>>
                {
                    new List<string> { "Value1", "Value2" },
                    new List<string> { "Value3", "Value4" },
                    new List<string> { "Value5", "Value6" }
                };

            // Act
            var result = filesCSV.write_report_data_as_csv(file_name: fileName, header: header, data: data);

            // Assert
            Assert.That(File.Exists(fileName), Is.True);
            string combinedContent = File.ReadAllText(fileName);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' });

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(3)); // 0 header row + 3 data rows

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Value1,Value2"));
            Assert.That(combinedContent, Does.Contain("Value3,Value4"));
            Assert.That(combinedContent, Does.Contain("Value5,Value6"));
        }

        [Test]
        public void WriteReportDataAsCsv_CreatesCsvFile()
        {
            dynamic filesCSV = PythonEngineManager.FilesCSVModule;

            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> { "Header1", "Header2" };
            List<List<string>> data = new List<List<string>>
                {
                    new List<string> { "Value1", "Value2" },
                    new List<string> { "Value3", "Value4" }
                };

            // Act
            var result = filesCSV.write_report_data_as_csv(file_name: fileName, header: header, data: data);

            // Assert
            Assert.That(File.Exists(fileName), Is.True);
            string combinedContent = File.ReadAllText(fileName);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' });

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(3)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Header1,Header2"));
            Assert.That(combinedContent, Does.Contain("Value1,Value2"));
            Assert.That(combinedContent, Does.Contain("Value3,Value4"));
        }

        [Test]
        public void WriteReportDataAsCsv_CreatesCsvFileWithNonAsciiData()
        {
            dynamic filesCSV = PythonEngineManager.FilesCSVModule;

            // Arrange
            string fileName = Path.Combine(tempDirectory, "report_non_ascii.csv");
            List<string> header = new List<string> { "Header1", "Header2" };
            List<List<string>> data = new List<List<string>>
            {
                new List<string> { "Välue1", "Välue2" },
                new List<string> { "Välue3", "Välue4" }
            };

            // Act
            var result = filesCSV.write_report_data_as_csv(file_name: fileName, header: header, data: data, enforce_ascii:true);

            // Assert
            Assert.That(File.Exists(fileName), Is.True);
            string combinedContent = File.ReadAllText(fileName);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' });
            foreach (var line in lines)
            {
                Console.WriteLine("{"+line);
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(3)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Header1,Header2"));
            Assert.That(combinedContent, Does.Contain("Vlue1,Vlue2")); // Non-ASCII characters should be removed when converted to ASCII
            Assert.That(combinedContent, Does.Contain("Vlue3,Vlue4")); // Non-ASCII characters should be removed when converted to ASCII
        }

        [Test]
        public void WriteReportDataAsCsv_CreatesCsvFileWithNonUtf8Data()
        {
            dynamic filesCSV = PythonEngineManager.FilesCSVModule;

            // Register the code page provider to support "latin-1" encoding
            System.Text.Encoding.RegisterProvider(System.Text.CodePagesEncodingProvider.Instance);

            // Arrange
            string fileName = Path.Combine(tempDirectory, "report_non_utf8.csv");
            List<string> header = new List<string> { "Header1", "Header2" };
            List<List<string>> data = new List<List<string>>
            {
                new List<string> { "Välue1", "Välue2" },
                new List<string> { "Välue3", "Välue4" }
            };

            // Act
            var result = filesCSV.write_report_data_as_csv(file_name: fileName, header: header, data: data, encoding: "latin-1");

            // Assert
            Assert.That(File.Exists(fileName), Is.True);
            string combinedContent = File.ReadAllText(fileName, System.Text.Encoding.Latin1);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' });
            foreach (var line in lines)
            {
                Console.WriteLine("{" + line);
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(3)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Header1,Header2"));
            Assert.That(combinedContent, Does.Contain("Välue1,Välue2")); // Non-UTF-8 characters should be preserved
            Assert.That(combinedContent, Does.Contain("Välue3,Välue4")); // Non-UTF-8 characters should be preserved
        }

        [Test]
        public void WriteReportDataAsCsv_CreatesCsvFileWithNonUtf8InputAndUtf8Encoding()
        {
            dynamic filesCSV = PythonEngineManager.FilesCSVModule;

            // Arrange
            string fileName = Path.Combine(tempDirectory, "report_non_utf8_input_utf8_encoding.csv");
            List<string> header = new List<string> { "Header1", "Header2" };
            List<List<string>> data = new List<List<string>>
            {
                new List<string> { "Välue1", "Välue2" },
                new List<string> { "Välue3", "Välue4" }
            };

            // Act
            var result = filesCSV.write_report_data_as_csv(file_name: fileName, header: header, data: data, encoding: "utf-8");

            // Assert
            Assert.That(File.Exists(fileName), Is.True);
            string combinedContent = File.ReadAllText(fileName, System.Text.Encoding.UTF8);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' });
            foreach (var line in lines)
            {
                Console.WriteLine("{" + line);
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(3)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Header1,Header2"));
            Assert.That(combinedContent, Does.Contain("Välue1,Välue2")); // Non-UTF-8 characters should be preserved
            Assert.That(combinedContent, Does.Contain("Välue3,Välue4")); // Non-UTF-8 characters should be preserved
        }

    }
}
