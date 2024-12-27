using PythonTests.Setup;
using System.Text;

namespace PythonTests.UtilitiesTests
{
    public static class _CommonFilesBaseWriteTests
    {
        public static void WriteReportData_CreatesReportFile_HeaderAndData(string tempDirectory, string delimiter, WriteReportDataDelegate writeReportData)
        {
            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.StandardTestData_HeaderAndData(tempDirectory, delimiter);

            // Act
            var parameters = new Dictionary<string, object>
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

            var result = writeReportData(parameters);
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

        
        public static void WriteReportData_CreatesReportFile_HeaderOnly(string tempDirectory, string delimiter, WriteReportDataDelegate writeReportData)
        {
            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.StandardTestData_HeaderOnly(tempDirectory,delimiter);

            // Act
            var parameters = new Dictionary<string, object>
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

            var result = writeReportData(parameters);
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

        
        public static void WriteReportData_CreatesReportFile_DataOnly(string tempDirectory, string delimiter, WriteReportDataDelegate writeReportData)
        {
            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.StandardTestData_DataOnly(tempDirectory, delimiter);

            // Act
            var parameters = new Dictionary<string, object>
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

            var result = writeReportData(parameters);
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

        
        public static void WriteReportData_CreatesReportFileWithDelimiter_HeaderAndData(string tempDirectory, string delimiter, WriteReportDataDelegate writeReportData)
        {
            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.DelimitedTestData_HeaderAndData(tempDirectory, delimiter);

            // Act
            var parameters = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", false },
                { "encoding", "utf-8" },
                { "bom", null },
                { "quoting", 0 }, // csv.QUOTE_MINIMAL
                { "delimiter", delimiter }
            };

            var result = writeReportData(parameters);
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
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, header.Select(d => d.Contains(delimiter) ? $"\"{d}\"" : d)))); //wrap string already containing a delimiter
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, data[0].Select(d => d.Contains(delimiter) ? $"\"{d}\"" : d)))); //wrap string already containing a delimiter
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, data[1].Select(d => d.Contains(delimiter) ? $"\"{d}\"" : d)))); //wrap string already containing a delimiter
        }

        
        public static void WriteReportData_CreatesReportFileWithDelimiter_DataOnly(string tempDirectory, string delimiter, WriteReportDataDelegate writeReportData)
        {
            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.DelimitedTestData_DataOnly(tempDirectory, delimiter);

            // Act
            var parameters = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", false },
                { "encoding", "utf-8" },
                { "bom", null },
                { "quoting", 0 }, // csv.QUOTE_MINIMAL
                { "delimiter", delimiter }
            };

            var result = writeReportData(parameters);

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
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, header.Select(d => d.Contains(delimiter) ? $"\"{d}\"" : d)))); //wrap string already containing a delimiter
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, data[0].Select(d => d.Contains(delimiter) ? $"\"{d}\"" : d)))); //wrap string already containing a delimiter
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, data[1].Select(d => d.Contains(delimiter) ? $"\"{d}\"" : d)))); //wrap string already containing a delimiter
        }
        
        public static void WriteReportData_CreatesReportFileWithDelimiter_HeaderOnly(string tempDirectory, string delimiter, WriteReportDataDelegate writeReportData)
        {
            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.DelimitedTestData_HeaderOnly(tempDirectory,delimiter);

            // Act
            var parameters = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", false },
                { "encoding", "utf-8" },
                { "bom", null },
                { "quoting", 0 }, // csv.QUOTE_MINIMAL
                { "delimiter", delimiter }
            };

            var result = writeReportData(parameters);
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
        
        public static void WriteReportData_CreatesReportFileWithNonUtf8_HeaderAndData(string tempDirectory, string delimiter, WriteReportDataDelegate writeReportData)
        {
            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.NonUTF8TestData_HeaderAndData(tempDirectory, delimiter);

            // Act
            var parameters = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", false },
                { "encoding", "utf-8" },
                { "bom", null },
                { "quoting", 3 }, // csv.QUOTE_NONE
                { "delimiter", delimiter }
            };

            var result = writeReportData(parameters);
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
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, header.Select(d => d.Contains(delimiter) ? $"\"{d}\"" : d)))); //wrap string already containing a and Non-UTF-8 character should be preserved
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, data[0].Select(d => d.Contains(delimiter) ? $"\"{d}\"" : d))));
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, data[1].Select(d => d.Contains(delimiter) ? $"\"{d}\"" : d)))); //wrap string already containing a and Non-UTF-8 character should be preserved
        }


        
        public static void WriteReportData_CreatesReportFileWithNonUtf8_HeaderOnly(string tempDirectory, string delimiter, WriteReportDataDelegate writeReportData)
        {
            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.NonUTF8TestData_HeaderOnly(tempDirectory, delimiter);

            // Act
            var parameters = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", false },
                { "encoding", "utf-8" },
                { "bom", null },
                { "quoting", 3 }, // csv.QUOTE_NONE
                { "delimiter", delimiter }
            };

            var result = writeReportData(parameters);
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
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, header))); // Non-UTF-8 characters in header should be preserved
        }

        
        public static void WriteReportData_CreatesReportFileWithNonUtf8_DataOnly(string tempDirectory, string delimiter, WriteReportDataDelegate writeReportData)
        {
            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.NonUTF8TestData_DataOnly(tempDirectory, delimiter);

            // Act
            var parameters = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", false },
                { "encoding", "utf-8" },
                { "bom", null },
                { "quoting", 3 }, // csv.QUOTE_NONE
                { "delimiter", delimiter }
            };

            var result = writeReportData(parameters);
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

        
        public static void WriteReportData_CreatesReportFileWithNonUtf8AndDelimiter_HeaderAndData(string tempDirectory, string delimiter, WriteReportDataDelegate writeReportData)
        {
            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.NonUTF8AndDelimitedTestData_HeaderAndData(tempDirectory, delimiter);

            // Act
            var parameters = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", false },
                { "encoding", "utf-8" },
                { "bom", null },
                { "quoting", 0 }, // csv.QUOTE_MINIMAL
                { "delimiter", delimiter }
            };

            var result = writeReportData(parameters);
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
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, header.Select(d => d.Contains(delimiter) ? $"\"{d}\"" : d)))); //wrap string already containing a delimiter, Non-UTF-8 characters and delimiter in header should be preserved and quoted
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, data[0])));
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, data[1].Select(d => d.Contains(delimiter) ? $"\"{d}\"" : d)))); //wrap string already containing a and Non-UTF-8 character should be preserved
        }

        
        public static void WriteReportData_CreatesReportFileWithNonUtf8AndDelimiter_DataOnly(string tempDirectory, string delimiter, WriteReportDataDelegate writeReportData)
        {
            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.NonUTF8AndDelimitedTestData_DataOnly(tempDirectory, delimiter);

            // Act
            var parameters = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", false },
                { "encoding", "utf-8" },
                { "bom", null },
                { "quoting", 0 }, // csv.QUOTE_MINIMAL
                { "delimiter", delimiter }
            };

            var result = writeReportData(parameters);
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
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, data[0])));
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, data[1].Select(d => d.Contains(delimiter) ? $"\"{d}\"" : d)))); //wrap string already containing a and Non-UTF-8 character should be preserved
        }


        
        public static void WriteReportData_CreatesReportFileWithNonUtf8AndDelimiter_HeaderOnly(string tempDirectory, string delimiter, WriteReportDataDelegate writeReportData)
        {
            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.NonUTF8AndDelimitedTestData_HeaderOnly(tempDirectory, delimiter);

            // Act
            var parameters = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", false },
                { "encoding", "utf-8" },
                { "bom", null },
                { "quoting", 0 }, // csv.QUOTE_MINIMAL
                { "delimiter", delimiter }
            };
            var result = writeReportData(parameters);
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
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, header.Select(d => d.Contains(delimiter  ) ? $"\"{d}\"" : d)))); //wrap string already containing a delimiter, Non-UTF-8 characters and delimiter in header should be preserved and quoted
        }


        
        public static void WriteReportData_CreatesReportFileWithNonAsciiDataAndEnforceAscii(string tempDirectory, string delimiter, WriteReportDataDelegate writeReportData)
        {
            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.NonASCIITestData_HeaderAndData(tempDirectory, delimiter);

            // Act
            var parameters = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", true },
                { "encoding", "utf-8" },
                { "bom", null },
                { "quoting", 3 }, // csv.QUOTE_NONE
                { "delimiter", delimiter }
            };
            var result = writeReportData(parameters);
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
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, data[0].Select(d => _CommonFileBaseTestsData.StripNonAscii(d)))));
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, data[1].Select(d => _CommonFileBaseTestsData.StripNonAscii(d)))));
        }

        
        public static void WriteReportData_CreatesReportFileWithBOM(string tempDirectory, string delimiter, WriteReportDataDelegate writeReportData)
        { 
            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.StandardTestData_HeaderAndData(tempDirectory,delimiter);

            dynamic bomValue = PythonEngineManager.BOMValueClass();
            var bom = bomValue.UTF_8;
            
            // Act
            var parameters = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", false },
                { "encoding", "utf-8" },
                { "bom", bom },
                { "quoting", 3 }, // csv.QUOTE_NONE
                { "delimiter", delimiter }
            };
            var result = writeReportData(parameters);
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

        public static void WriteReportDataAs_CreatesFileWithLatinEncoding_HeaderAndData(string tempDirectory, string delimiter, WriteReportDataDelegate writeReportData)
        {
            // Arrange
            var (fileName, header, data) = _CommonFileBaseTestsData.NonASCIITestData_HeaderAndData(tempDirectory, delimiter);

            // Act
            var parameters = new Dictionary<string, object>
            {
                { "file_name", fileName },
                { "header", header },
                { "data", data },
                { "write_type", "w" },
                { "enforce_ascii", false },
                { "encoding", "latin-1" },
                { "bom", null },
                { "quoting", 3 }, // csv.QUOTE_NONE
                { "delimiter", delimiter }
            };
            var result = writeReportData(parameters);
            Console.WriteLine(result.message);


            // Register the code page provider to support "latin-1" encoding
            System.Text.Encoding.RegisterProvider(System.Text.CodePagesEncodingProvider.Instance);

            // Assert
            Assert.That(File.Exists(fileName), Is.True);
            string reportContent = File.ReadAllText(fileName, System.Text.Encoding.Latin1);
            string[] lines = reportContent.Split(new[] { '\r', '\n' });
            foreach (var line in lines)
            {
                Console.WriteLine("{" + line);
            }

            // Check for the number of rows
            Assert.That(lines.Length, Is.EqualTo(3)); // 1 header row + 2 data rows

            // Check for the content
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, header)));
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, data[0]))); // Non-UTF-8 characters should be preserved
            Assert.That(reportContent, Does.Contain(string.Join(delimiter, data[1]))); // Non-UTF-8 characters should be preserved
        }
    }
}
