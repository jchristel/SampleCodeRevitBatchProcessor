//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2025, Jan Christel
// All rights reserved.

// Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

// - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
// - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
// - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
//
// This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
// In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
// or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
//
//
//


using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using CsvHelper;
using CsvHelper.Configuration;
using System.Globalization;

namespace CSVHelperWrapper
{
    public class WriteToFile
    {
        // Stores a list of error messages
        public static List<string> ErrorHistory { get; private set; } = new List<string>();

        // Method to retrieve all stored errors
        public static List<string> GetErrorHistory()
        {
            // Return a copy to avoid direct modification
            return new List<string>(ErrorHistory);
        }

        // Method to clear errors if needed
        public static void ClearErrorHistory()
        {
            ErrorHistory.Clear();
        }

        /// <summary>
        /// Writes a column based text file with the specified header and dataand delimiter.
        /// </summary>
        /// <param name="filePath">The fully qualified file path of the file to be written. </param>
        /// <param name="header">The header row. Can be an empty list or null if no header is to be written.</param>
        /// <param name="data">The data to be written to file. Can be an empty list or null if no data is to be written.</param>
        /// <param name="writeType">W for overwriting any existing data. A for appending data to existing file.</param>
        /// <param name="bom">Byte order mark. Default is null.</param>
        /// <param name="delimiter">The delimiter to be used. Default is ','</param>
        /// <returns>True if file was written without an exception. Otherwise False.</returns>
        public static bool WriteToTextFile(string filePath, List<string> header, List<List<string>> data, string writeType = "w", byte[] bom = null, string delimiter = ",")
        {
            try
            {
                var append = writeType == "a";
                var encoding = bom != null && bom == BOMValue.UTF_16_LITTLE_ENDIAN ? Encoding.Unicode :
                               bom != null && bom == BOMValue.UTF_16_BIG_ENDIAN ? Encoding.BigEndianUnicode :
                               bom != null && bom == BOMValue.UTF_32_LITTLE_ENDIAN ? Encoding.UTF32 :
                               bom != null && bom == BOMValue.UTF_32_BIG_ENDIAN ? Encoding.UTF32 :
                               Encoding.UTF8;

                using (var writer = new FileStream(filePath, append ? FileMode.Append : FileMode.Create, FileAccess.Write))
                {
                    // Write BOM only if not appending
                    if (!append && bom != null)
                    {
                        writer.Write(bom, 0, bom.Length);
                    }

                    using (var streamWriter = new StreamWriter(writer, encoding))
                    {
                        var config = new CsvConfiguration(CultureInfo.InvariantCulture)
                        {
                            Delimiter = delimiter
                        };

                        using (var csv = new CsvWriter(streamWriter, config))
                        {
                            // Write header if provided
                            if (!append && header != null && header.Count > 0)
                            {
                                foreach (var field in header)
                                {
                                    csv.WriteField(field);
                                }
                                csv.NextRecord();
                            }

                            // Write data rows if there are any
                            if (data != null && data.Count > 0)
                            {
                                foreach (var row in data)
                                {
                                    foreach (var field in row)
                                    {
                                        csv.WriteField(field);
                                    }
                                    csv.NextRecord();
                                }
                            }
                        }
                    }
                }
                // Success
                return true; 
            }
            catch (Exception ex)
            {
                ErrorHistory.Add($"Error at {DateTime.Now}: {ex.Message}");

                // Failure
                return false; 
            }
        }
    }
}