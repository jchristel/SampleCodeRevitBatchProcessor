namespace PythonTests.UtilitiesTests
{
    public static class _CommonFileBaseTestsData
    {
       
        public static string StripNonAscii(string input)
        {
            // Remove non-ASCII characters from input string
            // https://stackoverflow.com/questions/1120198/most-efficient-way-to-remove-special-characters-from-string
            // used to compare data read from file with data written to file
            return new string(input.Where(c => c <= 127).ToArray());
        }


        public static (string fileName, List<string> header, List<List<string>> data) StandardTestData_EmptyFile(string tempDirectory, string delimiter)
        {
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> ();
            List<List<string>> data = new List<List<string>>();
            return (fileName, header, data);
        }

        public static (string fileName, List<string> header, List<List<string>> data) StandardTestData_HeaderAndData(string tempDirectory, string delimiter)
        {
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> { "Header1", "Header2" };
            List<List<string>> data = new List<List<string>>
            {
                new List<string> { "Value1", "Value2" },
                new List<string> { "Value3", "Value4" }
            };
            return (fileName, header, data);
        }

        public static (string fileName, List<string> header, List<List<string>> data) StandardTestData_HeaderOnly(string tempDirectory, string delimiter)
        {
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> { "Header1", "Header2" };
            List<List<string>> data = new List<List<string>>(); // No data rows
            return (fileName, header, data);
        }

        public static (string fileName, List<string> header, List<List<string>> data) StandardTestData_DataOnly(string tempDirectory, string delimiter)
        {
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string>(); // No header
            List<List<string>> data = new List<List<string>>
            {
                new List<string> { "Value1", "Value2" },
                new List<string> { "Value3", "Value4" }
            };
            return (fileName, header, data);
        }

        public static (string fileName, List<string> header, List<List<string>> data) DelimitedTestData_HeaderAndData(string tempDirectory, string delimiter)
        {
            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> { $"Header1{delimiter}Part1", $"Header2{delimiter}Part2" }; // Header containing delimiter
            List<List<string>> data = new List<List<string>>
            {
                new List<string> { $"Value1{delimiter}Part1", $"Value2{delimiter}Part2" }, // Data containing delimiter
                new List<string> { $"Value3{delimiter}Part3", $"Value4{delimiter}Part4" }  // Data containing delimiter
            };
            return (fileName, header, data);
        }

        public static (string fileName, List<string> header, List<List<string>> data) DelimitedTestData_HeaderOnly(string tempDirectory, string delimiter)
        {
            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> { $"Header1{delimiter}Part1", $"Header2{delimiter}Part2" };// Header containing delimiter
            List<List<string>> data = new List<List<string>>(); // No data rows
            return (fileName, header, data);
        }

        public static (string fileName, List<string> header, List<List<string>> data) DelimitedTestData_DataOnly(string tempDirectory,string delimiter)
        {
            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> (); // No header
            List<List<string>> data = new List<List<string>>
            {
                new List<string> { $"Value1{delimiter}Part1", "Value2" },
                new List<string> { "Value3", $"Value4{delimiter}Part4" }
            };
            return (fileName, header, data);
        }

        public static (string fileName, List<string> header, List<List<string>> data) NonUTF8TestData_HeaderAndData(string tempDirectory, string delimiter)
        {
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> { "Hëader1", "Hëader2" }; // Non-UTF-8 characters in header
            List<List<string>> data = new List<List<string>>
            {
                new List<string> { "Value1", "Value2" },
                new List<string> { "Value3", "Välue4" } // Non-UTF-8 character in data
            };
            return (fileName, header, data);
        }

        public static (string fileName, List<string> header, List<List<string>> data) NonUTF8TestData_HeaderOnly(string tempDirectory, string delimiter)
        {
            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> { "Hëader1", "Hëader2" }; // Non-UTF-8 characters in header
            List<List<string>> data = new List<List<string>>(); // No data rows
            return (fileName, header, data);
        }

        public static (string fileName, List<string> header, List<List<string>> data) NonUTF8TestData_DataOnly(string tempDirectory, string delimiter)
        {
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> (); // No header
            List<List<string>> data = new List<List<string>>
            {
                new List<string> { "Value1", "Value2" },
                new List<string> { "Value3", "Välue4" } // Non-UTF-8 character
            };
            return (fileName, header, data);
        }

       public static (string fileName, List<string> header, List<List<string>> data) NonUTF8AndDelimitedTestData_HeaderAndData(string tempDirectory, string delimiter)
        {
            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string>{ $"Hëader1{delimiter}Part1", $"Hëader2{delimiter}Part2" }; // Non-UTF-8 characters and delimiter in header
            List<List<string>> data = new List<List<string>>
            {
                new List<string> { "Value1", "Value2" },
                new List<string> { "Value3", $"Välue4{delimiter}Part" } // Non-UTF-8 character and delimiter in data
            };
            return (fileName, header, data);
        }

       public static (string fileName, List<string> header, List<List<string>> data) NonUTF8AndDelimitedTestData_HeaderOnly(string tempDirectory, string delimiter)
        {
            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string>{ $"Hëader1{delimiter}Part1", $"Hëader2{delimiter}Part2" }; // Non-UTF-8 characters and delimiter in header

            List<List<string>> data = new List<List<string>>(); // No data rows
            return (fileName, header, data);
        }

        public static (string fileName, List<string> header, List<List<string>> data) NonUTF8AndDelimitedTestData_DataOnly(string tempDirectory, string delimiter)
        {
            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> ();// No header
            List<List<string>> data = new List<List<string>>
            {
                new List<string> { "Value1", "Value2" },
                new List<string> { "Value3", $"Välue4{delimiter}Part" } // Non-UTF-8 character and delimiter in data
            };
            return (fileName, header, data);
        }

        public static (string fileName, List<string> header, List<List<string>> data) ArrangeMaxFieldSizeTestData_HeaderAndData(string tempDirectory, string delimiter)
        {
            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> { "Header1", "Header2" };
            List<List<string>> data = new List<List<string>>
            {
                new List<string> { new string('A', 1000000), "Value2" }, // Large field size
                new List<string> { "Value3", "Value4" }
            };
            return (fileName, header, data);
        }

        public static (string fileName, List<string> header, List<List<string>> data) NonASCIITestData_HeaderAndData(string tempDirectory, string delimiter)
        {
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> { "Header1", "Header2" };
            List<List<string>> data = new List<List<string>>
            {
                new List<string> { "Välue1", "Välue2" },
                new List<string> { "Välue3", "Välue4" }
            };
            return (fileName, header, data);
        }

        #region file combine test data
        public static (Dictionary<string, string>, List<string>)  StandardCombineTestData(string tempDirectory, string delimiter)
        {
            string header_all = $"Header1{delimiter}Header2";
            string data1_part = $"Value1{delimiter}Value2";
            string data2_part = $"Value3{delimiter}Value4";

            string fileName1 = Path.Combine(tempDirectory, "file1.txt");
            string fileName2 = Path.Combine(tempDirectory, "file2.txt");

            string data1 = $"{header_all}\n{data1_part}\n";
            string data2 = $"{header_all}\n{data2_part}\n";

            List<string> fileNames = new List<string> { fileName1, fileName2 };
            List<string> file_data = new List<string> { data1, data2 };
            
            Dictionary<string, string> fileData = new Dictionary<string, string>
            {
                { fileName1, data1 },
                { fileName2, data2 }
            };

            List<string> testComparisonData = new List<string> { 
                header_all, 
                data1_part,
                data2_part
            };

            return (fileData, testComparisonData);
        }

        public static (Dictionary<string, string>, List<string>) StandardCombineTestData_FourFilesAndMultipleRows(string tempDirectory, string delimiter)
        {
            string header_all = $"Header1{delimiter}Header2";
            string data1_part = $"Value1{delimiter}Value2";
            string data2_part = $"Value3{delimiter}Value4";
            string data3_part = $"Value5{delimiter}Value6";
            string data4_part = $"Value7{delimiter}Value8";
            string data5_part = $"Value9{delimiter}Value10";
            string data6_part = $"Value11{delimiter}Value12";
            string data7_part = $"Value13{delimiter}Value14";
            string data8_part = $"Value15{delimiter}Value16";
            string fileName1 = Path.Combine(tempDirectory, "file1.txt");
            string fileName2 = Path.Combine(tempDirectory, "file2.txt");
            string fileName3 = Path.Combine(tempDirectory, "file3.txt");
            string fileName4 = Path.Combine(tempDirectory, "file4.txt");
            string data1 = $"{header_all}\n{data1_part}\n{data5_part}\n";
            string data2 = $"{header_all}\n{data2_part}\n{data6_part}\n";
            string data3 = $"{header_all}\n{data3_part}\n{data7_part}\n";
            string data4 = $"{header_all}\n{data4_part}\n{data8_part}\n";
            List<string> fileNames = new List<string> { fileName1, fileName2, fileName3, fileName4 };
            List<string> file_data = new List<string> { data1, data2, data3, data4 };
            Dictionary<string, string> fileData = new Dictionary<string, string>
            {
                { fileName1, data1 },
                { fileName2, data2 },
                { fileName3, data3 },
                { fileName4, data4 }
            };
            List<string> testComparisonData = new List<string> {
                header_all,
                data1_part,
                data2_part,
                data3_part,
                data4_part,
                data5_part,
                data6_part,
                data7_part,
                data8_part
            };
            return (fileData, testComparisonData);
        }

        public static (Dictionary<string, string>, List<string>) StandardCombineTestData_FourFilesAndMultipleRows_WithSuffix(string tempDirectory, string delimiter)
        {
            string header_all = $"Header1{delimiter}Header2";
            string data1_part = $"Value1{delimiter}Value2";
            string data2_part = $"Value3{delimiter}Value4";
            string data3_part = $"Value5{delimiter}Value6";
            string data4_part = $"Value7{delimiter}Value8";
            string data5_part = $"Value9{delimiter}Value10";
            string data6_part = $"Value11{delimiter}Value12";
            string data7_part = $"Value13{delimiter}Value14";
            string data8_part = $"Value15{delimiter}Value16";
            string fileName1 = Path.Combine(tempDirectory, "file1_mich gefragt.txt");
            string fileName2 = Path.Combine(tempDirectory, "file2_mich gefragt.txt");
            string fileName3 = Path.Combine(tempDirectory, "file3_mich gefragt.txt");
            string fileName4 = Path.Combine(tempDirectory, "file4.txt");
            string data1 = $"{header_all}\n{data1_part}\n{data5_part}\n";
            string data2 = $"{header_all}\n{data2_part}\n{data6_part}\n";
            string data3 = $"{header_all}\n{data3_part}\n{data7_part}\n";
            string data4 = $"{header_all}\n{data4_part}\n{data8_part}\n";
            List<string> fileNames = new List<string> { fileName1, fileName2, fileName3, fileName4 };
            List<string> file_data = new List<string> { data1, data2, data3, data4 };
            Dictionary<string, string> fileData = new Dictionary<string, string>
            {
                { fileName1, data1 },
                { fileName2, data2 },
                { fileName3, data3 },
                { fileName4, data4 }
            };
            List<string> testComparisonData = new List<string> {
                header_all,
                data1_part,
                data2_part,
                data3_part,
                //data4_part, not included because file has different suffix
                data5_part,
                data6_part,
                data7_part //,
                //data8_part not included because file has different suffix
            };
            return (fileData, testComparisonData);
        }

        public static (Dictionary<string, string>, List<string>) StandardCombineTestData_FourFilesAndMultipleRows_WithPrefix(string tempDirectory, string delimiter)
        {
            string header_all = $"Header1{delimiter}Header2";
            string data1_part = $"Value1{delimiter}Value2";
            string data2_part = $"Value3{delimiter}Value4";
            string data3_part = $"Value5{delimiter}Value6";
            string data4_part = $"Value7{delimiter}Value8";
            string data5_part = $"Value9{delimiter}Value10";
            string data6_part = $"Value11{delimiter}Value12";
            string data7_part = $"Value13{delimiter}Value14";
            string data8_part = $"Value15{delimiter}Value16";
            string fileName1 = Path.Combine(tempDirectory, "duHast_file1.txt");
            string fileName2 = Path.Combine(tempDirectory, "duHast_file2.txt");
            string fileName3 = Path.Combine(tempDirectory, "duHast_file3.txt");
            string fileName4 = Path.Combine(tempDirectory, "file4.txt");
            string data1 = $"{header_all}\n{data1_part}\n{data5_part}\n";
            string data2 = $"{header_all}\n{data2_part}\n{data6_part}\n";
            string data3 = $"{header_all}\n{data3_part}\n{data7_part}\n";
            string data4 = $"{header_all}\n{data4_part}\n{data8_part}\n";
            List<string> fileNames = new List<string> { fileName1, fileName2, fileName3, fileName4 };
            List<string> file_data = new List<string> { data1, data2, data3, data4 };
            Dictionary<string, string> fileData = new Dictionary<string, string>
            {
                { fileName1, data1 },
                { fileName2, data2 },
                { fileName3, data3 },
                { fileName4, data4 }
            };
            List<string> testComparisonData = new List<string> {
                header_all,
                data1_part,
                data2_part,
                data3_part,
                //data4_part, not included because file has different prefix
                data5_part,
                data6_part,
                data7_part //,
                //data8_part not included because file has different prefix
            };
            return (fileData, testComparisonData);
        }

        public static (Dictionary<string, string>, List<string>) StandardCombineTestData_FourFilesAndMultipleRows_WithPrefixAndSuffix(string tempDirectory, string delimiter)
        {
            string header_all = $"Header1{delimiter}Header2";
            string data1_part = $"Value1{delimiter}Value2";
            string data2_part = $"Value3{delimiter}Value4";
            string data3_part = $"Value5{delimiter}Value6";
            string data4_part = $"Value7{delimiter}Value8";
            string data5_part = $"Value9{delimiter}Value10";
            string data6_part = $"Value11{delimiter}Value12";
            string data7_part = $"Value13{delimiter}Value14";
            string data8_part = $"Value15{delimiter}Value16";
            string fileName1 = Path.Combine(tempDirectory, "duHast_file1_mich gefragt.txt");
            string fileName2 = Path.Combine(tempDirectory, "duHast_file2_mich gefragt.txt");
            string fileName3 = Path.Combine(tempDirectory, "file3_mich gefragt.txt");
            string fileName4 = Path.Combine(tempDirectory, "duHast_file4.txt");
            string data1 = $"{header_all}\n{data1_part}\n{data5_part}\n";
            string data2 = $"{header_all}\n{data2_part}\n{data6_part}\n";
            string data3 = $"{header_all}\n{data3_part}\n{data7_part}\n";
            string data4 = $"{header_all}\n{data4_part}\n{data8_part}\n";
            List<string> fileNames = new List<string> { fileName1, fileName2, fileName3, fileName4 };
            List<string> file_data = new List<string> { data1, data2, data3, data4 };
            Dictionary<string, string> fileData = new Dictionary<string, string>
            {
                { fileName1, data1 },
                { fileName2, data2 },
                { fileName3, data3 },
                { fileName4, data4 }
            };
            List<string> testComparisonData = new List<string> {
                header_all,
                data1_part,
                data2_part,
                //data3_part,not included because file has different prefix
                //data4_part, not included because file has different prefix
                data5_part,
                data6_part//,
                //data7_part not included because file has different prefix
                //data8_part not included because file has different prefix
            };
            return (fileData, testComparisonData);
        }

        public static (Dictionary<string, string>, List<string>) StandardCombineTestData_FourFilesAndMultipleRows_WithDiffExtension(string tempDirectory, string delimiter)
        {
            string header_all = $"Header1{delimiter}Header2";
            string data1_part = $"Value1{delimiter}Value2";
            string data2_part = $"Value3{delimiter}Value4";
            string data3_part = $"Value5{delimiter}Value6";
            string data4_part = $"Value7{delimiter}Value8";
            string data5_part = $"Value9{delimiter}Value10";
            string data6_part = $"Value11{delimiter}Value12";
            string data7_part = $"Value13{delimiter}Value14";
            string data8_part = $"Value15{delimiter}Value16";
            string fileName1 = Path.Combine(tempDirectory, "file1.dert");
            string fileName2 = Path.Combine(tempDirectory, "file2.dert");
            string fileName3 = Path.Combine(tempDirectory, "file3.dert");
            string fileName4 = Path.Combine(tempDirectory, "file4.txt");
            string data1 = $"{header_all}\n{data1_part}\n{data5_part}\n";
            string data2 = $"{header_all}\n{data2_part}\n{data6_part}\n";
            string data3 = $"{header_all}\n{data3_part}\n{data7_part}\n";
            string data4 = $"{header_all}\n{data4_part}\n{data8_part}\n";
            List<string> fileNames = new List<string> { fileName1, fileName2, fileName3, fileName4 };
            List<string> file_data = new List<string> { data1, data2, data3, data4 };
            Dictionary<string, string> fileData = new Dictionary<string, string>
            {
                { fileName1, data1 },
                { fileName2, data2 },
                { fileName3, data3 },
                { fileName4, data4 }
            };
            List<string> testComparisonData = new List<string> {
                header_all,
                data1_part,
                data2_part,
                data3_part,
                //data4_part, not included because file has different extension
                data5_part,
                data6_part,
                data7_part //,
                //data8_part not included because file has different extension
            };
            return (fileData, testComparisonData);
        }

        public static (Dictionary<string, string>, List<string>) StandardCombineTestData_FourFilesAndMultipleRows_MissingNewLine(string tempDirectory, string delimiter)
        {
            string header_all = $"Header1{delimiter}Header2";
            string data1_part = $"Value1{delimiter}Value2";
            string data2_part = $"Value3{delimiter}Value4";
            string data3_part = $"Value5{delimiter}Value6";
            string data4_part = $"Value7{delimiter}Value8";
            string data5_part = $"Value9{delimiter}Value10";
            string data6_part = $"Value11{delimiter}Value12";
            string data7_part = $"Value13{delimiter}Value14";
            string data8_part = $"Value15{delimiter}Value16";
            string fileName1 = Path.Combine(tempDirectory, "file1.txt");
            string fileName2 = Path.Combine(tempDirectory, "file2.txt");
            string fileName3 = Path.Combine(tempDirectory, "file3.txt");
            string fileName4 = Path.Combine(tempDirectory, "file4.txt");
            string data1 = $"{header_all}\n{data1_part}\n{data5_part}"; //missing new line at end of file
            string data2 = $"{header_all}\n{data2_part}\n{data6_part}"; //missing new line at end of file
            string data3 = $"{header_all}\n{data3_part}\n{data7_part}\n";
            string data4 = $"{header_all}\n{data4_part}\n{data8_part}\n";
            List<string> fileNames = new List<string> { fileName1, fileName2, fileName3, fileName4 };
            List<string> file_data = new List<string> { data1, data2, data3, data4 };
            Dictionary<string, string> fileData = new Dictionary<string, string>
            {
                { fileName1, data1 },
                { fileName2, data2 },
                { fileName3, data3 },
                { fileName4, data4 }
            };
            List<string> testComparisonData = new List<string> {
                header_all,
                data1_part,
                data2_part,
                data3_part,
                data4_part,
                data5_part,
                data6_part,
                data7_part,
                data8_part
            };
            return (fileData, testComparisonData);
        }

        #endregion file combine test data

        #region file append test data
        public static (Dictionary<string, string>, List<string>, string, string) AppendToFile_AppendsContent(string tempDirectory, string delimiter)
        {
            string sourceFile = Path.Combine(tempDirectory, "source.txt");
            string appendFile = Path.Combine(tempDirectory, "append.txt");
            string header_all = $"Header1{delimiter}Header2";
            string data1_part = $"Value1{delimiter}Value2";
            string data2_part = $"Value3{delimiter}Value4";
            string data3_part = $"Value5{delimiter}Value6";
            string data1 = $"{header_all}\n{data1_part}\n"; 
            string data2 = $"{header_all}\n{data2_part}\n{data3_part}\n";

            Dictionary<string, string> fileData = new Dictionary<string, string>
            {
                { sourceFile, data1 },
                { appendFile, data2 }
            };

            List<string> testComparisonData = new List<string> {
                header_all,
                data1_part,
                data2_part,
                data3_part
            };
            return (fileData, testComparisonData, sourceFile, appendFile);

        }

        public static (Dictionary<string, string>, List<string>, string, string) AppendToFile_AppendsContent_MissingNewline(string tempDirectory, string delimiter)
        {
            string sourceFile = Path.Combine(tempDirectory, "source.txt");
            string appendFile = Path.Combine(tempDirectory, "append.txt");
            string header_all = $"Header1{delimiter}Header2";
            string data1_part = $"Value1{delimiter}Value2";
            string data2_part = $"Value3{delimiter}Value4";
            string data3_part = $"Value5{delimiter}Value6";
            string data1 = $"{header_all}\n{data1_part}"; //missing new line at end of file
            string data2 = $"{header_all}\n{data2_part}\n{data3_part}\n";

            Dictionary<string, string> fileData = new Dictionary<string, string>
            {
                { sourceFile, data1 },
                { appendFile, data2 }
            };

            List<string> testComparisonData = new List<string> {
                header_all,
                data1_part,
                data2_part,
                data3_part
            };
            return (fileData, testComparisonData, sourceFile, appendFile);

        }

        public static (Dictionary<string, string>, List<string>, string, string) AppendToFile_AppendsContent_MissingNewlineWithoutIgnoringFirstRow(string tempDirectory, string delimiter)
        {
            string sourceFile = Path.Combine(tempDirectory, "source.txt");
            string appendFile = Path.Combine(tempDirectory, "append.txt");
            string header1 = $"Header1{delimiter}Header2";
            string header2 = $"Header1{delimiter}Header2";
            string data1_part = $"Value1{delimiter}Value2";
            string data2_part = $"Value3{delimiter}Value4";
            string data3_part = $"Value5{delimiter}Value6";
            string data1 = $"{header1}\n{data1_part}"; //missing new line at end of file
            string data2 = $"{header2}\n{data2_part}\n{data3_part}\n";

            Dictionary<string, string> fileData = new Dictionary<string, string>
            {
                { sourceFile, data1 },
                { appendFile, data2 }
            };

            List<string> testComparisonData = new List<string> {
                header1,
                data1_part,
                header2,
                data2_part,
                data3_part
            };
            return (fileData, testComparisonData, sourceFile, appendFile);

        }
        #endregion file append test data

        #region file combine header independent test data

        public static (Dictionary<string, string>, List<string>) CombineFilesHeaderIndependent_CreatesCombinedFile(string tempDirectory, string delimiter)
        {
            string header1 = $"Header1{delimiter}Header2";
            string header2 = $"Header3{delimiter}Header4";
            string data1_part = $"Value1{delimiter}Value2";
            string data2_part = $"Value3{delimiter}Value4";

            string fileName1 = Path.Combine(tempDirectory, "file1.txt");
            string fileName2 = Path.Combine(tempDirectory, "file2.txt");

            string data1 = $"{header1}\n{data1_part}\n";
            string data2 = $"{header2}\n{data2_part}\n";

            List<string> fileNames = new List<string> { fileName1, fileName2 };
            List<string> file_data = new List<string> { data1, data2 };

            Dictionary<string, string> fileData = new Dictionary<string, string>
            {
                { fileName1, data1 },
                { fileName2, data2 }
            };

            List<string> testComparisonData = new List<string> {
                $"{header1}{delimiter}{header2}",
                $"{data1_part}{delimiter}N/A{delimiter}N/A",
                $"N/A{delimiter}N/A{delimiter}{data2_part}"
            };

            return (fileData, testComparisonData);
        }

        public static (Dictionary<string, string>, List<string>) CombineFilesHeaderIndependent_CreatesCombinedFileWithFourFiles(string tempDirectory, string delimiter)
        {
            string header1 = $"Header1{delimiter}Header2";
            string header2 = $"Header3{delimiter}Header4";
            string header3 = $"{header1}{delimiter}Header5{delimiter}Header6";
            string header4 = $"{header1}{delimiter}{header2}{delimiter}Header7";
            string data1_part = $"Value1{delimiter}Value2";
            string data2_part = $"Value3{delimiter}Value4";
            string data3_part = $"Value5{delimiter}Value6{delimiter}Value7{delimiter}Value8";
            string data4_part = $"Value9{delimiter}Value10{delimiter}Value11{delimiter}Value12{delimiter}Value13";

            string fileName1 = Path.Combine(tempDirectory, "file1.txt");
            string fileName2 = Path.Combine(tempDirectory, "file2.txt");
            string fileName3 = Path.Combine(tempDirectory, "file3.txt");
            string fileName4 = Path.Combine(tempDirectory, "file4.txt");

            string data1 = $"{header1}\n{data1_part}\n";
            string data2 = $"{header2}\n{data2_part}\n";
            string data3 = $"{header3}\n{data3_part}\n";
            string data4 = $"{header4}\n{data4_part}\n";

            Dictionary<string, string> fileData = new Dictionary<string, string>
            {
                { fileName1, data1 },
                { fileName2, data2 },
                { fileName3, data3 },
                { fileName4, data4 }
            };

            List<string> testComparisonData = new List<string> {
                $"{header1}{delimiter}{header2}{delimiter}Header5{delimiter}Header6{delimiter}Header7",
                $"{data1_part}{delimiter}N/A{delimiter}N/A{delimiter}N/A{delimiter}N/A{delimiter}N/A",
                $"N/A{delimiter}N/A{delimiter}{data2_part}{delimiter}N/A{delimiter}N/A{delimiter}N/A",
                $"Value5{delimiter}Value6{delimiter}N/A{delimiter}N/A{delimiter}Value7{delimiter}Value8{delimiter}N/A",
                $"Value9{delimiter}Value10{delimiter}Value11{delimiter}Value12{delimiter}N/A{delimiter}N/A{delimiter}Value13"
            };

            return (fileData, testComparisonData);
        }

        public static (Dictionary<string, string>, List<string>) CombineFilesHeaderIndependent_CreatesCombinedFileWithFourFilesAndMultipleRows(string tempDirectory, string delimiter)
        {
            string header1 = $"Header1{delimiter}Header2";
            string header2 = $"Header3{delimiter}Header4";
            string header3 = $"{header1}{delimiter}Header5{delimiter}Header6";
            string header4 = $"{header1}{delimiter}{header2}{delimiter}Header7";
            
            string data1_part = $"Value1{delimiter}Value2";
            string data2_part = $"Value3{delimiter}Value4";
            string data3_part = $"Value5{delimiter}Value6{delimiter}Value7{delimiter}Value8\nValue9{delimiter}Value10{delimiter}Value11{delimiter}Value12\nValue13{delimiter}Value14{delimiter}Value15{delimiter}Value16\nValue17{delimiter}Value18{delimiter}Value19{delimiter}Value20";
            string data4_part = $"Value21{delimiter}Value22{delimiter}Value23{delimiter}Value24{delimiter}Value25\nValue26{delimiter}Value27{delimiter}Value28{delimiter}Value29{delimiter}Value30\nValue31{delimiter}Value32{delimiter}Value33{delimiter}Value34{delimiter}Value35\nValue36{delimiter}Value37{delimiter}Value38{delimiter}Value39{delimiter}Value40";

            string fileName1 = Path.Combine(tempDirectory, "file1.txt");
            string fileName2 = Path.Combine(tempDirectory, "file2.txt");
            string fileName3 = Path.Combine(tempDirectory, "file3.txt");
            string fileName4 = Path.Combine(tempDirectory, "file4.txt");

            string data1 = $"{header1}\n{data1_part}\n";
            string data2 = $"{header2}\n{data2_part}\n";
            string data3 = $"{header3}\n{data3_part}\n";
            string data4 = $"{header4}\n{data4_part}\n";

            Dictionary<string, string> fileData = new Dictionary<string, string>
            {
                { fileName1, data1 },
                { fileName2, data2 },
                { fileName3, data3 },
                { fileName4, data4 }
            };

            List<string> testComparisonData = new List<string> {
                $"{header1}{delimiter}{header2}{delimiter}Header5{delimiter}Header6{delimiter}Header7",
                $"{data1_part}{delimiter}N/A{delimiter}N/A{delimiter}N/A{delimiter}N/A{delimiter}N/A",
                $"N/A{delimiter}N/A{delimiter}{data2_part}{delimiter}N/A{delimiter}N/A{delimiter}N/A",
                $"Value5{delimiter}Value6{delimiter}N/A{delimiter}N/A{delimiter}Value7{delimiter}Value8{delimiter}N/A",
                $"Value9{delimiter}Value10{delimiter}N/A{delimiter}N/A{delimiter}Value11{delimiter}Value12{delimiter}N/A",
                $"Value13{delimiter}Value14{delimiter}N/A{delimiter}N/A{delimiter}Value15{delimiter}Value16{delimiter}N/A",
                $"Value17{delimiter}Value18{delimiter}N/A{delimiter}N/A{delimiter}Value19{delimiter}Value20{delimiter}N/A",
                $"Value21{delimiter}Value22{delimiter}Value23{delimiter}Value24{delimiter}N/A{delimiter}N/A{delimiter}Value25",
                $"Value26{delimiter}Value27{delimiter}Value28{delimiter}Value29{delimiter}N/A{delimiter}N/A{delimiter}Value30",
                $"Value31{delimiter}Value32{delimiter}Value33{delimiter}Value34{delimiter}N/A{delimiter}N/A{delimiter}Value35",
                $"Value36{delimiter}Value37{delimiter}Value38{delimiter}Value39{delimiter}N/A{delimiter}N/A{delimiter}Value40"
            };

            return (fileData, testComparisonData);

        }
            #endregion file combine header independent test data
        }
}
