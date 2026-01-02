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


using CommunityToolkit.Mvvm.ComponentModel;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.CurrentFolder;
using duHastNet.DocManager.Core.Models.Database;
using duHastNet.DocManager.Core.Services;
using duHastNet.DocManager.UI.Shared.Stores;
using System.IO;

namespace duHastNet.DocManager.UI.Shared.ViewModels.Merge;

/// <summary>
/// Main ViewModel for the Document Manager application
/// </summary>
public partial class MergeViewModel : ObservableObject
{
    
    /// <summary>
    /// Exports metadata to cloud provider location if enabled
    /// </summary>
    private async Task ExportMetadataAsync()
    {
        try
        {
            // Check if cloud document manager is enabled
            if (!_manager.CloudDocumentManager.CloudDocumentManagerEnabled)
            {
                _messageStore.EnqueueMessage(
                    "Cloud document manager is not enabled. Skipping metadata export.",
                    MessageTypes.Information, dismissAfterSeconds: 3);
                return;
            }

            // Check if metadata mapper is configured
            if (_manager.CloudDocumentManager.MetaDataMapper == null)
            {
                _messageStore.EnqueueMessage(
                    "No cloud provider configured. Skipping metadata export.",
                    MessageTypes.Information, dismissAfterSeconds: 3);
                return;
            }

            var metaDataMapper = _manager.CloudDocumentManager.MetaDataMapper;

            // Check if there are any mappings configured
            if (metaDataMapper.MetaDataMap.Count == 0)
            {
                _messageStore.EnqueueMessage(
                    "No metadata mappings configured. Skipping metadata export.",
                    MessageTypes.Warning, dismissAfterSeconds: 20);
                return;
            }

            _messageStore.EnqueueMessage(
                "Exporting metadata for cloud upload...",
                MessageTypes.Information, dismissAfterSeconds: 3);

            // Prompt user for export location
            var selectedPath = _dialogService.ShowSaveFileDialog(
                "Export Metadata for Cloud Upload",
                "CSV files (*.csv)|*.csv|All files (*.*)|*.*",
                "CloudMetadata.csv");

            // Check for cancellation
            if (string.IsNullOrEmpty(selectedPath))
            {
                _messageStore.EnqueueMessage(
                    "Metadata export cancelled.",
                    MessageTypes.Information, dismissAfterSeconds: 3);
                return;
            }

            // Get documents that were updated (green and yellow status)
            var documentsToExport = DocumentMatchViewModel.MatchedDocuments
                .Where(d => d.MatchStatus == DocumentMatchStatus.Ok ||
                            d.MatchStatus == DocumentMatchStatus.WarningRevisionNotSequential)
                .ToList();

            if (documentsToExport.Count == 0)
            {
                _messageStore.EnqueueMessage(
                    "No documents to export metadata for.",
                    MessageTypes.Warning, dismissAfterSeconds: 20);
                return;
            }


            // Get full document objects from database
            // Use a dictionary to track documents we've already loaded to avoid duplicates
            var documentsById = new Dictionary<int, Document>();
            var filePathsByDocumentId = new Dictionary<int, List<string>>();

            foreach (var matchedDoc in documentsToExport)
            {
                //if (!matchedDoc.MatchedDocumentId.HasValue)
                //    continue;

                var docId = matchedDoc.MatchedDocumentId!.Value;
                
                // Only fetch the document if we haven't already
                if (!documentsById.ContainsKey(docId))
                {
                    var doc = await _docManagerApi.GetDocumentByIdAsync(docId);
                    if (doc != null)
                    {
                        documentsById[docId] = doc;
                    }
                }
                
                // Store the incoming file path for this document
                if (!string.IsNullOrWhiteSpace(matchedDoc.IncomingFilePath))
                {
                    if (!filePathsByDocumentId.TryGetValue(docId, out List<string>? value))
                    {
                        value = [];
                        filePathsByDocumentId[docId] = value;
                    }

                    value.Add(matchedDoc.IncomingFilePath);
                }
            }

            // Convert dictionary to list for export
            var documents = documentsById.Values.ToList();

            // Get revisions for metadata from database (not in-memory manager)
            var revisions = await _docManagerApi.GetAllRevisionsAsync();

            // Get custom properties for documents
            var customProperties = new Dictionary<int, List<CustomProperty>>();
            foreach (var doc in documents)
            {
                customProperties[doc.Id] = doc.CustomProperties;
            }

            // Set supported file types in the metadata mapper
            metaDataMapper.SupportedFileTypes = _currentFolderManager.Settings.SupportedFileTypes;

            // Create export service and perform export
            var exportService = new CloudMetadataExportService();
            bool success = await exportService.ExportMetadataAsync(
                selectedPath,
                documents,
                revisions,
                metaDataMapper,
                customProperties,
                filePathsByDocumentId);

            if (success)
            {
                _messageStore.EnqueueMessage(
                    $"Successfully exported metadata for {documents.Count} documents to {Path.GetFileName(selectedPath)}",
                    MessageTypes.Information, dismissAfterSeconds: 3);
            }
            else
            {
                _messageStore.EnqueueMessage(
                    "Metadata export failed. Please check the configuration and try again.",
                    MessageTypes.Error);
            }
        }
        catch (Exception ex)
        {
            _messageStore.EnqueueMessage(
                $"Error during metadata export: {ex.Message}",
                MessageTypes.Error);
        }
    }
}
