using PythonTests.Setup;
using System.Collections.Generic;


namespace PythonTests.UtilitiesTests
{
    public class FilesBaseCombineTests
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
            Assert.That(PythonEngineManager.FilesBaseCombineModule, Is.Not.Null, "file_combine should be loaded.");
        }

        [Test]
        public void CombineFiles_CreatesCombinedFile()
        {
            dynamic fileCombiner = PythonEngineManager.FilesBaseCombineModule;

            // Arrange
            string file1 = Path.Combine(tempDirectory, "file1.txt");
            string file2 = Path.Combine(tempDirectory, "file2.txt");
            File.WriteAllText(file1, "Header1;Header2\nValue1;Value2\n");
            File.WriteAllText(file2, "Header1;Header2\nValue3;Value4\n");

            // Act
            var result = fileCombiner.combine_files(folder_path: tempDirectory, file_prefix: "", file_suffix: "", file_extension: ".txt", output_file_name: "result.txt", delimiter: ";");
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            string combinedFilePath = Path.Combine(tempDirectory, "result.txt"); // Default output file name
            Assert.That(File.Exists(combinedFilePath), Is.True);
            string combinedContent = File.ReadAllText(combinedFilePath);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(3)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Header1;Header2"));
            Assert.That(combinedContent, Does.Contain("Value1;Value2"));
            Assert.That(combinedContent, Does.Contain("Value3;Value4"));
        }

        [Test]
        public void CombineFiles_CreatesCombinedFileWithFourFilesAndMultipleRows()
        {
            dynamic fileCombiner = PythonEngineManager.FilesBaseCombineModule;

            // Arrange
            string file1 = Path.Combine(tempDirectory, "file1.txt");
            string file2 = Path.Combine(tempDirectory, "file2.txt");
            string file3 = Path.Combine(tempDirectory, "file3.txt");
            string file4 = Path.Combine(tempDirectory, "file4.txt");
            File.WriteAllText(file1, "Header1;Header2\nValue1;Value2\nValue9;Value10\n");
            File.WriteAllText(file2, "Header1;Header2\nValue3;Value4\nValue11;Value12\n");
            File.WriteAllText(file3, "Header1;Header2\nValue5;Value6\nValue13;Value14\n");
            File.WriteAllText(file4, "Header1;Header2\nValue7;Value8\nValue15;Value16\n");

            // Act
            var result = fileCombiner.combine_files(folder_path: tempDirectory, file_prefix: "", file_suffix: "", file_extension: ".txt", output_file_name: "result.txt", delimiter: ";");
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            string combinedFilePath = Path.Combine(tempDirectory, "result.txt"); // Default output file name
            Assert.That(File.Exists(combinedFilePath), Is.True);
            string combinedContent = File.ReadAllText(combinedFilePath);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(9)); // 1 header row + 8 data rows

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Header1;Header2"));
            Assert.That(combinedContent, Does.Contain("Value1;Value2"));
            Assert.That(combinedContent, Does.Contain("Value3;Value4"));
            Assert.That(combinedContent, Does.Contain("Value5;Value6"));
            Assert.That(combinedContent, Does.Contain("Value7;Value8"));
            Assert.That(combinedContent, Does.Contain("Value9;Value10"));
            Assert.That(combinedContent, Does.Contain("Value11;Value12"));
            Assert.That(combinedContent, Does.Contain("Value13;Value14"));
            Assert.That(combinedContent, Does.Contain("Value15;Value16"));
        }

        [Test]
        public void CombineFiles_CreatesCombinedFileWithSuffix()
        {
            dynamic fileCombiner = PythonEngineManager.FilesBaseCombineModule;

            // Arrange
            string file1 = Path.Combine(tempDirectory, "file1_mich gefragt.txt");
            string file2 = Path.Combine(tempDirectory, "file2_mich gefragt.txt");
            string file3 = Path.Combine(tempDirectory, "file3_mich gefragt.txt");
            string file4 = Path.Combine(tempDirectory, "file4.txt");
            File.WriteAllText(file1, "Header1;Header2\nValue1;Value2\nValue9;Value10\n");
            File.WriteAllText(file2, "Header1;Header2\nValue3;Value4\nValue11;Value12\n");
            File.WriteAllText(file3, "Header1;Header2\nValue5;Value6\nValue13;Value14\n");
            File.WriteAllText(file4, "Header1;Header2\nValue7;Value8\nValue15;Value16\n");

            // Act
            var result = fileCombiner.combine_files(folder_path: tempDirectory, file_prefix: "", file_suffix: "mich gefragt", file_extension: ".txt", output_file_name: "result.txt", delimiter: ";");
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            string combinedFilePath = Path.Combine(tempDirectory, "result.txt"); // Default output file name
            Assert.That(File.Exists(combinedFilePath), Is.True);
            string combinedContent = File.ReadAllText(combinedFilePath);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(7)); // 1 header row + 6 data rows (3 files with suffix)

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Header1;Header2"));
            Assert.That(combinedContent, Does.Contain("Value1;Value2"));
            Assert.That(combinedContent, Does.Contain("Value3;Value4"));
            Assert.That(combinedContent, Does.Contain("Value5;Value6"));
            Assert.That(combinedContent, Does.Contain("Value9;Value10"));
            Assert.That(combinedContent, Does.Contain("Value11;Value12"));
            Assert.That(combinedContent, Does.Contain("Value13;Value14"));
            Assert.That(combinedContent, Does.Not.Contain("Value7;Value8"));
            Assert.That(combinedContent, Does.Not.Contain("Value15;Value16"));
        }

        [Test]
        public void CombineFiles_CreatesCombinedFileWithPrefix()
        {
            dynamic fileCombiner = PythonEngineManager.FilesBaseCombineModule;

            // Arrange
            string file1 = Path.Combine(tempDirectory, "duHast_file1.txt");
            string file2 = Path.Combine(tempDirectory, "duHast_file2.txt");
            string file3 = Path.Combine(tempDirectory, "duHast_file3.txt");
            string file4 = Path.Combine(tempDirectory, "file4.txt");
            File.WriteAllText(file1, "Header1;Header2\nValue1;Value2\nValue9;Value10\n");
            File.WriteAllText(file2, "Header1;Header2\nValue3;Value4\nValue11;Value12\n");
            File.WriteAllText(file3, "Header1;Header2\nValue5;Value6\nValue13;Value14\n");
            File.WriteAllText(file4, "Header1;Header2\nValue7;Value8\nValue15;Value16\n");

            // Act
            var result = fileCombiner.combine_files(folder_path: tempDirectory, file_prefix: "duHast", file_suffix: "", file_extension: ".txt", output_file_name: "result.txt", delimiter: ";");
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            string combinedFilePath = Path.Combine(tempDirectory, "result.txt"); // Default output file name
            Assert.That(File.Exists(combinedFilePath), Is.True);
            string combinedContent = File.ReadAllText(combinedFilePath);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(7)); // 1 header row + 6 data rows (3 files with prefix)

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Header1;Header2"));
            Assert.That(combinedContent, Does.Contain("Value1;Value2"));
            Assert.That(combinedContent, Does.Contain("Value3;Value4"));
            Assert.That(combinedContent, Does.Contain("Value5;Value6"));
            Assert.That(combinedContent, Does.Contain("Value9;Value10"));
            Assert.That(combinedContent, Does.Contain("Value11;Value12"));
            Assert.That(combinedContent, Does.Contain("Value13;Value14"));
            Assert.That(combinedContent, Does.Not.Contain("Value7;Value8"));
            Assert.That(combinedContent, Does.Not.Contain("Value15;Value16"));
        }
        [Test]
        public void CombineFiles_CreatesCombinedFileWithPrefixAndSuffix()
        {
            dynamic fileCombiner = PythonEngineManager.FilesBaseCombineModule;

            // Arrange
            string file1 = Path.Combine(tempDirectory, "duHast_file1_mich gefragt.txt");
            string file2 = Path.Combine(tempDirectory, "duHast_file2_mich gefragt.txt");
            string file3 = Path.Combine(tempDirectory, "file3_mich gefragt.txt");
            string file4 = Path.Combine(tempDirectory, "file4.txt");
            File.WriteAllText(file1, "Header1;Header2\nValue1;Value2\nValue9;Value10\n");
            File.WriteAllText(file2, "Header1;Header2\nValue3;Value4\nValue11;Value12\n");
            File.WriteAllText(file3, "Header1;Header2\nValue5;Value6\nValue13;Value14\n");
            File.WriteAllText(file4, "Header1;Header2\nValue7;Value8\nValue15;Value16\n");

            // Act
            var result = fileCombiner.combine_files(folder_path: tempDirectory, file_prefix: "duHast", file_suffix: "mich gefragt", file_extension: ".txt", output_file_name: "result.txt", delimiter: ";");
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            string combinedFilePath = Path.Combine(tempDirectory, "result.txt"); // Default output file name
            Assert.That(File.Exists(combinedFilePath), Is.True);
            string combinedContent = File.ReadAllText(combinedFilePath);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(5)); // 1 header row + 4 data rows (2 files with suffix and prefix matching filters provided)

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Header1;Header2"));
            Assert.That(combinedContent, Does.Contain("Value1;Value2"));
            Assert.That(combinedContent, Does.Contain("Value3;Value4"));
            Assert.That(combinedContent, Does.Contain("Value9;Value10"));
            Assert.That(combinedContent, Does.Contain("Value11;Value12"));
        }

        [Test]
        public void CombineFiles_CreatesCombinedFileWithDifferentExtension()
        {
            dynamic fileCombiner = PythonEngineManager.FilesBaseCombineModule;

            // Arrange
            string file1 = Path.Combine(tempDirectory, "file1.dert");
            string file2 = Path.Combine(tempDirectory, "file2.dert");
            string file3 = Path.Combine(tempDirectory, "file3.dert");
            string file4 = Path.Combine(tempDirectory, "file4.txt");
            File.WriteAllText(file1, "Header1;Header2\nValue1;Value2\nValue9;Value10\n");
            File.WriteAllText(file2, "Header1;Header2\nValue3;Value4\nValue11;Value12\n");
            File.WriteAllText(file3, "Header1;Header2\nValue5;Value6\nValue13;Value14\n");
            File.WriteAllText(file4, "Header1;Header2\nValue7;Value8\nValue15;Value16\n");

            // Act
            var result = fileCombiner.combine_files(folder_path: tempDirectory, file_prefix: "", file_suffix: "", file_extension: ".dert", output_file_name: "result.txt", delimiter: ";");
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            string combinedFilePath = Path.Combine(tempDirectory, "result.txt"); // Default output file name
            Assert.That(File.Exists(combinedFilePath), Is.True);
            string combinedContent = File.ReadAllText(combinedFilePath);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(7)); // 1 header row + 6 data rows (3 files with .dert extension)

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Header1;Header2"));
            Assert.That(combinedContent, Does.Contain("Value1;Value2"));
            Assert.That(combinedContent, Does.Contain("Value3;Value4"));
            Assert.That(combinedContent, Does.Contain("Value5;Value6"));
            Assert.That(combinedContent, Does.Contain("Value9;Value10"));
            Assert.That(combinedContent, Does.Contain("Value11;Value12"));
            Assert.That(combinedContent, Does.Contain("Value13;Value14"));
            Assert.That(combinedContent, Does.Not.Contain("Value7;Value8"));
            Assert.That(combinedContent, Does.Not.Contain("Value15;Value16"));
        }

        [Test]
        public void CombineFiles_CreatesCombinedFileWithMissingNewline()
        {
            dynamic fileCombiner = PythonEngineManager.FilesBaseCombineModule;

            // Arrange
            string file1 = Path.Combine(tempDirectory, "file1.txt");
            string file2 = Path.Combine(tempDirectory, "file2.txt");
            string file3 = Path.Combine(tempDirectory, "file3.txt");
            string file4 = Path.Combine(tempDirectory, "file4.txt");
            File.WriteAllText(file1, "Header1;Header2\nValue1;Value2\nValue9;Value10");
            File.WriteAllText(file2, "Header1;Header2\nValue3;Value4\nValue11;Value12");
            File.WriteAllText(file3, "Header1;Header2\nValue5;Value6\nValue13;Value14\n");
            File.WriteAllText(file4, "Header1;Header2\nValue7;Value8\nValue15;Value16\n");

            // Act
            var result = fileCombiner.combine_files(folder_path: tempDirectory, file_prefix: "", file_suffix: "", file_extension: ".txt", output_file_name: "result.txt", delimiter: ";");
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            string combinedFilePath = Path.Combine(tempDirectory, "result.txt"); // Default output file name
            Assert.That(File.Exists(combinedFilePath), Is.True);
            string combinedContent = File.ReadAllText(combinedFilePath);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(9)); // 1 header row + 8 data rows

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Header1;Header2"));
            Assert.That(combinedContent, Does.Contain("Value1;Value2"));
            Assert.That(combinedContent, Does.Contain("Value3;Value4"));
            Assert.That(combinedContent, Does.Contain("Value5;Value6"));
            Assert.That(combinedContent, Does.Contain("Value7;Value8"));
            Assert.That(combinedContent, Does.Contain("Value9;Value10"));
            Assert.That(combinedContent, Does.Contain("Value11;Value12"));
            Assert.That(combinedContent, Does.Contain("Value13;Value14"));
            Assert.That(combinedContent, Does.Contain("Value15;Value16"));
        }

        [Test]
        public void AppendToFile_AppendsContent()
        {
            dynamic fileCombiner = PythonEngineManager.FilesBaseCombineModule;

            // Arrange
            string sourceFile = Path.Combine(tempDirectory, "source.txt");
            string appendFile = Path.Combine(tempDirectory, "append.txt");
            File.WriteAllText(sourceFile, "Header1;Header2\nValue1;Value2\n");
            File.WriteAllText(appendFile, "Header1;Header2\nValue3;Value4\nValue5;Value6\n");

            // Act
            var result = fileCombiner.append_to_file(source_file: sourceFile, append_file: appendFile, ignore_first_row: true, delimiter: ";");

            // Assert
            Console.WriteLine(result.message);
            Assert.That(result.status, Is.True);
            string combinedContent = File.ReadAllText(sourceFile);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(4)); // 1 header row + 3 data rows

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Value1;Value2"));
            Assert.That(combinedContent, Does.Contain("Value3;Value4"));
            Assert.That(combinedContent, Does.Contain("Value5;Value6"));
        }

        [Test]
        public void AppendToFile_AppendsContentWithMissingNewline()
        {
            dynamic fileCombiner = PythonEngineManager.FilesBaseCombineModule;

            // Arrange
            string sourceFile = Path.Combine(tempDirectory, "source.txt");
            string appendFile = Path.Combine(tempDirectory, "append.txt");
            File.WriteAllText(sourceFile, "Header1;Header2\nValue1;Value2");
            File.WriteAllText(appendFile, "Header1;Header2\nValue3;Value4\nValue5;Value6");

            // Act
            var result = fileCombiner.append_to_file(source_file: sourceFile, append_file: appendFile, ignore_first_row: true, delimiter: ";");

            // Assert
            Console.WriteLine(result.message);
            Assert.That(result.status, Is.True);
            string combinedContent = File.ReadAllText(sourceFile);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(4)); // 1 header row + 3 data rows

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Value1;Value2"));
            Assert.That(combinedContent, Does.Contain("Value3;Value4"));
            Assert.That(combinedContent, Does.Contain("Value5;Value6"));
        }

        [Test]
        public void AppendToFile_AppendsContentWithMissingNewlineWithoutIgnoringFirstRow()
        {
            dynamic fileCombiner = PythonEngineManager.FilesBaseCombineModule;

            // Arrange
            string sourceFile = Path.Combine(tempDirectory, "source.txt");
            string appendFile = Path.Combine(tempDirectory, "append.txt");
            File.WriteAllText(sourceFile, "Header1;Header2\nValue1;Value2");
            File.WriteAllText(appendFile, "Header1;Header2\nValue3;Value4\nValue5;Value6");

            // Act
            var result = fileCombiner.append_to_file(source_file: sourceFile, append_file: appendFile, ignore_first_row: false, delimiter: ";");

            // Assert
            Console.WriteLine(result.message);
            Assert.That(result.status, Is.True);
            string combinedContent = File.ReadAllText(sourceFile);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(5)); // 1 header row + 4 data rows

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Header1;Header2"));
            Assert.That(combinedContent, Does.Contain("Value1;Value2"));
            Assert.That(combinedContent, Does.Contain("Value3;Value4"));
            Assert.That(combinedContent, Does.Contain("Value5;Value6"));
        }

        [Test]
        public void CombineFilesHeaderIndependent_CreatesCombinedFile()
        {
            dynamic fileCombiner = PythonEngineManager.FilesBaseCombineModule;

            // Arrange
            string file1 = Path.Combine(tempDirectory, "file1.txt");
            string file2 = Path.Combine(tempDirectory, "file2.txt");
            File.WriteAllText(file1, "Header1\tHeader2\nValue1\tValue2\n");
            File.WriteAllText(file2, "Header3\tHeader4\nValue3\tValue4\n");

            // Act
            var result_combine = fileCombiner.combine_files_header_independent(
                folder_path: tempDirectory,
                file_prefix: "",
                file_suffix: "",
                file_extension: ".txt",
                output_file_name: "combined.txt",
                overwrite_existing: true,
                delimiter: "\t"
                );

            Console.WriteLine(result_combine.message);
            Console.WriteLine("---START---");
            foreach (var line in result_combine.result)
            {
                string output = ">>";
                foreach (var item in line)
                {
                    output += item + ",";
                }
                Console.WriteLine(output);
            }
            Console.WriteLine("---END---");

            // Assert
            string combinedFilePath = Path.Combine(tempDirectory, "combined.txt");
            Assert.That(File.Exists(combinedFilePath), Is.True);
            string combinedContent = File.ReadAllText(combinedFilePath);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(3)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Header1\tHeader2\tHeader3\tHeader4"));
            Assert.That(combinedContent, Does.Contain("Value1\tValue2\tN/A\tN/A"));
            Assert.That(combinedContent, Does.Contain("N/A\tN/A\tValue3\tValue4"));
        }


        [Test]
        public void CombineFilesHeaderIndependent_CreatesCombinedFileWithFourFiles()
        {
            dynamic fileCombiner = PythonEngineManager.FilesBaseCombineModule;

            // Arrange
            string file1 = Path.Combine(tempDirectory, "file1.txt");
            string file2 = Path.Combine(tempDirectory, "file2.txt");
            string file3 = Path.Combine(tempDirectory, "file3.txt");
            string file4 = Path.Combine(tempDirectory, "file4.txt");
            File.WriteAllText(file1, "Header1;Header2\nValue1;Value2\n");
            File.WriteAllText(file2, "Header3;Header4\nValue3;Value4\n");
            File.WriteAllText(file3, "Header1;Header2;Header5;Header6\nValue5;Value6;Value7;Value8\n");
            File.WriteAllText(file4, "Header1;Header2;Header3;Header4;Header7\nValue9;Value10;Value11;Value12;Value13\n");

            // Act
            var result_combine = fileCombiner.combine_files_header_independent(
                folder_path: tempDirectory,
                file_prefix: "",
                file_suffix: "",
                file_extension: ".txt",
                output_file_name: "combined.txt",
                overwrite_existing: true,
                delimiter: ";"
            );

            Console.WriteLine(result_combine.message);
            Console.WriteLine("---START---");
            foreach (var line in result_combine.result)
            {
                string output = ">>";
                foreach (var item in line)
                {
                    output += item + ",";
                }
                Console.WriteLine(output);
            }
            Console.WriteLine("---END---");

            // Assert
            string combinedFilePath = Path.Combine(tempDirectory, "combined.txt");
            Assert.That(File.Exists(combinedFilePath), Is.True);
            string combinedContent = File.ReadAllText(combinedFilePath);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(5)); // 1 header row + 4 data rows

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Header1;Header2;Header3;Header4;Header5;Header6;Header7"));
            Assert.That(combinedContent, Does.Contain("Value1;Value2;N/A;N/A;N/A;N/A;N/A"));
            Assert.That(combinedContent, Does.Contain("N/A;N/A;Value3;Value4;N/A;N/A;N/A"));
            Assert.That(combinedContent, Does.Contain("Value5;Value6;N/A;N/A;Value7;Value8;N/A"));
            Assert.That(combinedContent, Does.Contain("Value9;Value10;Value11;Value12;N/A;N/A;Value13"));
        }

        [Test]
        public void CombineFilesHeaderIndependent_CreatesCombinedFileWithFourFilesAndMultipleRows()
        {
            dynamic fileCombiner = PythonEngineManager.FilesBaseCombineModule;

            // Arrange
            string file1 = Path.Combine(tempDirectory, "file1.txt");
            string file2 = Path.Combine(tempDirectory, "file2.txt");
            string file3 = Path.Combine(tempDirectory, "file3.txt");
            string file4 = Path.Combine(tempDirectory, "file4.txt");
            File.WriteAllText(file1, "Header1;Header2\nValue1;Value2\n");
            File.WriteAllText(file2, "Header3;Header4\nValue3;Value4\n");
            File.WriteAllText(file3, "Header1;Header2;Header5;Header6\nValue5;Value6;Value7;Value8\nValue9;Value10;Value11;Value12\nValue13;Value14;Value15;Value16\nValue17;Value18;Value19;Value20\n");
            File.WriteAllText(file4, "Header1;Header2;Header3;Header4;Header7\nValue21;Value22;Value23;Value24;Value25\nValue26;Value27;Value28;Value29;Value30\nValue31;Value32;Value33;Value34;Value35\nValue36;Value37;Value38;Value39;Value40\n");

            // Act
            var result_combine = fileCombiner.combine_files_header_independent(
                folder_path: tempDirectory,
                file_prefix: "",
                file_suffix: "",
                file_extension: ".txt",
                output_file_name: "combined.txt",
                overwrite_existing: true,
                delimiter: ";"
            );

            Console.WriteLine(result_combine.message);
            Console.WriteLine("---START---");
            foreach (var line in result_combine.result)
            {
                string output = ">>";
                foreach (var item in line)
                {
                    output += item + ",";
                }
                Console.WriteLine(output);
            }
            Console.WriteLine("---END---");

            // Assert
            string combinedFilePath = Path.Combine(tempDirectory, "combined.txt");
            Assert.That(File.Exists(combinedFilePath), Is.True);
            string combinedContent = File.ReadAllText(combinedFilePath);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(11)); // 1 header row + 10 data rows

            // Check for the content
            Assert.That(combinedContent, Does.Contain("Header1;Header2;Header3;Header4;Header5;Header6;Header7"));
            Assert.That(combinedContent, Does.Contain("Value1;Value2;N/A;N/A;N/A;N/A;N/A"));
            Assert.That(combinedContent, Does.Contain("N/A;N/A;Value3;Value4;N/A;N/A;N/A"));
            Assert.That(combinedContent, Does.Contain("Value5;Value6;N/A;N/A;Value7;Value8;N/A"));
            Assert.That(combinedContent, Does.Contain("Value9;Value10;N/A;N/A;Value11;Value12;N/A"));
            Assert.That(combinedContent, Does.Contain("Value13;Value14;N/A;N/A;Value15;Value16;N/A"));
            Assert.That(combinedContent, Does.Contain("Value17;Value18;N/A;N/A;Value19;Value20;N/A"));
            Assert.That(combinedContent, Does.Contain("Value21;Value22;Value23;Value24;N/A;N/A;Value25"));
            Assert.That(combinedContent, Does.Contain("Value26;Value27;Value28;Value29;N/A;N/A;Value30"));
            Assert.That(combinedContent, Does.Contain("Value31;Value32;Value33;Value34;N/A;N/A;Value35"));
            Assert.That(combinedContent, Does.Contain("Value36;Value37;Value38;Value39;N/A;N/A;Value40"));
        }
    }
}
