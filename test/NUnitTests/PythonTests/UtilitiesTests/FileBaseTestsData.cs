namespace PythonTests.UtilitiesTests
{
    public static class FileBaseTestsData
    {
       
        public static string StripNonAscii(string input)
        {
            // Remove non-ASCII characters from input string
            // https://stackoverflow.com/questions/1120198/most-efficient-way-to-remove-special-characters-from-string
            // used to compare data read from file with data written to file
            return new string(input.Where(c => c <= 127).ToArray());
        }

        public static (string fileName, List<string> header, List<List<string>> data) StandardTestData_HeaderAndData(string tempDirectory, char delimiter)
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

        public static (string fileName, List<string> header, List<List<string>> data) StandardTestData_HeaderOnly(string tempDirectory, char delimiter)
        {
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> { "Header1", "Header2" };
            List<List<string>> data = new List<List<string>>(); // No data rows
            return (fileName, header, data);
        }

        public static (string fileName, List<string> header, List<List<string>> data) StandardTestData_DataOnly(string tempDirectory, char delimiter)
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

        public static (string fileName, List<string> header, List<List<string>> data) DelimitedTestData_DataOnly(string tempDirectory,char delimiter)
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

        public static (string fileName, List<string> header, List<List<string>> data) DelimitedTestData_HeaderOnly(string tempDirectory, char delimiter)
        {
            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> { $"Header1{delimiter}Part1", $"Header2{delimiter}Part2" };// Header containing delimiter
            List<List<string>> data = new List<List<string>>(); // No data rows
            return (fileName, header, data);
        }

        public static (string fileName, List<string> header, List<List<string>> data) DelimitedTestData_HeaderAndData(string tempDirectory, char delimiter)
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


        public static (string fileName, List<string> header, List<List<string>> data) NonASCIITestData(string tempDirectory, char delimiter)
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

        public static (string fileName, List<string> header, List<List<string>> data) NonUTF8TestData_DataOnly(string tempDirectory, char delimiter)
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

        public static (string fileName, List<string> header, List<List<string>> data) NonUTF8TestData_HeaderOnly(string tempDirectory, char delimiter)
        {
            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> { "Hëader1", "Hëader2" }; // Non-UTF-8 characters in header
            List<List<string>> data = new List<List<string>>(); // No data rows
            return (fileName, header, data);
        }

        public static (string fileName, List<string> header, List<List<string>> data) NonUTF8TestData_HeaderAndData(string tempDirectory, char delimiter)
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

        public static (string fileName, List<string> header, List<List<string>> data) NonUTF8AndDelimitedTestData_DataOnly(string tempDirectory, char delimiter)
        {
            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string> { "Header1", "Header2" };
            List<List<string>> data = new List<List<string>>
            {
                new List<string> { "Value1", "Value2" },
                new List<string> { "Value3", $"Välue4{delimiter}Part" } // Non-UTF-8 character and delimiter in data
            };
            return (fileName, header, data);
        }

        public static (string fileName, List<string> header, List<List<string>> data) NonUTF8AndDelimitedTestData_HeaderOnly(string tempDirectory, char delimiter)
        {
            // Arrange
            string fileName = Path.Combine(tempDirectory, "report.csv");
            List<string> header = new List<string>{ $"Hëader1{delimiter}Part1", $"Hëader2{delimiter}Part2" }; // Non-UTF-8 characters and delimiter in header

            List<List<string>> data = new List<List<string>>(); // No data rows
            return (fileName, header, data);
        }


        public static (string fileName, List<string> header, List<List<string>> data) ArrangeMaxFieldSizeTestData(string tempDirectory, char delimiter)
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

    }
}
