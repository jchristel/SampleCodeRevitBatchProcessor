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


using CsvHelper;
using CsvHelper.Configuration;
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;

namespace duHastNet.FileIOWrapper
{
    public class ReadFromColumnBasedTextFile : WrapperBase
    {

        /// <summary>
        /// Reads a column based text file with the specified delimiter.
        /// </summary>
        /// <param name="filePath">The fully qualified file path of the file to be read.</param>
        /// <param name="delimiter">The delimiter to be used. Default is ','</param>
        /// <returns>A list of nested lists representing each row in the file read.</returns>
        public List<List<string>> ReadFromTextFile(string filePath, string delimiter = ",")
        {
            return ReadFromTextFileInternal(filePath, int.MaxValue, delimiter);
        }

        /// <summary>
        /// Reads a specified number of rows from a column based text file with the specified delimiter.
        /// </summary>
        /// <param name="filePath">The fully qualified file path of the file to be read.</param>
        /// <param name="delimiter">The delimiter to be used. Default is ','</param>
        /// /// <param name="rowCount">The number of rows to read from the file.</param>
        /// <returns>A list of nested lists representing each row read from the file.</returns>
        public List<List<string>> ReadRowsFromTextFile(string filePath, string delimiter = ",", int rowCount = 1)
        {
            return ReadFromTextFileInternal(filePath, rowCount, delimiter);
        }

        /// <summary>
        /// Internal method to read rows from a column based text file with the specified delimiter.
        /// </summary>
        /// <param name="filePath">The fully qualified file path of the file to be read.</param>
        /// <param name="rowCount">The number of rows to read from the file. Use int.MaxValue to read all rows.</param>
        /// <param name="delimiter">The delimiter to be used. Default is ','</param>
        /// <returns>A list of nested lists representing each row read from the file.</returns>
        private List<List<string>> ReadFromTextFileInternal(string filePath, int rowCount, string delimiter)
        {
            var records = new List<List<string>>();

            try
            {
                using var reader = new StreamReader(filePath);
                using var csv = new CsvReader(reader, new CsvConfiguration(CultureInfo.InvariantCulture)
                {
                    BadDataFound = null, // Don't throw on bad data
                    Delimiter = delimiter
                });
                int currentRow = 0;
                while (csv.Read() && currentRow < rowCount)
                {
                    var row = new List<string>();
                    for (int i = 0; i < csv.Parser.Count; i++)
                    {
                        row.Add(csv.GetField(i));
                    }
                    records.Add(row);
                    currentRow++;
                }
            }
            catch (Exception ex)
            {
                ErrorHistory.Add($"Error reading file: {ex.Message}");

                //if an error occured while reading the file, return an empty list
                return [];
            }

            return records;
        }
    }
}
