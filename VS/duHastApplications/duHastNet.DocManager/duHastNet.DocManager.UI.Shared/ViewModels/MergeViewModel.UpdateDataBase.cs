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
using duHastNet.DocManager.UI.Shared.Stores;

namespace duHastNet.DocManager.UI.Shared.ViewModels;

/// <summary>
/// Main ViewModel for the Document Manager application
/// </summary>
public partial class MergeViewModel : ObservableObject
{
    
    /// <summary>
    /// Updates the database with documents of green and yellow status
    /// </summary>
    /// <returns>True if update was successful, false otherwise</returns>
    private async Task<bool> UpdateDatabaseAsync()
    {
        try
        {
            // Validate database connection
            if (!_docManagerApi.IsDatabaseReady())
            {
                _messageStore.EnqueueMessage(
                    "Database connection not available.",
                    MessageTypes.Error);
                return false;
            }

            // Filter documents for database update (green and yellow status only)
            var documentsToUpdate = DocumentMatchViewModel.MatchedDocuments
                .Where(d => d.MatchStatus == DocumentMatchStatus.Ok ||
                            d.MatchStatus == DocumentMatchStatus.WarningRevisionNotSequential)
                .ToList();

            if (!documentsToUpdate.Any())
            {
                _messageStore.EnqueueMessage(
                    "No documents with green or yellow status to update.",
                    MessageTypes.Warning, dismissAfterSeconds: 20);
                return false;
            }

            _messageStore.EnqueueMessage(
                $"Updating database with {documentsToUpdate.Count} documents...",
                MessageTypes.Information, dismissAfterSeconds: 3);

            // Convert DateTime to DateOnly
            //DateOnly revisionDateOnly = DateOnly.FromDateTime(RevisionDate!.Value);

            // Check if revision with same date and description exists
            var existingRevisions = await _docManagerApi.GetRevisionsByDateAsync(RevisionDate!.Value).ConfigureAwait(false);
            Revision? targetRevision = existingRevisions
                .FirstOrDefault(r => string.Equals(r.Description, RevisionDescription,
                                     StringComparison.OrdinalIgnoreCase));

            if (targetRevision == null)
            {
                // Create new revision
                targetRevision = new Revision(RevisionDate!.Value, RevisionDescription);
                await _docManagerApi.CreateRevisionAsync(targetRevision).ConfigureAwait(false);

                _messageStore.EnqueueMessage(
                    $"Created new revision: {RevisionDescription} ({RevisionDate!.Value:yyyy-MM-dd})",
                    MessageTypes.Information, dismissAfterSeconds: 3);
            }
            else
            {
                _messageStore.EnqueueMessage(
                    $"Using existing revision: {RevisionDescription} ({RevisionDate!.Value:yyyy-MM-dd})",
                    MessageTypes.Information, dismissAfterSeconds: 3);
            }

            // Update documents in database
            var updateErrors = new List<string>();
            var documentsUpdated = 0;

            foreach (var matchedDoc in documentsToUpdate)
            {
                try
                {
                    if (matchedDoc.HasMatch && matchedDoc.MatchedDocumentId.HasValue)
                    {
                        // Update existing document
                        var document = await _docManagerApi.GetDocumentByIdAsync(matchedDoc.MatchedDocumentId.Value).ConfigureAwait(false);

                        if (document != null)
                        {
                            // Store old revision ID for bidirectional update
                            int oldRevisionId = document.RevisionId;

                            // Update revision indicator
                            document.Revision = matchedDoc.IncomingRevision;

                            // Update revision ID
                            document.RevisionId = targetRevision.Id;

                            // Update document in database
                            await _docManagerApi.UpdateDocumentAsync(document).ConfigureAwait(false);

                            // Update bidirectional relationship
                            if (oldRevisionId != targetRevision.Id)
                            {
                                // Remove from old revision
                                if (oldRevisionId != 0)
                                {
                                    await _docManagerApi.RemoveDocumentFromRevisionAsync(oldRevisionId, document.Id).ConfigureAwait(false);
                                }

                                // Add to new revision
                                await _docManagerApi.AddDocumentToRevisionAsync(targetRevision.Id, document.Id).ConfigureAwait(false);
                            }

                            documentsUpdated++;
                        }
                        else
                        {
                            updateErrors.Add($"Document with ID {matchedDoc.MatchedDocumentId.Value} not found in database");
                        }
                    }
                    else
                    {
                        // This is a new document - should not happen in step 1
                        // New documents should only be added through a separate workflow
                        updateErrors.Add($"Document {matchedDoc.IncomingFileName} has no match - cannot update");
                    }
                }
                catch (Exception ex)
                {
                    updateErrors.Add($"Error updating {matchedDoc.IncomingFileName}: {ex.Message}");
                }
            }

            // Report results
            if (updateErrors.Any())
            {
                var errorMessage = $"Database update completed with errors. " +
                                  $"Updated: {documentsUpdated}, Errors: {updateErrors.Count}. " +
                                  $"First error: {updateErrors.First()}";
                _messageStore.EnqueueMessage(errorMessage, MessageTypes.Warning, dismissAfterSeconds: 20);
                return false; // Had errors, so return false
            }
            else
            {
                _messageStore.EnqueueMessage(
                    $"Successfully updated {documentsUpdated} documents in database with revision " +
                    $"{RevisionDescription} ({RevisionDate!.Value:yyyy-MM-dd})",
                    MessageTypes.Information, dismissAfterSeconds: 3);
                return true; // Success, return true
            }
        }
        catch (Exception ex)
        {
            _messageStore.EnqueueMessage(
                $"Error during database update: {ex.Message}",
                MessageTypes.Error);
            return false; // Exception occurred, return false
        }
    }
}
