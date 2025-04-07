
using System;
using System.Collections.Generic;
using System.IO;
using CsvHelper;
using CsvHelper.Configuration;
using System.Globalization;

namespace CSVHelperWrapper
{
    public class WriteToFile
    {
        public static bool WriteToCsv(string filePath, List<string> header, List<List<string>> data)
        {
            try
            {
                using (var writer = new StreamWriter(filePath))
                using (var csv = new CsvWriter(writer, new CsvConfiguration(CultureInfo.InvariantCulture)))
                {
                    // Write header if provided
                    if (header != null && header.Count > 0)
                    {
                        foreach (var field in header)
                        {
                            csv.WriteField(field);
                        }
                        csv.NextRecord();
                    }

                    // Write data rows
                    foreach (var row in data)
                    {
                        foreach (var field in row)
                        {
                            csv.WriteField(field);
                        }
                        csv.NextRecord();
                    }
                }
                return true; // Success
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error writing to CSV: {ex.Message}");
                return false; // Failure
            }
        }
    }
}