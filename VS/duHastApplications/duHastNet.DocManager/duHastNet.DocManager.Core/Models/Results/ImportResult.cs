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

namespace duHastNet.DocManager.Core.Models.Results;

/// <summary>
/// Result of document import operation
/// </summary>
public class ImportResult : ResultBase
{
    /// <summary>
    /// Indicates whether the import was successful
    /// </summary>
    public bool IsImportSuccessful { get; set; }

    /// <summary>
    /// Total number of documents processed during import
    /// </summary>
    public int DocumentsProcessed { get; set; }

    /// <summary>
    /// Number of documents successfully created
    /// </summary>
    public int DocumentsCreated { get; set; }

    /// <summary>
    /// Number of documents skipped (duplicates, etc.)
    /// </summary>
    public int DocumentsSkipped { get; set; }

    /// <summary>
    /// Number of revision batches created during import
    /// </summary>
    public int RevisionsCreated { get; set; }

    /// <summary>
    /// Implementation of abstract Success property - maps to IsImportSuccessful
    /// </summary>
    public override bool Success
    {
        get => IsImportSuccessful;
        set => IsImportSuccessful = value;
    }

    /// <summary>
    /// Initializes a new instance of ImportResult with default message
    /// </summary>
    public ImportResult()
    {
        Message = "Document import completed successfully";
    }

    /// <summary>
    /// Creates a successful import result
    /// </summary>
    /// <param name="documentsProcessed">Total documents processed</param>
    /// <param name="documentsCreated">Documents successfully created</param>
    /// <param name="documentsSkipped">Documents skipped</param>
    /// <param name="revisionsCreated">Revisions created</param>
    /// <returns>ImportResult with IsImportSuccessful = true</returns>
    public static ImportResult CreateSuccess(int documentsProcessed, int documentsCreated,
        int documentsSkipped, int revisionsCreated)
    {
        return new ImportResult
        {
            IsImportSuccessful = true,
            DocumentsProcessed = documentsProcessed,
            DocumentsCreated = documentsCreated,
            DocumentsSkipped = documentsSkipped,
            RevisionsCreated = revisionsCreated
        };
    }

    /// <summary>
    /// Creates a failed import result with error messages
    /// </summary>
    /// <param name="errors">Error messages</param>
    /// <returns>ImportResult with IsImportSuccessful = false</returns>
    public static ImportResult CreateFailure(params string[] errors)
    {
        var result = new ImportResult { IsImportSuccessful = false };

        foreach (var error in errors)
        {
            result.AddError(error);
        }

        // Set Message to summarize the failure
        result.Message = errors.Length > 0
            ? (errors.Length == 1 ? errors[0] : $"Import failed with {errors.Length} errors")
            : "Import failed";

        return result;
    }
}