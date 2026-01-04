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
using duHastNet.DocManager.Core.Models.Database;
using duHastNet.DocManager.Core.Models.Results;
using System.Globalization;

namespace duHastNet.DocManager.Core.Services;

/// <summary>
/// Service responsible for importing documents from CSV format
/// Handles creation of new documents and updates to existing documents
/// </summary>
public class DocumentImportService
{
    private readonly IUnitOfWork _unitOfWork;

    public DocumentImportService(IUnitOfWork unitOfWork)
    {
        _unitOfWork = unitOfWork;
    }

    /// <summary>
    /// Imports documents from a CSV file
    /// </summary>
    /// <param name="filePath">Path to CSV file to import</param>
    /// <param name="useFullRevisionHistory">If true, expects all revision columns (including blanks for documents not in that revision). If false, only imports revisions with non-blank indicators.</param>
    /// <returns>Import result with statistics and any errors</returns>
    public async Task<ImportResult> ImportDocumentsAsync(string filePath, bool useFullRevisionHistory = false)
    {
        var result = new ImportResult();
        var errors = new List<string>();
        int documentsProcessed = 0;
        int documentsCreated = 0;
        int documentsUpdated = 0;
        int documentsSkipped = 0;

        try
        {
            // Load custom field definitions and revisions for validation
            var customFieldDefinitions = await _unitOfWork.CustomFieldDefinitions.GetAllAsync();
            var customFieldLookup = customFieldDefinitions.ToDictionary(
                cfd => cfd.PropertyName,
                cfd => cfd,
                StringComparer.OrdinalIgnoreCase);

            var revisions = await _unitOfWork.Revisions.GetAllAsync();
            var revisionLookup = revisions.ToDictionary(r => r.Id, r => r);

            using var reader = new StreamReader(filePath);
            using var csv = new CsvReader(reader, new CsvConfiguration(CultureInfo.InvariantCulture)
            {
                HasHeaderRecord = true,
                MissingFieldFound = null // Don't throw on missing fields
            });

            // Read header to get column names
            csv.Read();
            csv.ReadHeader();
            var headers = csv.HeaderRecord?.ToList() ?? new List<string>();

            // Identify custom field columns and revision history columns
            var customFieldColumns = GetCustomFieldColumns(headers, customFieldLookup);
            var revisionHistoryColumns = GetRevisionHistoryColumns(headers);

            // Validate that all custom field definitions have corresponding CSV columns
            // This ensures the business rule "all documents use all properties" is maintained
            var missingColumns = customFieldDefinitions
                .Where(cfd => !customFieldColumns.Contains(cfd.PropertyName, StringComparer.OrdinalIgnoreCase))
                .Select(cfd => cfd.PropertyName)
                .ToList();

            if (missingColumns.Any())
            {
                return ImportResult.CreateFailure(
                    $"Import failed: CSV file is missing required custom field columns: {string.Join(", ", missingColumns)}");
            }

            int rowNumber = 1; // Start at 1 for first data row

            // Read each row
            while (await Task.Run(() => csv.Read()))
            {
                rowNumber++;
                documentsProcessed++;

                try
                {
                    var importRow = ParseRow(csv, headers, customFieldColumns, revisionHistoryColumns);

                    if (importRow.Id.Equals("new", StringComparison.OrdinalIgnoreCase))
                    {
                        // Create new document
                        var createResult = await CreateNewDocumentAsync(
                            importRow,
                            customFieldLookup,
                            revisionLookup,
                            rowNumber);

                        if (createResult.Success)
                        {
                            documentsCreated++;
                        }
                        else
                        {
                            errors.AddRange(createResult.Errors);
                            documentsSkipped++;
                        }
                    }
                    else
                    {
                        // Update existing document
                        var updateResult = await UpdateExistingDocumentAsync(
                            importRow,
                            customFieldLookup,
                            revisionLookup,
                            rowNumber);

                        if (updateResult.Success)
                        {
                            documentsUpdated++;
                        }
                        else
                        {
                            errors.AddRange(updateResult.Errors);
                            documentsSkipped++;
                        }
                    }
                }
                catch (Exception ex)
                {
                    errors.Add($"Row {rowNumber}: {ex.Message}");
                    documentsSkipped++;
                }
            }

            // Set result
            result.IsImportSuccessful = errors.Count == 0;
            result.DocumentsProcessed = documentsProcessed;
            result.DocumentsCreated = documentsCreated;
            result.DocumentsSkipped = documentsSkipped;
            result.Message = errors.Count == 0
                ? $"Import completed: {documentsCreated} created, {documentsUpdated} updated"
                : $"Import completed with errors: {documentsCreated} created, {documentsUpdated} updated, {documentsSkipped} skipped";

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
    /// Parses a CSV row into an ImportRow object
    /// </summary>
    private DocumentImportRow ParseRow(
        CsvReader csv,
        List<string> headers,
        List<string> customFieldColumns,
        List<(string IndicatorColumn, string IdColumn, int Index)> revisionHistoryColumns)
    {
        var row = new DocumentImportRow
        {
            Id = csv.GetField("Id") ?? string.Empty,
            DocumentNumber = csv.GetField("Document Number") ?? string.Empty,
            DocumentName = csv.GetField("Document Name") ?? string.Empty,
            RevisionIndicator = csv.GetField("Revision Indicator") ?? string.Empty,
            // Empty or invalid RevisionId defaults to 0 (no revision assigned yet)
            // This allows importing documents that don't have revisions
            RevisionId = int.TryParse(csv.GetField("Revision Id"), out int revId) ? revId : 0
        };

        // Parse custom fields
        foreach (var fieldColumn in customFieldColumns)
        {
            var value = csv.GetField(fieldColumn) ?? string.Empty;
            row.CustomFields[fieldColumn] = value;
        }

        // Parse revision history
        // Note: This method handles both import modes automatically:
        // - Full mode (useFullRevisionHistory=true): Reads all revision columns, stores only non-blank indicators
        // - Sparse mode (useFullRevisionHistory=false): Reads only present revision columns, stores non-blank indicators
        // In both cases, blank indicators are skipped, which is the desired behavior
        foreach (var (indicatorColumn, idColumn, index) in revisionHistoryColumns)
        {
            var indicator = csv.GetField(indicatorColumn) ?? string.Empty;
            var idString = csv.GetField(idColumn) ?? string.Empty;

            if (!string.IsNullOrWhiteSpace(indicator) && int.TryParse(idString, out int historyRevId))
            {
                row.RevisionHistory.Add((index, historyRevId, indicator));
            }
        }

        return row;
    }

    /// <summary>
    /// Identifies custom field columns from CSV headers
    /// </summary>
    private List<string> GetCustomFieldColumns(
        List<string> headers,
        Dictionary<string, CustomFieldDefinition> customFieldLookup)
    {
        var fixedColumns = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "Id", "Document Number", "Document Name", "Revision Indicator", "Revision Id"
        };

        return headers
            .Where(h => !fixedColumns.Contains(h) &&
                       !h.StartsWith("Revision Indicator ", StringComparison.OrdinalIgnoreCase) &&
                       !h.StartsWith("Revision Id ", StringComparison.OrdinalIgnoreCase) &&
                       customFieldLookup.ContainsKey(h))
            .ToList();
    }

    /// <summary>
    /// Identifies revision history columns from CSV headers
    /// </summary>
    private List<(string IndicatorColumn, string IdColumn, int Index)> GetRevisionHistoryColumns(List<string> headers)
    {
        var revisionColumns = new List<(string IndicatorColumn, string IdColumn, int Index)>();

        var indicatorColumns = headers
            .Where(h => h.StartsWith("Revision Indicator ", StringComparison.OrdinalIgnoreCase))
            .ToList();

        foreach (var indicatorColumn in indicatorColumns)
        {
            // Extract index number from "Revision Indicator N"
            var indexStr = indicatorColumn.Substring("Revision Indicator ".Length).Trim();
            if (int.TryParse(indexStr, out int index))
            {
                var idColumn = $"Revision Id {index}";
                if (headers.Contains(idColumn, StringComparer.OrdinalIgnoreCase))
                {
                    revisionColumns.Add((indicatorColumn, idColumn, index));
                }
            }
        }

        return revisionColumns.OrderBy(rc => rc.Index).ToList();
    }

    /// <summary>
    /// Creates a new document from import row
    /// </summary>
    private async Task<ValidationResult> CreateNewDocumentAsync(
        DocumentImportRow importRow,
        Dictionary<string, CustomFieldDefinition> customFieldLookup,
        Dictionary<int, Revision> revisionLookup,
        int rowNumber)
    {
        try
        {
            // Validate required fields
            if (string.IsNullOrWhiteSpace(importRow.DocumentNumber))
            {
                return ValidationResult.CreateFailure($"Row {rowNumber}: Document Number is required");
            }

            if (string.IsNullOrWhiteSpace(importRow.DocumentName))
            {
                return ValidationResult.CreateFailure($"Row {rowNumber}: Document Name is required");
            }

            // Allow RevisionId = 0 or empty to indicate "No Revision" 
            // This supports documents that don't have a revision assigned yet
            // Any non-zero value must exist in the revisions table
            if (importRow.RevisionId != 0 && !revisionLookup.ContainsKey(importRow.RevisionId))
            {
                var availableRevisions = revisionLookup.Count > 0
                    ? string.Join(", ", revisionLookup.Keys.OrderBy(k => k))
                    : "none";
                return ValidationResult.CreateFailure(
                    $"Row {rowNumber}: Invalid Revision Id {importRow.RevisionId}. Available revisions: {availableRevisions}. Use 0 or leave empty for documents without a revision.");
            }

            // Check if document already exists
            var exists = await _unitOfWork.Documents.DocumentExistsAsync(
                importRow.DocumentNumber,
                importRow.RevisionIndicator);

            if (exists)
            {
                return ValidationResult.CreateFailure(
                    $"Row {rowNumber}: Document {importRow.DocumentNumber} with revision {importRow.RevisionIndicator} already exists");
            }

            // Create new document
            var document = new Document(
                importRow.DocumentNumber,
                importRow.DocumentName,
                importRow.RevisionIndicator,
                importRow.RevisionId);

            // Set revision history
            foreach (var (index, revId, indicator) in importRow.RevisionHistory)
            {
                document.SetRevisionIndicator(revId, indicator);
            }

            // Insert document - SQLite-net-pcl should update the Id property
            await _unitOfWork.Documents.InsertAsync(document);

            // Verify we have a valid Id after insert
            if (document.Id == 0)
            {
                // Fallback: Query for the just-inserted document
                var docs = await _unitOfWork.Documents.GetDocumentsByNumberAsync(importRow.DocumentNumber);
                var insertedDoc = docs.FirstOrDefault(d => d.Revision == importRow.RevisionIndicator);

                if (insertedDoc == null)
                {
                    return ValidationResult.CreateFailure($"Row {rowNumber}: Document created but could not be retrieved for custom properties");
                }

                document = insertedDoc;
            }

            // Add custom properties using the valid document Id
            foreach (var (fieldName, fieldValue) in importRow.CustomFields)
            {
                if (customFieldLookup.TryGetValue(fieldName, out var fieldDef))
                {
                    var customProperty = new CustomProperty(
                        document.Id,
                        fieldDef.Id,
                        fieldValue);

                    await _unitOfWork.CustomProperties.InsertAsync(customProperty);
                }
            }

            // Update bidirectional relationship: add document to revision's DocumentIds collection
            if (document.RevisionId != 0)
            {
                await _unitOfWork.Revisions.AddDocumentToRevisionAsync(document.RevisionId, document.Id);
            }

            return ValidationResult.CreateSuccess();
        }
        catch (Exception ex)
        {
            return ValidationResult.CreateFailure($"Row {rowNumber}: {ex.Message}");
        }
    }

    /// <summary>
    /// Updates an existing document from import row
    /// </summary>
    private async Task<ValidationResult> UpdateExistingDocumentAsync(
        DocumentImportRow importRow,
        Dictionary<string, CustomFieldDefinition> customFieldLookup,
        Dictionary<int, Revision> revisionLookup,
        int rowNumber)
    {
        try
        {
            // Parse document ID
            if (!int.TryParse(importRow.Id, out int documentId))
            {
                return ValidationResult.CreateFailure($"Row {rowNumber}: Invalid document Id '{importRow.Id}'");
            }

            // Get existing document
            var document = await _unitOfWork.Documents.GetByIdAsync(documentId);
            if (document == null)
            {
                return ValidationResult.CreateFailure($"Row {rowNumber}: Document with Id {documentId} not found");
            }

            bool documentChanged = false;
            int oldRevisionId = document.RevisionId; // Track old revision for bidirectional update

            // Check for document number change
            if (document.Number != importRow.DocumentNumber)
            {
                // Add old number to history with current date
                document.AddToHistory(document.Number, DateOnly.FromDateTime(DateTime.Now));
                // Update to new number
                document.Number = importRow.DocumentNumber;
                documentChanged = true;
            }

            // Check for document name change
            if (document.Name != importRow.DocumentName)
            {
                document.Name = importRow.DocumentName;
                documentChanged = true;
            }

            // Check for revision indicator change (updates indicator only, not revision id or history)
            if (document.Revision != importRow.RevisionIndicator)
            {
                document.Revision = importRow.RevisionIndicator;
                documentChanged = true;
            }

            // Check for revision id change (validates and updates, keeps indicator unchanged)
            if (document.RevisionId != importRow.RevisionId)
            {
                // Allow RevisionId = 0 to indicate "No Revision"
                if (importRow.RevisionId != 0 && !revisionLookup.ContainsKey(importRow.RevisionId))
                {
                    return ValidationResult.CreateFailure(
                        $"Row {rowNumber}: Invalid Revision Id {importRow.RevisionId}. Use 0 for documents without a revision.");
                }

                document.RevisionId = importRow.RevisionId;
                documentChanged = true;
            }

            // Update document if changed
            if (documentChanged)
            {
                await _unitOfWork.Documents.UpdateAsync(document);
            }

            // Update bidirectional relationship if revision changed
            if (oldRevisionId != document.RevisionId)
            {
                // Remove from old revision's DocumentIds collection
                if (oldRevisionId != 0)
                {
                    await _unitOfWork.Revisions.RemoveDocumentFromRevisionAsync(oldRevisionId, document.Id);
                }

                // Add to new revision's DocumentIds collection
                if (document.RevisionId != 0)
                {
                    await _unitOfWork.Revisions.AddDocumentToRevisionAsync(document.RevisionId, document.Id);
                }
            }

            // Update custom properties
            var existingProperties = await _unitOfWork.CustomProperties.GetPropertiesByDocumentAsync(documentId);

            foreach (var (fieldName, fieldValue) in importRow.CustomFields)
            {
                if (customFieldLookup.TryGetValue(fieldName, out var fieldDef))
                {
                    var existingProperty = existingProperties
                        .FirstOrDefault(cp => cp.CustomFieldDefinitionId == fieldDef.Id);

                    if (existingProperty != null)
                    {
                        // Update existing property
                        if (existingProperty.PropertyValue != fieldValue)
                        {
                            existingProperty.PropertyValue = fieldValue;
                            await _unitOfWork.CustomProperties.UpdateAsync(existingProperty);
                        }
                    }
                    else
                    {
                        // Create new property
                        var customProperty = new CustomProperty(
                            document.Id,
                            fieldDef.Id,
                            fieldValue);

                        await _unitOfWork.CustomProperties.InsertAsync(customProperty);
                    }
                }
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
    private class DocumentImportRow
    {
        public string Id { get; set; } = string.Empty;
        public string DocumentNumber { get; set; } = string.Empty;
        public string DocumentName { get; set; } = string.Empty;
        public string RevisionIndicator { get; set; } = string.Empty;
        public int RevisionId { get; set; }
        public Dictionary<string, string> CustomFields { get; set; } = new();
        public List<(int Index, int RevisionId, string Indicator)> RevisionHistory { get; set; } = new();
    }
}