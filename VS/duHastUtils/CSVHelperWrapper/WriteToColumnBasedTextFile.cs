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
using System.Linq;
using System.Text;

namespace duHastNet.FileIOWrapper
{
    public class WriteToColumnBasedTextFile : WrapperBase
    {
        // same values as python's csv.QUOTE_MINIMAL, QUOTE_ALL, QUOTE_NONNUMERIC and QUOTE_NONE
        public const int QuoteMinimal = 0;
        public const int QuoteAll = 1;
        public const int QuoteNonNumeric = 2;
        public const int QuoteNone = 3;

        /// <summary>
        /// Writes a column based text file with the specified header and dataand delimiter.
        /// </summary>
        /// <param name="filePath">The fully qualified file path of the file to be written. </param>
        /// <param name="header">The header row. Can be an empty list or null if no header is to be written.</param>
        /// <param name="data">The data to be written to file. Can be an empty list or null if no data is to be written.</param>
        /// <param name="writeType">W for overwriting any existing data. A for appending data to existing file.</param>
        /// <param name="bom">Byte order mark. Default is null.</param>
        /// <param name="delimiter">The delimiter to be used. Default is ','</param>
        /// <param name="quoting">Quoting style, matching python's csv constants: 0 = minimal (default, only fields containing the delimiter, a quote or a line break are quoted), 1 = all fields quoted, 2 = non numeric fields quoted, 3 = none (no quoting or escaping).</param>
        /// <param name="encodingName">Name of the encoding to write the file in (a .net encoding name, e.g. 'utf-8', 'iso-8859-1', 'windows-1252'). Default is null: utf-8. Ignored if a byte order mark is supplied, in that case the encoding is derived from the byte order mark.</param>
        /// <returns>True if file was written without an exception. Otherwise False.</returns>
        public bool WriteToTextFile(string filePath, List<string> header, List<List<string>> data, string writeType = "w", byte[] bom = null, string delimiter = ",", int quoting = 0, string encodingName = null)
        {
            try
            {
                var append = writeType == "a";
                var encoding = GetEncodingFromBom(bom, encodingName);

                using var writer = new FileStream(filePath, append ? FileMode.Append : FileMode.Create, FileAccess.Write);

                // Write BOM only if not appending
                if (!append && bom != null)
                {
                    writer.Write(bom, 0, bom.Length);
                }

                using var streamWriter = new StreamWriter(writer, encoding);

                var config = new CsvConfiguration(CultureInfo.InvariantCulture)
                {
                    Delimiter = delimiter,
                    // matches the line endings previously written by the python writer
                    NewLine = "\n"
                };

                switch (quoting)
                {
                    case QuoteAll:
                        config.ShouldQuote = args => true;
                        break;
                    case QuoteNonNumeric:
                        config.ShouldQuote = args => !double.TryParse(args.Field, NumberStyles.Any, CultureInfo.InvariantCulture, out _) || args.Field.Length == 0;
                        break;
                    case QuoteNone:
                        config.Mode = CsvMode.NoEscape;
                        break;
                    case QuoteMinimal:
                        break;
                    default:
                        throw new ArgumentOutOfRangeException(nameof(quoting), quoting, "Quoting must be 0 (minimal), 1 (all), 2 (non numeric) or 3 (none).");
                }

                using var csv = new CsvWriter(streamWriter, config);

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

                return true;
            }
            catch (Exception ex)
            {
                ErrorHistory.Add($"Error at {DateTime.Now}: {ex.Message}");
                return false;
            }
        }

        // Extract the encoding logic into a separate method for better readability
        private static Encoding GetEncodingFromBom(byte[] bom, string encodingName)
        {
            if (bom == null)
            {
                if (string.IsNullOrWhiteSpace(encodingName)) return new UTF8Encoding(false);

                // makes code page based encodings (windows-1252...) available
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                var named = Encoding.GetEncoding(encodingName);
                // the byte order mark is only ever written if requested, so do not let the encoding emit one
                if (named.CodePage == 65001) return new UTF8Encoding(false);
                if (named.CodePage == 1200) return new UnicodeEncoding(false, false);
                if (named.CodePage == 1201) return new UnicodeEncoding(true, false);
                return named;
            }

            if (bom.SequenceEqual(BOMValue.UTF_16_LITTLE_ENDIAN))
                return new UnicodeEncoding(false, false);
            if (bom.SequenceEqual(BOMValue.UTF_16_BIG_ENDIAN))
                return new UnicodeEncoding(true, false);
            if (bom.SequenceEqual(BOMValue.UTF_32_LITTLE_ENDIAN))
                return new UTF32Encoding(false, false);
            if (bom.SequenceEqual(BOMValue.UTF_32_BIG_ENDIAN))
                return new UTF32Encoding(true, false); // Big-endian UTF-32

            return new UTF8Encoding(false);
        }
    }
}