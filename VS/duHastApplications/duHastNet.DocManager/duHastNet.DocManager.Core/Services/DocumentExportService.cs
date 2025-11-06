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
using duHastNet.DocManager.Core.Models;
using System.Globalization;

namespace duHastNet.DocManager.Core.Services;

/// <summary>
/// Service responsible for exporting documents to CSV format
/// Handles dynamic column generation for custom fields and revision history
/// </summary>
public class DocumentExportService
{
    /// <summary>
    /// Exports documents to a CSV file with custom fields and revision history
    /// </summary>
    /// <param name="filePath">Path where CSV file will be saved</param>
    /// <param name="documents">Collection of documents to export</param>
    /// <param name="customFieldDefinitions">Custom field definitions for column headers</param>
    /// <param name="revisions">All revisions for looking up revision details</param>
    /// <returns>True if export successful, false otherwise</returns>
    public bool ExportDocuments(
        string filePath,
        IEnumerable<Document> documents,
        IEnumerable<CustomFieldDefinition> customFieldDefinitions,
        IEnumerable<Revision> revisions)
    {
        try
        {
            // Convert to list for multiple enumeration
            var documentsList = documents.ToList();

            // Determine the maximum number of revisions any document has
            var maxRevisionCount = documentsList.Any() 
                ? documentsList.Max(d => d.RevisionIndicatorHistory.Count) 
                : 0;

            // Build the list of all custom field names in order
            var customFieldNames = customFieldDefinitions
                .OrderBy(cfd => cfd.PropertyName)
                .Select(cfd => cfd.PropertyName)
                .ToList();

            // Create revision lookup dictionary
            var revisionLookup = revisions.ToDictionary(r => r.Id, r => r);

            using var writer = new StreamWriter(filePath);
            using var csv = new CsvWriter(writer, new CsvConfiguration(CultureInfo.InvariantCulture)
            {
                HasHeaderRecord = true
            });

            // Write header row
            WriteHeader(csv, customFieldNames, maxRevisionCount);

            // Write data rows
            foreach (var document in documentsList)
            {
                WriteDocumentRow(csv, document, customFieldNames, maxRevisionCount, revisionLookup);
            }

            return true;
        }
        catch
        {
            return false;
        }
    }

    /// <summary>
    /// Writes the CSV header row with fixed columns, custom fields, and revision history columns
    /// </summary>
    private void WriteHeader(CsvWriter csv, List<string> customFieldNames, int maxRevisionCount)
    {
        // Fixed columns
        csv.WriteField("Id");
        csv.WriteField("Document Number");
        csv.WriteField("Document Name");
        csv.WriteField("Revision Indicator");
        csv.WriteField("Revision Id");

        // Custom field columns
        foreach (var fieldName in customFieldNames)
        {
            csv.WriteField(fieldName);
        }

        // Revision history columns (pairs of Revision Indicator N and Revision Id N)
        for (int i = 1; i <= maxRevisionCount; i++)
        {
            csv.WriteField($"Revision Indicator {i}");
            csv.WriteField($"Revision Id {i}");
        }

        csv.NextRecord();
    }

    /// <summary>
    /// Writes a single document row with all its data
    /// </summary>
    private void WriteDocumentRow(
        CsvWriter csv,
        Document document,
        List<string> customFieldNames,
        int maxRevisionCount,
        Dictionary<int, Revision> revisionLookup)
    {
        // Fixed columns
        csv.WriteField(document.Id);
        csv.WriteField(document.Number);
        csv.WriteField(document.Name);
        csv.WriteField(document.Revision);
        csv.WriteField(document.RevisionId);

        // Custom field values
        foreach (var fieldName in customFieldNames)
        {
            var customProperty = document.CustomProperties
                .FirstOrDefault(cp => cp.PropertyName == fieldName);
            csv.WriteField(customProperty?.PropertyValue ?? string.Empty);
        }

        // Revision history - sorted by index, with current revision as last entry
        WriteRevisionHistory(csv, document, maxRevisionCount, revisionLookup);

        csv.NextRecord();
    }

    /// <summary>
    /// Writes revision history columns for a document
    /// History is sorted by index with current revision appearing as the last entry
    /// </summary>
    private void WriteRevisionHistory(
        CsvWriter csv,
        Document document,
        int maxRevisionCount,
        Dictionary<int, Revision> revisionLookup)
    {
        // Get revision history sorted by index (which is the key in the dictionary)
        var sortedHistory = document.RevisionIndicatorHistory
            .OrderBy(kvp => kvp.Key)
            .ToList();

        // Write each historical revision pair
        for (int i = 0; i < maxRevisionCount; i++)
        {
            if (i < sortedHistory.Count)
            {
                var revisionId = sortedHistory[i].Key;
                var revisionIndicator = sortedHistory[i].Value;

                csv.WriteField(revisionIndicator);
                csv.WriteField(revisionId);
            }
            else
            {
                // Empty cells for documents with fewer revisions
                csv.WriteField(string.Empty);
                csv.WriteField(string.Empty);
            }
        }
    }
}
