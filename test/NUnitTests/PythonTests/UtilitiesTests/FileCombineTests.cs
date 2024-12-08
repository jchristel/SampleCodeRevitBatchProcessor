using PythonTests.Setup;


namespace PythonTests.UtilitiesTests
{
    public class FileCombineTests
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
            Assert.That(PythonEngineManager.FileCombineModule, Is.Not.Null, "file_combine should be loaded.");
        }

        [Test]
        public void CombineFiles_CreatesCombinedFile()
        {
            dynamic fileCombiner = PythonEngineManager.FileCombineModule;

            // Arrange
            string file1 = Path.Combine(tempDirectory, "file1.txt");
            string file2 = Path.Combine(tempDirectory, "file2.txt");
            File.WriteAllText(file1, "Header1,Header2\nValue1,Value2\n");
            File.WriteAllText(file2, "Header1,Header2\nValue3,Value4\n");

            // Act
            var result = fileCombiner.combine_files(folder_path: tempDirectory);
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            string combinedFilePath = Path.Combine(tempDirectory, "result.txt"); // Default output file name
            Assert.That(File.Exists(combinedFilePath), Is.True);
            string combinedContent = File.ReadAllText(combinedFilePath);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(3)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Header1,Header2"));
            Assert.That(combinedContent, Does.Contain("Value1,Value2"));
            Assert.That(combinedContent, Does.Contain("Value3,Value4"));
        }

        [Test]
        public void CombineFiles_CreatesCombinedCsvFile()
        {
            dynamic fileCombiner = PythonEngineManager.FileCombineModule;

            // Arrange
            string file1 = Path.Combine(tempDirectory, "file1.csv");
            string file2 = Path.Combine(tempDirectory, "file2.csv");
            File.WriteAllText(file1, "Header1,Header2\nValue1,Value2\nValue5,Value6\n");
            File.WriteAllText(file2, "Header1,Header2\nValue3,Value4\nValue7,Value8\n");

            // Act
            var result = fileCombiner.combine_files(folder_path: tempDirectory, file_extension:".csv",output_file_name: "combined.csv");

            // Assert
            string combinedFilePath = Path.Combine(tempDirectory, "combined.csv");
            Assert.That(File.Exists(combinedFilePath), Is.True);
            string combinedContent = File.ReadAllText(combinedFilePath);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(5)); // 1 header row + 4 data rows

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Header1,Header2"));
            Assert.That(combinedContent, Does.Contain("Value1,Value2"));
            Assert.That(combinedContent, Does.Contain("Value3,Value4"));
            Assert.That(combinedContent, Does.Contain("Value5,Value6"));
            Assert.That(combinedContent, Does.Contain("Value7,Value8"));
        }

        [Test]
        public void CombineFiles_CreatesCombinedTabSeparatedFile()
        {
            dynamic fileCombiner = PythonEngineManager.FileCombineModule;

            // Arrange
            string file1 = Path.Combine(tempDirectory, "file1.txt");
            string file2 = Path.Combine(tempDirectory, "file2.txt");
            File.WriteAllText(file1, "Header1\tHeader2\nValue1\tValue2\n");
            File.WriteAllText(file2, "Header1\tHeader2\nValue3\tValue4\n");

            // Act
            var result = fileCombiner.combine_files(folder_path: tempDirectory, delimiter: "\t");
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            string combinedFilePath = Path.Combine(tempDirectory, "result.txt"); // Default output file name
            Assert.That(File.Exists(combinedFilePath), Is.True);
            string combinedContent = File.ReadAllText(combinedFilePath);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(3)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Header1\tHeader2"));
            Assert.That(combinedContent, Does.Contain("Value1\tValue2"));
            Assert.That(combinedContent, Does.Contain("Value3\tValue4"));
        }

        [Test]
        public void AppendToFile_AppendsContent()
        {
            dynamic fileCombiner = PythonEngineManager.FileCombineModule;

            // Arrange
            string sourceFile = Path.Combine(tempDirectory, "source.txt");
            string appendFile = Path.Combine(tempDirectory, "append.txt");
            File.WriteAllText(sourceFile, "Header1,Header2\nValue1,Value2\n");
            File.WriteAllText(appendFile, "Header1,Header2\nValue3,Value4\n");

            // Act
            var result = fileCombiner.append_to_file(sourceFile, appendFile, true);

            // Assert
            Console.WriteLine(result.message);
            Assert.That(result.status, Is.True);
            string combinedContent = File.ReadAllText(sourceFile);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(3)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Value1,Value2"));
            Assert.That(combinedContent, Does.Contain("Value3,Value4"));
        }

        [Test]
        public void AppendToFile_AppendsCsvContent()
        {
            dynamic fileCombiner = PythonEngineManager.FileCombineModule;

            // Arrange
            string sourceFile = Path.Combine(tempDirectory, "source.csv");
            string appendFile = Path.Combine(tempDirectory, "append.csv");
            File.WriteAllText(sourceFile, "Header1,Header2\nValue1,Value2\n");
            File.WriteAllText(appendFile, "Header1,Header2\nValue3,Value4\n");

            // Act
            var result = fileCombiner.append_to_file(sourceFile, appendFile, true);

            // Assert
            Console.WriteLine(result.message);
            Assert.That(result.status, Is.True);
            string combinedContent = File.ReadAllText(sourceFile);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(3)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Value1,Value2"));
            Assert.That(combinedContent, Does.Contain("Value3,Value4"));
        }

        [Test]
        public void AppendToFile_AppendsTabSeparatedContent()
        {
            dynamic fileCombiner = PythonEngineManager.FileCombineModule;

            // Arrange
            string sourceFile = Path.Combine(tempDirectory, "source.txt");
            string appendFile = Path.Combine(tempDirectory, "append.txt");
            File.WriteAllText(sourceFile, "Header1\tHeader2\nValue1\tValue2\n");
            File.WriteAllText(appendFile, "Header1\tHeader2\nValue3\tValue4\n");

            // Act
            var result = fileCombiner.append_to_file(sourceFile, appendFile, true);

            // Assert
            Console.WriteLine(result.message);
            Assert.That(result.status, Is.True);
            string combinedContent = File.ReadAllText(sourceFile);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(3)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Value1\tValue2"));
            Assert.That(combinedContent, Does.Contain("Value3\tValue4"));
        }

        [Test]
        public void CombineFilesHeaderIndependent_CreatesCombinedFile()
        {
            dynamic fileCombiner = PythonEngineManager.FileCombineModule;

            // Arrange
            string file1 = Path.Combine(tempDirectory, "file1.txt");
            string file2 = Path.Combine(tempDirectory, "file2.txt");
            File.WriteAllText(file1, "Header1\tHeader2\nValue1\tValue2\n");
            File.WriteAllText(file2, "Header3\tHeader4\nValue3\tValue4\n");

            // Act
            fileCombiner.combine_files_header_independent(tempDirectory, "", "", ".txt", "combined.txt");

            // Assert
            string combinedFilePath = Path.Combine(tempDirectory, "combined.txt");
            Assert.That(File.Exists(combinedFilePath), Is.True);
            string combinedContent = File.ReadAllText(combinedFilePath);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(3)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Header1"));
            Assert.That(combinedContent, Does.Contain("Header2"));
            Assert.That(combinedContent, Does.Contain("Header3"));
            Assert.That(combinedContent, Does.Contain("Header4"));
            Assert.That(combinedContent, Does.Contain("Value1"));
            Assert.That(combinedContent, Does.Contain("Value2"));
            Assert.That(combinedContent, Does.Contain("Value3"));
            Assert.That(combinedContent, Does.Contain("Value4"));
        }

        [Test]
        public void CombineFilesCsvHeaderIndependent_CreatesCombinedFile()
        {
            dynamic fileCombiner = PythonEngineManager.FileCombineModule;

            // Arrange
            string file1 = Path.Combine(tempDirectory, "file1.csv");
            string file2 = Path.Combine(tempDirectory, "file2.csv");
            File.WriteAllText(file1, "Header1,Header2\nValue1,Value2\n");
            File.WriteAllText(file2, "Header3,Header4\nValue3,Value4\n");

            // Act
            fileCombiner.combine_files_csv_header_independent(tempDirectory, "", "", ".csv", "combined.csv");

            // Assert
            string combinedFilePath = Path.Combine(tempDirectory, "combined.csv");
            Assert.That(File.Exists(combinedFilePath), Is.True);
            string combinedContent = File.ReadAllText(combinedFilePath);

            Console.WriteLine(combinedContent);

            string[] lines = combinedContent.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(3)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Header1"));
            Assert.That(combinedContent, Does.Contain("Header2"));
            Assert.That(combinedContent, Does.Contain("Header3"));
            Assert.That(combinedContent, Does.Contain("Header4"));
            Assert.That(combinedContent, Does.Contain("Value1"));
            Assert.That(combinedContent, Does.Contain("Value2"));
            Assert.That(combinedContent, Does.Contain("Value3"));
            Assert.That(combinedContent, Does.Contain("Value4"));
        }

        [Test]
        public void CombineFilesJson_CreatesCombinedFile()
        {
            dynamic fileCombiner = PythonEngineManager.FileCombineModule;

            // Arrange
            string file1 = Path.Combine(tempDirectory, "file1.json");
            string file2 = Path.Combine(tempDirectory, "file2.json");
            File.WriteAllText(file1, "{\"key1\": \"value1\"}");
            File.WriteAllText(file2, "{\"key2\": \"value2\"}");

            // Act
            bool result = fileCombiner.combine_files_json(tempDirectory, "", "", ".json", "combined.json");

            // Assert
            Assert.That(result, Is.True);
            string combinedFilePath = Path.Combine(tempDirectory, "combined.json");
            Assert.That(File.Exists(combinedFilePath), Is.True);
            string combinedContent = File.ReadAllText(combinedFilePath);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(1)); // 1 data row (one long json string

            // Check for the content
            Assert.That(combinedContent, Does.Contain("\"key1\": \"value1\""));
            Assert.That(combinedContent, Does.Contain("\"key2\": \"value2\""));
        }
    }
}
