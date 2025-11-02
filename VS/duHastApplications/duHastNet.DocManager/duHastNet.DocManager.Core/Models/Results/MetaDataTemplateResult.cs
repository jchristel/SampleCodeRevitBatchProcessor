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

namespace duHastNet.DocManager.Core.Models.Results;

/// <summary>
/// Result class for metadata template file operations
/// Contains either the list of column headers on success, or error information on failure
/// </summary>
public class MetaDataTemplateResult : ResultBase
{
    /// <summary>
    /// List of column headers extracted from the template file
    /// Empty list if operation failed
    /// </summary>
    public List<string> ColumnHeaders { get; set; } = new List<string>();

    /// <summary>
    /// The file path that was processed
    /// </summary>
    public string? FilePath { get; set; }

    /// <summary>
    /// Indicates whether the template file was read successfully
    /// </summary>
    public bool IsReadSuccessful { get; set; }

    /// <summary>
    /// Implementation of abstract Success property - maps to IsReadSuccessful
    /// </summary>
    public override bool Success
    {
        get => IsReadSuccessful;
        set => IsReadSuccessful = value;
    }

    /// <summary>
    /// Creates a successful result with column headers
    /// </summary>
    /// <param name="filePath">Path to the template file that was read</param>
    /// <param name="columnHeaders">List of column headers found in the file</param>
    /// <returns>Success result with column headers</returns>
    public static MetaDataTemplateResult CreateSuccess(string filePath, List<string> columnHeaders)
    {
        return new MetaDataTemplateResult
        {
            IsReadSuccessful = true,
            FilePath = filePath,
            ColumnHeaders = columnHeaders,
            Message = $"Successfully read {columnHeaders.Count} column headers from template file"
        };
    }

    /// <summary>
    /// Creates a failure result with error message
    /// </summary>
    /// <param name="errorMessage">Error message describing the failure</param>
    /// <returns>Failure result with error information</returns>
    public static MetaDataTemplateResult CreateFailure(string errorMessage)
    {
        var result = new MetaDataTemplateResult
        {
            IsReadSuccessful = false,
            Message = errorMessage
        };
        result.AddError(errorMessage);
        return result;
    }

    /// <summary>
    /// Creates a failure result with error message and file path
    /// </summary>
    /// <param name="filePath">Path to the file that failed to read</param>
    /// <param name="errorMessage">Error message describing the failure</param>
    /// <returns>Failure result with error information</returns>
    public static MetaDataTemplateResult CreateFailure(string filePath, string errorMessage)
    {
        var result = new MetaDataTemplateResult
        {
            IsReadSuccessful = false,
            FilePath = filePath,
            Message = errorMessage
        };
        result.AddError(errorMessage);
        return result;
    }
}
