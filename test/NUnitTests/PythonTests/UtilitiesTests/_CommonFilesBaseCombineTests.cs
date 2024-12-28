using PythonTests.Setup;
using System.Collections.Generic;


namespace PythonTests.UtilitiesTests
{
    public static class _CommonFilesBaseCombineTests
    {

        public static void CombineFiles_CreatesCombinedFile(
            string tempDirectory,
            string delimiter,
            CombineReportDataDelegate combineReportData
            )
        {

            // Arrange
            var (fileData, testComparisonData) = _CommonFileBaseTestsData.StandardCombineTestData(tempDirectory, delimiter);
            
            // write test data to files
            foreach (var file in fileData)
            {
                File.WriteAllText(file.Key, file.Value);
            }

            // Act
            var parameters = new Dictionary<string, object>
            {
                { "folder_path", tempDirectory },
                { "file_prefix", "" },
                { "file_suffix", "" },
                { "file_extension", ".txt" },
                { "output_file_name", "result.txt" },
                { "delimiter", delimiter }
            };

            //var result = fileCombiner.combine_files(folder_path: tempDirectory, file_prefix: "", file_suffix: "", file_extension: ".txt", output_file_name: "result.txt", delimiter: ";");
            var result = combineReportData(parameters);
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
            Assert.That(lines.Length, Is.EqualTo(testComparisonData.Count)); // 1 header row + 2 data rows

            // Check for the content
            foreach (var data in testComparisonData)
            {
                Assert.That(combinedContent, Does.Contain(data));
            }
        }

        
        public static void CombineFiles_CreatesCombinedFileWithFourFilesAndMultipleRows(string tempDirectory,
            string delimiter,
            CombineReportDataDelegate combineReportData
            )
        {
            // Arrange
            var (fileData, testComparisonData) = _CommonFileBaseTestsData.StandardCombineTestData_FourFilesAndMultipleRows(tempDirectory, delimiter);

            // write test data to files
            foreach (var file in fileData)
            {
                File.WriteAllText(file.Key, file.Value);
            }

            // Act
            var parameters = new Dictionary<string, object>
            {
                { "folder_path", tempDirectory },
                { "file_prefix", "" },
                { "file_suffix", "" },
                { "file_extension", ".txt" },
                { "output_file_name", "result.txt" },
                { "delimiter", delimiter }
            };

            //var result = fileCombiner.combine_files(folder_path: tempDirectory, file_prefix: "", file_suffix: "", file_extension: ".txt", output_file_name: "result.txt", delimiter: ";");
            var result = combineReportData(parameters); Console.WriteLine(result.message);
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
            Assert.That(lines.Length, Is.EqualTo(testComparisonData.Count)); // 1 header row + 8 data rows

            // Check for the content
            foreach (var data in testComparisonData)
            {
                Assert.That(combinedContent, Does.Contain(data));
            }
        }

        
        public static void CombineFiles_CreatesCombinedFileWithSuffix(string tempDirectory,
            string delimiter,
            CombineReportDataDelegate combineReportData)
        {
            // Arrange
            var (fileData, testComparisonData) = _CommonFileBaseTestsData.StandardCombineTestData_FourFilesAndMultipleRows_WithSuffix(tempDirectory, delimiter);

            // write test data to files
            foreach (var file in fileData)
            {
                File.WriteAllText(file.Key, file.Value);
            }

            // Act
            var parameters = new Dictionary<string, object>
            {
                { "folder_path", tempDirectory },
                { "file_prefix", "" },
                { "file_suffix", "mich gefragt" },
                { "file_extension", ".txt" },
                { "output_file_name", "result.txt" },
                { "delimiter", delimiter }
            };

            var result = combineReportData(parameters);
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
            Assert.That(lines.Length, Is.EqualTo(testComparisonData.Count)); // 1 header row + 6 data rows (3 files with suffix)

            // Check for the content
            foreach (var data in testComparisonData)
            {
                Assert.That(combinedContent, Does.Contain(data));
            }
        }

        
        public static void CombineFiles_CreatesCombinedFileWithPrefix(string tempDirectory,
            string delimiter,
            CombineReportDataDelegate combineReportData)
        {
            // Arrange
            var (fileData, testComparisonData) = _CommonFileBaseTestsData.StandardCombineTestData_FourFilesAndMultipleRows_WithPrefix(tempDirectory, delimiter);

            // write test data to files
            foreach (var file in fileData)
            {
                File.WriteAllText(file.Key, file.Value);
            }

            // Act
            var parameters = new Dictionary<string, object>
            {
                { "folder_path", tempDirectory },
                { "file_prefix", "duHast" },
                { "file_suffix", "" },
                { "file_extension", ".txt" },
                { "output_file_name", "result.txt" },
                { "delimiter", delimiter }
            };

            var result = combineReportData(parameters);
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
            Assert.That(lines.Length, Is.EqualTo(testComparisonData.Count)); // 1 header row + 6 data rows (3 files with prefix)

            // Check for the content
            foreach (var data in testComparisonData)
            {
                Assert.That(combinedContent, Does.Contain(data));
            }
        }
        
        public static void CombineFiles_CreatesCombinedFileWithPrefixAndSuffix(string tempDirectory,
            string delimiter,
            CombineReportDataDelegate combineReportData)
        {
            // Arrange
            var (fileData, testComparisonData) = _CommonFileBaseTestsData.StandardCombineTestData_FourFilesAndMultipleRows_WithPrefixAndSuffix(tempDirectory, delimiter);

            // write test data to files
            foreach (var file in fileData)
            {
                File.WriteAllText(file.Key, file.Value);
            }

            // Act
            var parameters = new Dictionary<string, object>
            {
                { "folder_path", tempDirectory },
                { "file_prefix", "duHast" },
                { "file_suffix", "mich gefragt" },
                { "file_extension", ".txt" },
                { "output_file_name", "result.txt" },
                { "delimiter", delimiter }
            };

            var result = combineReportData(parameters);
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
            Assert.That(lines.Length, Is.EqualTo(testComparisonData.Count)); // 1 header row + 4 data rows (2 files with suffix and prefix matching filters provided)

            // Check for the content
            foreach (var data in testComparisonData)
            {
                Assert.That(combinedContent, Does.Contain(data));
            }
        }

        
        public static void CombineFiles_CreatesCombinedFileWithDifferentExtension(string tempDirectory,
            string delimiter,
            CombineReportDataDelegate combineReportData)
        {
            // Arrange
            var (fileData, testComparisonData) = _CommonFileBaseTestsData.StandardCombineTestData_FourFilesAndMultipleRows_WithDiffExtension(tempDirectory, delimiter);

            // write test data to files
            foreach (var file in fileData)
            {
                File.WriteAllText(file.Key, file.Value);
            }

            // Act
            var parameters = new Dictionary<string, object>
            {
                { "folder_path", tempDirectory },
                { "file_prefix", "" },
                { "file_suffix", "" },
                { "file_extension", ".dert" },
                { "output_file_name", "result.txt" },
                { "delimiter", delimiter }
            };

            var result = combineReportData(parameters);
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
            Assert.That(lines.Length, Is.EqualTo(testComparisonData.Count)); // 1 header row + 6 data rows (3 files with .dert extension)

            // Check for the content
            foreach (var data in testComparisonData)
            {
                Assert.That(combinedContent, Does.Contain(data));
            }
        }

        
        public static void CombineFiles_CreatesCombinedFileWithMissingNewline(
            string tempDirectory,
            string delimiter,
            CombineReportDataDelegate combineReportData)
        {
            // Arrange
            var (fileData, testComparisonData) = _CommonFileBaseTestsData.StandardCombineTestData_FourFilesAndMultipleRows_MissingNewLine(tempDirectory, delimiter);

            // write test data to files
            foreach (var file in fileData)
            {
                File.WriteAllText(file.Key, file.Value);
            }

            // Act
            var parameters = new Dictionary<string, object>
            {
                { "folder_path", tempDirectory },
                { "file_prefix", "" },
                { "file_suffix", "" },
                { "file_extension", ".txt" },
                { "output_file_name", "result.txt" },
                { "delimiter", delimiter }
            };

            var result = combineReportData(parameters);
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
            Assert.That(lines.Length, Is.EqualTo(testComparisonData.Count)); // 1 header row + 8 data rows

            // Check for the content
            foreach (var data in testComparisonData)
            {
                Assert.That(combinedContent, Does.Contain(data));
            }
        }

        
        public static void AppendToFile_AppendsContent(string tempDirectory,
            string delimiter,
            CombineReportDataDelegate combineReportData)
        {
            // Arrange
            var (fileData, testComparisonData, sourceFile, appendFile) = _CommonFileBaseTestsData.AppendToFile_AppendsContent(tempDirectory, delimiter);

            // write test data to files
            foreach (var file in fileData)
            {
                File.WriteAllText(file.Key, file.Value);
            }

            // Act
            var parameters = new Dictionary<string, object>
            {
                { "source_file",sourceFile },
                { "append_file", appendFile },
                { "ignore_first_row", true },
                { "delimiter", delimiter }
            };

            var result = combineReportData(parameters);
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            string combinedContent = File.ReadAllText(sourceFile);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(testComparisonData.Count)); // 1 header row + 3 data rows

            // Check for the content
            foreach (var data in testComparisonData)
            {
                Assert.That(combinedContent, Does.Contain(data));
            }
        }

        
        public static void AppendToFile_AppendsContentWithMissingNewline(string tempDirectory,
            string delimiter,
            CombineReportDataDelegate combineReportData)
        {
            // Arrange
            var (fileData, testComparisonData, sourceFile, appendFile) = _CommonFileBaseTestsData.AppendToFile_AppendsContent_MissingNewline(tempDirectory, delimiter);

            // write test data to files
            foreach (var file in fileData)
            {
                File.WriteAllText(file.Key, file.Value);
            }

            // Act
            var parameters = new Dictionary<string, object>
            {
                { "source_file",sourceFile },
                { "append_file", appendFile },
                { "ignore_first_row", true },
                { "delimiter", delimiter }
            };

            var result = combineReportData(parameters);
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            string combinedContent = File.ReadAllText(sourceFile);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(testComparisonData.Count)); // 1 header row + 3 data rows

            // Check for the content
            foreach (var data in testComparisonData)
            {
                Assert.That(combinedContent, Does.Contain(data));
            }
        }

        
        public static void AppendToFile_AppendsContentWithMissingNewlineWithoutIgnoringFirstRow(string tempDirectory,
            string delimiter,
            CombineReportDataDelegate combineReportData)
        {
            // Arrange
            var (fileData, testComparisonData, sourceFile, appendFile) = _CommonFileBaseTestsData.AppendToFile_AppendsContent_MissingNewlineWithoutIgnoringFirstRow(tempDirectory, delimiter);

            // write test data to files
            foreach (var file in fileData)
            {
                File.WriteAllText(file.Key, file.Value);
            }

            // Act
            var parameters = new Dictionary<string, object>
            {
                { "source_file",sourceFile },
                { "append_file", appendFile },
                { "ignore_first_row", false },
                { "delimiter", delimiter }
            };

            var result = combineReportData(parameters);
            Console.WriteLine(result.message);

            // Assert
            Assert.That(result.status, Is.True);
            string combinedContent = File.ReadAllText(sourceFile);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(testComparisonData.Count)); // 1 header row + 4 data rows

            // Check for the content
            foreach (var data in testComparisonData)
            {
                Assert.That(combinedContent, Does.Contain(data));
            }
        }

        
        public static void CombineFilesHeaderIndependent_CreatesCombinedFile(
            string tempDirectory,
            string delimiter,
            CombineReportDataDelegate combineReportData)
        {
            // Arrange
            var (fileData, testComparisonData) = _CommonFileBaseTestsData.CombineFilesHeaderIndependent_CreatesCombinedFile(tempDirectory, delimiter);

            // write test data to files
            foreach (var file in fileData)
            {
                File.WriteAllText(file.Key, file.Value);
            }

            // Act
            var parameters = new Dictionary<string, object>
            {
                { "folder_path", tempDirectory },
                { "file_prefix", "" },
                { "file_suffix", "" },
                { "file_extension", ".txt" },
                { "output_file_name", "result.txt" },
                { "overwrite_existing", true },
                { "delimiter", delimiter }
            };

            var result = combineReportData(parameters);

            Console.WriteLine(result.message);
            Console.WriteLine("---START---");
            foreach (var line in result.result)
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
            string combinedFilePath = Path.Combine(tempDirectory, "result.txt");
            Assert.That(File.Exists(combinedFilePath), Is.True);
            string combinedContent = File.ReadAllText(combinedFilePath);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(testComparisonData.Count)); // 1 header row + 2 data rows

            // Check for the content
            foreach (var data in testComparisonData)
            {
                Assert.That(combinedContent, Does.Contain(data));
            }
        }


        
        public static void CombineFilesHeaderIndependent_CreatesCombinedFileWithFourFiles(string tempDirectory,
            string delimiter,
            CombineReportDataDelegate combineReportData)
        {
            // Arrange
            var (fileData, testComparisonData) = _CommonFileBaseTestsData.CombineFilesHeaderIndependent_CreatesCombinedFileWithFourFiles(tempDirectory, delimiter);

            // write test data to files
            foreach (var file in fileData)
            {
                File.WriteAllText(file.Key, file.Value);
            }

            // Act
            var parameters = new Dictionary<string, object>
            {
                { "folder_path", tempDirectory },
                { "file_prefix", "" },
                { "file_suffix", "" },
                { "file_extension", ".txt" },
                { "output_file_name", "result.txt" },
                { "overwrite_existing", true },
                { "delimiter", delimiter }
            };

            var result = combineReportData(parameters);


            Console.WriteLine(result.message);
            Console.WriteLine("---START---");
            foreach (var line in result.result)
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
            string combinedFilePath = Path.Combine(tempDirectory, "result.txt");
            Assert.That(File.Exists(combinedFilePath), Is.True);
            string combinedContent = File.ReadAllText(combinedFilePath);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(testComparisonData.Count)); // 1 header row + 4 data rows

            // Check for the content
            foreach (var data in testComparisonData)
            {
                Assert.That(combinedContent, Does.Contain(data));
            }
        }

        
        public static void CombineFilesHeaderIndependent_CreatesCombinedFileWithFourFilesAndMultipleRows(string tempDirectory,
            string delimiter,
            CombineReportDataDelegate combineReportData)
        {
            // Arrange
            var (fileData, testComparisonData) = _CommonFileBaseTestsData.CombineFilesHeaderIndependent_CreatesCombinedFileWithFourFilesAndMultipleRows(tempDirectory, delimiter);

            // write test data to files
            foreach (var file in fileData)
            {
                File.WriteAllText(file.Key, file.Value);
            }

            // Act
            var parameters = new Dictionary<string, object>
            {
                { "folder_path", tempDirectory },
                { "file_prefix", "" },
                { "file_suffix", "" },
                { "file_extension", ".txt" },
                { "output_file_name", "result.txt" },
                { "overwrite_existing", true },
                { "delimiter", delimiter }
            };

            var result = combineReportData(parameters);


            Console.WriteLine(result.message);
            Console.WriteLine("---START---");
            foreach (var line in result.result)
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
            string combinedFilePath = Path.Combine(tempDirectory, "result.txt");
            Assert.That(File.Exists(combinedFilePath), Is.True);
            string combinedContent = File.ReadAllText(combinedFilePath);
            string[] lines = combinedContent.Split(new[] { '\r', '\n' });

            foreach (var line in lines)
            {
                Console.WriteLine("{" + line + "}");
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(testComparisonData.Count)); // 1 header row + 10 data rows

            // Check for the content
            foreach (var data in testComparisonData)
            {
                Assert.That(combinedContent, Does.Contain(data));
            }
        }
    }
}
