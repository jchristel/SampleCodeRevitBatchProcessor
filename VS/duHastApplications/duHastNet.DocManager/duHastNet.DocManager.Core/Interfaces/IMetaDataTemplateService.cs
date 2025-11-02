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

using duHastNet.DocManager.Core.Models.Results;

namespace duHastNet.DocManager.Core.Interfaces;

/// <summary>
/// Interface for reading metadata template files and extracting column headers
/// Currently supports CSV format for Aconex metadata templates
/// </summary>
public interface IMetaDataTemplateService
{
    /// <summary>
    /// Reads a CSV template file and extracts the column headers from the first row
    /// </summary>
    /// <param name="filePath">Full path to the CSV template file</param>
    /// <returns>Result containing the list of column headers if successful, or error information if failed</returns>
    /// <remarks>
    /// This method:
    /// - Validates that the file exists and is a CSV file
    /// - Reads only the first row of the CSV file
    /// - Returns all column names found in the first row
    /// - Handles common CSV parsing issues (quotes, delimiters, etc.)
    /// </remarks>
    Task<MetaDataTemplateResult> ReadColumnHeadersAsync(string filePath);

    /// <summary>
    /// Validates that a file path is a valid CSV file
    /// </summary>
    /// <param name="filePath">Full path to the file to validate</param>
    /// <returns>True if the file exists and has a .csv extension, false otherwise</returns>
    bool IsValidCsvFile(string filePath);
}
