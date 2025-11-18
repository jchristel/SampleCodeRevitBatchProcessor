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

using CsvHelper;
using CsvHelper.Configuration;
using duHastNet.DocManager.Core.Interfaces;
using duHastNet.DocManager.Core.Models.Results;
using System.Globalization;

namespace duHastNet.DocManager.Core.Services;

/// <summary>
/// Service for reading metadata template files (CSV format) and extracting column headers
/// Used for Aconex metadata mapping configuration
/// </summary>
public class MetaDataTemplateService : IMetaDataTemplateService
{
    /// <summary>
    /// Reads a CSV template file and extracts the column headers from the first row
    /// </summary>
    /// <param name="filePath">Full path to the CSV template file</param>
    /// <returns>Result containing the list of column headers if successful, or error information if failed</returns>
    public async Task<MetaDataTemplateResult> ReadColumnHeadersAsync(string filePath)
    {
        try
        {
            // Validate input
            if (string.IsNullOrWhiteSpace(filePath))
            {
                return MetaDataTemplateResult.CreateFailure("File path cannot be null or empty");
            }

            // Validate file
            if (!IsValidCsvFile(filePath))
            {
                return MetaDataTemplateResult.CreateFailure(filePath, 
                    "Invalid file: Must be a CSV file (.csv extension) and must exist");
            }

            // Read the CSV file headers
            var columnHeaders = new List<string>();

            // Configure CSV reader to handle various CSV formats
            var config = new CsvConfiguration(CultureInfo.InvariantCulture)
            {
                // Allow flexible handling of missing fields
                MissingFieldFound = null,
                // Handle bad data gracefully
                BadDataFound = null,
                // Trim whitespace from headers
                TrimOptions = TrimOptions.Trim,
                // Detect delimiter automatically if possible
                DetectDelimiter = true,
                DetectDelimiterValues = new[] { ",", ";", "\t", "|" },
                // Allow comments in CSV
                AllowComments = true,
                Comment = '#'
            };

            using (var reader = new StreamReader(filePath))
            using (var csv = new CsvReader(reader, config))
            {
                // Read the header record
                await csv.ReadAsync().ConfigureAwait(false);
                csv.ReadHeader();

                // Get the header names
                if (csv.HeaderRecord != null)
                {
                    columnHeaders.AddRange(csv.HeaderRecord);
                }
            }

            // Validate that we found headers
            if (columnHeaders.Count == 0)
            {
                return MetaDataTemplateResult.CreateFailure(filePath,
                    "No column headers found in the CSV file. The file may be empty or improperly formatted.");
            }

            // Remove any empty or whitespace-only headers
            columnHeaders = columnHeaders
                .Where(h => !string.IsNullOrWhiteSpace(h))
                .Select(h => h.Trim())
                .ToList();

            if (columnHeaders.Count == 0)
            {
                return MetaDataTemplateResult.CreateFailure(filePath,
                    "All column headers were empty or whitespace. The CSV file must have valid column names.");
            }

            // Check for duplicate headers
            var duplicates = columnHeaders
                .GroupBy(h => h)
                .Where(g => g.Count() > 1)
                .Select(g => g.Key)
                .ToList();

            if (duplicates.Any())
            {
                var result = MetaDataTemplateResult.CreateSuccess(filePath, columnHeaders);
                result.AddWarning($"Found duplicate column headers: {string.Join(", ", duplicates)}. " +
                    "This may cause issues with metadata mapping.");
                return result;
            }

            return MetaDataTemplateResult.CreateSuccess(filePath, columnHeaders);
        }
        catch (IOException ioEx)
        {
            return MetaDataTemplateResult.CreateFailure(filePath,
                $"File access error: {ioEx.Message}. The file may be locked or in use by another application.");
        }
        catch (UnauthorizedAccessException uaEx)
        {
            return MetaDataTemplateResult.CreateFailure(filePath,
                $"Access denied: {uaEx.Message}. Check file permissions.");
        }
        catch (CsvHelperException csvEx)
        {
            return MetaDataTemplateResult.CreateFailure(filePath,
                $"CSV parsing error: {csvEx.Message}. The file may not be a valid CSV format.");
        }
        catch (Exception ex)
        {
            return MetaDataTemplateResult.CreateFailure(filePath,
                $"Unexpected error reading template file: {ex.Message}");
        }
    }

    /// <summary>
    /// Validates that a file path is a valid CSV file
    /// </summary>
    /// <param name="filePath">Full path to the file to validate</param>
    /// <returns>True if the file exists and has a .csv extension, false otherwise</returns>
    public bool IsValidCsvFile(string filePath)
    {
        if (string.IsNullOrWhiteSpace(filePath))
        {
            return false;
        }

        // Check if file exists
        if (!File.Exists(filePath))
        {
            return false;
        }

        // Check file extension
        var extension = Path.GetExtension(filePath);
        return string.Equals(extension, ".csv", StringComparison.OrdinalIgnoreCase);
    }
}
