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
using System.Threading.Tasks;


namespace duHastNet.Utils.Logging
{
    public class SimpleLogger
    {
        private readonly string _filePath;
        private readonly List<string> _errorMessages = new List<string>(); // Stores exception messages

        public SimpleLogger(string filePath)
        {
            _filePath = filePath;
        }

        public IReadOnlyList<string> ErrorMessages => _errorMessages.AsReadOnly(); // Expose errors safely

        public void LogMessages(List<(string message, WPF.Stores.MessageTypes type)> messages)
        {
            var records = new List<LogEntry>();
            foreach (var (message, type) in messages)
            {
                records.Add(new LogEntry
                {
                    Message = message,
                    Type = type,
                    Timestamp = DateTime.Now
                });
            }

            StreamWriter writer = null;
            CsvWriter csv = null;
            try
            {
                writer = new StreamWriter(_filePath, true);
                csv = new CsvWriter(writer, new CsvConfiguration(CultureInfo.InvariantCulture));

                // Write records in custom order
                foreach (var record in records)
                {
                    csv.WriteField(record.Timestamp);
                    csv.WriteField(record.Type);
                    csv.WriteField(record.Message);
                }

            }
            catch (Exception ex)
            {
                _errorMessages.Add($"Error writing logs: {ex.Message}"); // Store errors in the list
            }
            finally
            {
                csv?.Dispose();
                writer?.Dispose();
            }
        }

        public async Task LogMessagesAsync(List<(string message, Utils.WPF.Stores.MessageTypes type)> messages)
        {
            var records = new List<LogEntry>();
            foreach (var (message, type) in messages)
            {
                records.Add(new LogEntry
                {
                    Message = message,
                    Type = type,
                    Timestamp = DateTime.Now
                });
            }

            try
            {
                using (StreamWriter writer = new StreamWriter(_filePath, true))
                using (CsvWriter csv = new CsvWriter(writer, new CsvConfiguration(CultureInfo.InvariantCulture)))
                {
                    // Write records field-by-field in the desired order
                    foreach (var record in records)
                    {
                        csv.WriteField(record.Timestamp);
                        csv.WriteField(record.Type);
                        csv.WriteField(record.Message);
                        await csv.NextRecordAsync();
                    }

                }
            }
            catch (Exception ex)
            {
                _errorMessages.Add($"Error writing logs: {ex.Message}"); // Store errors
            }
        }

        public void LogMessagesFireAndForget(List<(string message, Utils.WPF.Stores.MessageTypes type)> messages)
        {
            Task.Run(async () =>
            {
                try
                {
                    await LogMessagesAsync(messages);
                }
                catch (Exception ex)
                {
                    _errorMessages.Add($"Logging error: {ex.Message}"); // Store errors
                }
            });
        }
    }
}
