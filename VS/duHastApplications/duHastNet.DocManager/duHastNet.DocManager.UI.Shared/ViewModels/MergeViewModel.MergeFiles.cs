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


using duHastNet.DocManager.Core.Models.CurrentFolder;
using duHastNet.DocManager.UI.Shared.Stores;
using System;
using System.Linq;
using System.Threading.Tasks;
using System.IO;

namespace duHastNet.DocManager.UI.Shared.ViewModels;

/// <summary>
/// Partial class for MergeViewModel containing file merging logic
/// </summary>
public partial class MergeViewModel
{
    /// <summary>
    /// Merges incoming files with red and yellow status into their target locations
    /// Uses CurrentFolderManager to handle file operations including superseding old files
    /// </summary>
    /// <returns>Task representing the async operation</returns>
    private async Task MergeFilesAsync()
    {
        try
        {
            _messageStore.SetCurrentMessage(
                "Merging files into target folders...",
                MessageTypes.Information);

            // Get documents to merge (red and yellow status)
            // Red = NoMatch or ErrorDuplicateDocument (need to be handled manually)
            // Yellow = Warnings (safe to merge but with caution)
            var documentsToMerge = DocumentMatchViewModel.MatchedDocuments
                .Where(d => d.MatchStatus == DocumentMatchStatus.WarningRevisionNotSequential ||
                            d.MatchStatus == DocumentMatchStatus.WarningMissingRevision ||
                            d.MatchStatus == DocumentMatchStatus.NoMatch)
                .ToList();

            if (!documentsToMerge.Any())
            {
                _messageStore.SetCurrentMessage(
                    "No files with warnings or unmatched status to merge.",
                    MessageTypes.Information);
                return;
            }

            // For documents with yellow status (warnings) that have matches,
            // we can use the supersede functionality to move old files and bring in new ones
            var documentsWithMatches = documentsToMerge
                .Where(d => d.HasMatch)
                .ToList();

            // For documents without matches (red - NoMatch), we can only move the incoming files
            // Cannot supersede because there's nothing to supersede
            var documentsWithoutMatches = documentsToMerge
                .Where(d => !d.HasMatch)
                .ToList();

            int filesMovedSuccessfully = 0;
            int filesMovedFailed = 0;
            int filesSuperseded = 0;

            // Handle documents with matches (can supersede old versions)
            if (documentsWithMatches.Any())
            {
                _messageStore.SetCurrentMessage(
                    $"Processing {documentsWithMatches.Count} files with matches (will supersede old versions)...",
                    MessageTypes.Information);

                // Get current documents from manager for supersede operation
                var currentDocuments = _manager.GetAllDocuments().ToList();

                // Use CurrentFolderManager to supersede documents
                // This will:
                // 1. Move old files to superseded folder
                // 2. Move new files to current folder
                bool supersedeSuccessful = _currentFolderManager.SupersedeDocuments(currentDocuments);

                if (supersedeSuccessful)
                {
                    filesSuperseded = documentsWithMatches.Count;
                    filesMovedSuccessfully += documentsWithMatches.Count;

                    _messageStore.SetCurrentMessage(
                        $"Successfully superseded {filesSuperseded} files (old versions moved to superseded folder).",
                        MessageTypes.Information);
                }
                else
                {
                    // Check errors from CurrentFolderManager
                    var errors = _currentFolderManager.Errors;
                    var errorMessages = errors.Select(e => e.Message).ToList();

                    // Count how many actually succeeded by checking process messages
                    var matchedDocuments = _currentFolderManager.GetMatchedDocuments();
                    var successfulMoves = matchedDocuments
                        .Count(d => d.GetProcessStatus()==true);

                    filesMovedSuccessfully += successfulMoves;
                    filesMovedFailed += documentsWithMatches.Count - successfulMoves;

                    if (errorMessages.Any())
                    {
                        _messageStore.SetCurrentMessage(
                            $"File merge completed with errors. Moved: {successfulMoves}, Failed: {filesMovedFailed}. " +
                            $"First error: {errorMessages.First()}",
                            MessageTypes.Warning);
                    }
                    else
                    {
                        _messageStore.SetCurrentMessage(
                            $"File merge completed. Moved: {successfulMoves} files.",
                            MessageTypes.Information);
                    }
                }
            }

            // Handle documents without matches (just move incoming files, no superseding)
            if (documentsWithoutMatches.Any())
            {
                _messageStore.SetCurrentMessage(
                    $"Processing {documentsWithoutMatches.Count} unmatched files (will move to target folders without superseding)...",
                    MessageTypes.Information);

                // For unmatched documents, we need to manually move them to target folders
                // based on filing rules
                int unmatchedSuccess = 0;
                int unmatchedFailed = 0;

                foreach (var doc in documentsWithoutMatches)
                {
                    try
                    {
                        // Get the incoming file path
                        var incomingFilePath = doc.IncomingFilePath;

                        if (string.IsNullOrEmpty(incomingFilePath) || !File.Exists(incomingFilePath))
                        {
                            unmatchedFailed++;
                            _messageStore.SetCurrentMessage(
                                $"Incoming file not found: {doc.IncomingFileName}",
                                MessageTypes.Warning);
                            continue;
                        }

                        // Determine target folder based on filing rules
                        // We'll need to add a public method to CurrentFolderManager for this
                        // For now, log that unmatched files need manual handling
                        unmatchedFailed++;

                        _messageStore.SetCurrentMessage(
                            $"Unmatched file requires manual handling: {doc.IncomingFileName}. " +
                            $"File path: {incomingFilePath}",
                            MessageTypes.Warning);
                    }
                    catch (Exception ex)
                    {
                        unmatchedFailed++;
                        _messageStore.SetCurrentMessage(
                            $"Error processing unmatched file {doc.IncomingFileName}: {ex.Message}",
                            MessageTypes.Error);
                    }
                }

                if (unmatchedSuccess > 0)
                {
                    filesMovedSuccessfully += unmatchedSuccess;
                }
                if (unmatchedFailed > 0)
                {
                    filesMovedFailed += unmatchedFailed;
                }
            }

            // Final summary
            if (filesMovedFailed > 0)
            {
                _messageStore.SetCurrentMessage(
                    $"File merge completed with some issues. " +
                    $"Successfully moved: {filesMovedSuccessfully}, Failed: {filesMovedFailed}. " +
                    $"Check individual file messages for details.",
                    MessageTypes.Warning);
            }
            else
            {
                _messageStore.SetCurrentMessage(
                    $"File merge completed successfully! Moved {filesMovedSuccessfully} files to target locations. " +
                    $"{filesSuperseded} old file versions were superseded.",
                    MessageTypes.Information);
            }
        }
        catch (Exception ex)
        {
            _messageStore.SetCurrentMessage(
                $"Error during file merge: {ex.Message}",
                MessageTypes.Error);
        }

        await Task.CompletedTask; // For async signature consistency
    }
}
