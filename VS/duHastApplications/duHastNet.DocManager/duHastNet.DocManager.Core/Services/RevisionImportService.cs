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
using duHastNet.DocManager.Core.Interfaces;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.Results;
using System.Globalization;

namespace duHastNet.DocManager.Core.Services;

/// <summary>
/// Service responsible for importing revisions from CSV format
/// Handles creation of new revisions and updates to existing revisions
/// </summary>
public class RevisionImportService
{
    private readonly IUnitOfWork _unitOfWork;

    public RevisionImportService(IUnitOfWork unitOfWork)
    {
        _unitOfWork = unitOfWork ?? throw new ArgumentNullException(nameof(unitOfWork));
    }

    /// <summary>
    /// Imports revisions from a CSV file
    /// </summary>
    /// <param name="filePath">Path to CSV file to import</param>
    /// <returns>Import result with statistics and any errors</returns>
    public async Task<ImportResult> ImportRevisionsAsync(string filePath)
    {
        var result = new ImportResult();
        var errors = new List<string>();
        int revisionsProcessed = 0;
        int revisionsCreated = 0;
        int revisionsUpdated = 0;
        int revisionsSkipped = 0;

        try
        {
            using var reader = new StreamReader(filePath);
            using var csv = new CsvReader(reader, new CsvConfiguration(CultureInfo.InvariantCulture)
            {
                HasHeaderRecord = true,
                MissingFieldFound = null // Don't throw on missing fields
            });

            // Read header
            csv.Read();
            csv.ReadHeader();

            int rowNumber = 1; // Start at 1 for first data row

            // Read each row
            while (await Task.Run(() => csv.Read()))
            {
                rowNumber++;
                revisionsProcessed++;

                try
                {
                    var importRow = ParseRow(csv);

                    if (importRow.Id.Equals("new", StringComparison.OrdinalIgnoreCase))
                    {
                        // Create new revision
                        var createResult = await CreateNewRevisionAsync(importRow, rowNumber);

                        if (createResult.Success)
                        {
                            revisionsCreated++;
                        }
                        else
                        {
                            errors.AddRange(createResult.Errors);
                            revisionsSkipped++;
                        }
                    }
                    else
                    {
                        // Update existing revision
                        var updateResult = await UpdateExistingRevisionAsync(importRow, rowNumber);

                        if (updateResult.Success)
                        {
                            revisionsUpdated++;
                        }
                        else
                        {
                            errors.AddRange(updateResult.Errors);
                            revisionsSkipped++;
                        }
                    }
                }
                catch (Exception ex)
                {
                    errors.Add($"Row {rowNumber}: {ex.Message}");
                    revisionsSkipped++;
                }
            }

            // Set result
            result.IsImportSuccessful = errors.Count == 0;
            result.DocumentsProcessed = revisionsProcessed;  // Reusing DocumentsProcessed for revisions
            result.DocumentsCreated = revisionsCreated;      // Reusing for revisions created
            result.DocumentsSkipped = revisionsSkipped;      // Reusing for revisions skipped
            result.Message = errors.Count == 0
                ? $"Import completed: {revisionsCreated} revisions created, {revisionsUpdated} updated"
                : $"Import completed with errors: {revisionsCreated} created, {revisionsUpdated} updated, {revisionsSkipped} skipped";

            foreach (var error in errors)
            {
                result.AddError(error);
            }

            return result;
        }
        catch (Exception ex)
        {
            return ImportResult.CreateFailure($"Import failed: {ex.Message}");
        }
    }

    /// <summary>
    /// Parses a CSV row into a RevisionImportRow object
    /// </summary>
    private RevisionImportRow ParseRow(CsvReader csv)
    {
        var row = new RevisionImportRow
        {
            Id = csv.GetField("Id") ?? string.Empty,
            RevisionDateString = csv.GetField("Revision Date") ?? string.Empty,
            Description = csv.GetField("Description") ?? string.Empty
            // Note: Document Count is read-only for reference, not imported
        };

        return row;
    }

    /// <summary>
    /// Creates a new revision from import row
    /// </summary>
    private async Task<ValidationResult> CreateNewRevisionAsync(
        RevisionImportRow importRow,
        int rowNumber)
    {
        try
        {
            // Parse and validate revision date
            if (!DateTime.TryParse(importRow.RevisionDateString, out DateTime revisionDate))
            {
                return ValidationResult.CreateFailure(
                    $"Row {rowNumber}: Invalid Revision Date '{importRow.RevisionDateString}'. Use format: yyyy-MM-dd");
            }

            // Create new revision
            var revision = new Revision(revisionDate, importRow.Description);

            // Check if revision with same date and description already exists
            var existingRevisions = await _unitOfWork.Revisions.GetRevisionsByDateAsync(revisionDate);
            var conflictingRevision = existingRevisions.FirstOrDefault(r => revision.Conflicts(r));

            if (conflictingRevision != null)
            {
                return ValidationResult.CreateFailure(
                    $"Row {rowNumber}: Revision with date {revisionDate:yyyy-MM-dd} and description '{importRow.Description}' already exists");
            }

            // Insert revision
            await _unitOfWork.Revisions.InsertAsync(revision);

            return ValidationResult.CreateSuccess();
        }
        catch (Exception ex)
        {
            return ValidationResult.CreateFailure($"Row {rowNumber}: {ex.Message}");
        }
    }

    /// <summary>
    /// Updates an existing revision from import row
    /// </summary>
    private async Task<ValidationResult> UpdateExistingRevisionAsync(
        RevisionImportRow importRow,
        int rowNumber)
    {
        try
        {
            // Parse revision ID
            if (!int.TryParse(importRow.Id, out int revisionId))
            {
                return ValidationResult.CreateFailure($"Row {rowNumber}: Invalid revision Id '{importRow.Id}'");
            }

            // Get existing revision
            var revision = await _unitOfWork.Revisions.GetByIdAsync(revisionId);
            if (revision == null)
            {
                return ValidationResult.CreateFailure($"Row {rowNumber}: Revision with Id {revisionId} not found");
            }

            bool revisionChanged = false;

            // Parse and check for revision date change
            if (!string.IsNullOrWhiteSpace(importRow.RevisionDateString))
            {
                if (DateTime.TryParse(importRow.RevisionDateString, out DateTime newRevisionDate))
                {
                    if (revision.RevisionDate.Date != newRevisionDate.Date)
                    {
                        revision.RevisionDate = newRevisionDate;
                        revisionChanged = true;
                    }
                }
                else
                {
                    return ValidationResult.CreateFailure(
                        $"Row {rowNumber}: Invalid Revision Date '{importRow.RevisionDateString}'. Use format: yyyy-MM-dd");
                }
            }

            // Check for description change
            var newDescription = importRow.Description ?? string.Empty;
            var currentDescription = revision.Description ?? string.Empty;
            
            if (currentDescription != newDescription)
            {
                revision.Description = string.IsNullOrWhiteSpace(newDescription) ? null : newDescription;
                revisionChanged = true;
            }

            // Update revision if changed
            if (revisionChanged)
            {
                await _unitOfWork.Revisions.UpdateAsync(revision);
            }

            return ValidationResult.CreateSuccess();
        }
        catch (Exception ex)
        {
            return ValidationResult.CreateFailure($"Row {rowNumber}: {ex.Message}");
        }
    }

    /// <summary>
    /// Represents a row from the import CSV
    /// </summary>
    private class RevisionImportRow
    {
        public string Id { get; set; } = string.Empty;
        public string RevisionDateString { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
    }
}
