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
using duHastNet.DocManager.Core.Models.MetaData;
using System.Globalization;

namespace duHastNet.DocManager.Core.Services;

/// <summary>
/// Service responsible for exporting document metadata to cloud provider format
/// Supports mapping document properties to cloud provider metadata fields
/// </summary>
public class CloudMetadataExportService
{
    /// <summary>
    /// Exports documents with mapped metadata to a CSV file for cloud upload
    /// </summary>
    /// <param name="filePath">Path where CSV metadata file will be saved</param>
    /// <param name="documents">Collection of documents to export</param>
    /// <param name="revisions">All revisions for looking up revision details</param>
    /// <param name="cloudMetaData">Cloud provider metadata mapper (e.g., Aconex)</param>
    /// <param name="customProperties">Custom properties for each document</param>
    /// <param name="filePathsByDocumentId">Dictionary mapping document IDs to their incoming file paths</param>
    /// <returns>True if export successful, false otherwise</returns>
    public async Task<bool> ExportMetadataAsync(
        string filePath,
        IEnumerable<Document> documents,
        IEnumerable<Revision> revisions,
        ICloudMetaData cloudMetaData,
        Dictionary<int, List<CustomProperty>> customProperties,
        Dictionary<int, string> filePathsByDocumentId)
    {
        try
        {
            // Validate inputs
            if (string.IsNullOrWhiteSpace(filePath))
                return false;

            if (cloudMetaData == null)
                return false;

            var documentsList = documents.ToList();
            var revisionsList = revisions.ToList();
            var mappings = cloudMetaData.MetaDataMap;

            if (!documentsList.Any() || !mappings.Any())
                return false;

            // Read template file if it exists to get the correct column order
            List<string> columnHeaders;
            if (!string.IsNullOrWhiteSpace(cloudMetaData.MetadataTemplateFilePath) &&
                File.Exists(cloudMetaData.MetadataTemplateFilePath))
            {
                // Read headers from template to maintain order
                columnHeaders = await ReadTemplateHeadersAsync(cloudMetaData.MetadataTemplateFilePath).ConfigureAwait(false);
            }
            else
            {
                // Use mapped fields if no template
                columnHeaders = mappings
                    .Select(m => m.MetaFieldName ?? string.Empty)
                    .Where(h => !string.IsNullOrWhiteSpace(h))
                    .Distinct()
                    .ToList();
            }

            if (!columnHeaders.Any())
                return false;

            // Write CSV file
            using var writer = new StreamWriter(filePath);
            using var csv = new CsvWriter(writer, new CsvConfiguration(CultureInfo.InvariantCulture)
            {
                HasHeaderRecord = true
            });

            // Write header row
            foreach (var header in columnHeaders)
            {
                csv.WriteField(header);
            }
            csv.NextRecord();

            // Write data rows
            foreach (var document in documentsList)
            {
                await WriteDocumentRowAsync(csv, document, columnHeaders, mappings, revisionsList, customProperties, filePathsByDocumentId).ConfigureAwait(false);
            }

            return true;
        }
        catch
        {
            return false;
        }
    }

    /// <summary>
    /// Reads column headers from a CSV template file
    /// </summary>
    private async Task<List<string>> ReadTemplateHeadersAsync(string templatePath)
    {
        try
        {
            var headers = new List<string>();

            using var reader = new StreamReader(templatePath);
            using var csv = new CsvReader(reader, new CsvConfiguration(CultureInfo.InvariantCulture)
            {
                HasHeaderRecord = true,
                DetectDelimiter = true,
                DetectDelimiterValues = new[] { ",", ";", "\t", "|" }
            });

            await csv.ReadAsync().ConfigureAwait(false);
            csv.ReadHeader();

            if (csv.HeaderRecord != null)
            {
                headers.AddRange(csv.HeaderRecord.Where(h => !string.IsNullOrWhiteSpace(h)));
            }

            return headers;
        }
        catch
        {
            return new List<string>();
        }
    }

    /// <summary>
    /// Writes a single document row with mapped metadata values
    /// </summary>
    private async Task WriteDocumentRowAsync(
        CsvWriter csv,
        Document document,
        List<string> columnHeaders,
        List<MetaDataMap> mappings,
        List<Revision> revisions,
        Dictionary<int, List<CustomProperty>> customProperties,
        Dictionary<int, string> filePathsByDocumentId)
    {
        // For each column header, find the corresponding mapping and get the value
        foreach (var header in columnHeaders)
        {
            var mapping = mappings.FirstOrDefault(m => m.MetaFieldName == header);

            if (mapping == null)
            {
                // No mapping for this field - write empty
                csv.WriteField(string.Empty);
                continue;
            }

            // Get the value based on mapping type
            string value;

            if (!string.IsNullOrWhiteSpace(mapping.MetaFieldValue))
            {
                // Fixed/static value
                value = mapping.MetaFieldValue;
            }
            else if (!string.IsNullOrWhiteSpace(mapping.DocumentPropertyName))
            {
                // Dynamic value from document property
                value = GetDocumentPropertyValue(document, mapping.DocumentPropertyName, revisions, customProperties);
            }
            else if (!string.IsNullOrWhiteSpace(mapping.FilePropertyName))
            {
                // Dynamic value from file property
                value = GetFilePropertyValue(document, mapping.FilePropertyName, filePathsByDocumentId);
            }
            else
            {
                // No value source configured
                value = string.Empty;
            }

            csv.WriteField(value);
        }

        csv.NextRecord();
        await Task.CompletedTask.ConfigureAwait(false); // For async signature consistency
    }

    /// <summary>
    /// Gets a document property value by name
    /// Supports standard properties and custom properties
    /// </summary>
    private string GetDocumentPropertyValue(
        Document document,
        string propertyName,
        List<Revision> revisions,
        Dictionary<int, List<CustomProperty>> customProperties)
    {
        // Standard document properties
        switch (propertyName.ToLowerInvariant())
        {
            case "number":
            case "documentnumber":
                return document.Number;

            case "name":
            case "documentname":
                return document.Name;

            case "revision":
            case "revisionindicator":
                return document.Revision;

            case "revisionid":
                return document.RevisionId.ToString();

            case "revisiondate":
                var revision = revisions.FirstOrDefault(r => r.Id == document.RevisionId);
                return revision?.RevisionDate.ToString("dd/MM/yyyy") ?? string.Empty;

            case "revisiondescription":
                var rev = revisions.FirstOrDefault(r => r.Id == document.RevisionId);
                return rev?.Description ?? string.Empty;

            case "isactive":
                return document.IsActive.ToString();

            case "id":
            case "documentid":
                return document.Id.ToString();

            default:
                // Check custom properties
                if (customProperties.TryGetValue(document.Id, out var docProperties))
                {
                    var customProp = docProperties.FirstOrDefault(p =>
                        string.Equals(p.PropertyName, propertyName, StringComparison.OrdinalIgnoreCase));

                    return customProp?.PropertyValue ?? string.Empty;
                }
                return string.Empty;
        }
    }

    /// <summary>
    /// Gets a file property value by name
    /// Supports file name, extension, and full path
    /// </summary>
    private string GetFilePropertyValue(
        Document document,
        string propertyName,
        Dictionary<int, string> filePathsByDocumentId)
    {
        // Try to get the file path for this document
        if (!filePathsByDocumentId.TryGetValue(document.Id, out var filePath))
        {
            return string.Empty;
        }

        // Handle different file property names
        switch (propertyName.ToLowerInvariant())
        {
            case "filename":
            case "name":
                return Path.GetFileName(filePath);

            case "filenamewithoutextension":
            case "namewithoutextension":
                return Path.GetFileNameWithoutExtension(filePath);

            case "extension":
            case "fileextension":
                return Path.GetExtension(filePath).TrimStart('.');

            case "fullpath":
            case "filepath":
            case "path":
                return filePath;

            case "directoryname":
            case "directory":
            case "folder":
                return Path.GetDirectoryName(filePath) ?? string.Empty;

            default:
                return string.Empty;
        }
    }
}
