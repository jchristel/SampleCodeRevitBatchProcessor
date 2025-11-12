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

namespace duHastNet.DocManager.Core.Models.CurrentFolder
{
    public partial class CurrentFolderManager
    {
        #region file utilities

        /// <summary>
        /// Checks if a file is locked by another process.
        /// </summary>
        private bool IsFileLocked(string filePath)
        {
            // Summary:
            // check if file is locked by another process
            // return true if locked, false if not locked
            try
            {
                using (var stream = System.IO.File.Open(filePath, System.IO.FileMode.Open, System.IO.FileAccess.ReadWrite, System.IO.FileShare.None))
                {
                    stream.Close();
                }
            }
            catch (System.IO.IOException)
            {
                // file is locked
                return true;
            }
            // file is not locked
            return false;
        }

        #endregion file utilities

        #region move matched incoming files to current folder(s)

        /// <summary>
        /// Determines the target folder for the specified document based on filing rules.
        /// </summary>
        /// <remarks>If the system is operating in single-folder mode, this method returns the
        /// preconfigured folder path. In multiple-folder mode, the method evaluates the document's properties against
        /// the defined filing rules to determine the appropriate target folder.</remarks>
        /// <param name="documentPath">The full path of the document to be filed. This parameter can be <see langword="null"/>.</param>
        /// <returns>The path of the target folder where the document should be filed. Returns an empty string if no matching
        /// folder is found.</returns>
        private string DetermineTargetCurrentFolder(string? documentPath)
        {

            // Summary:
            // determine target current folder based on filing rules
            // if single folder mode, return that folder
            // if multiple folder mode, determine target folder based on document properties and folder distribution rules
            // return target folder path or empty string if not found
            
            if (string.IsNullOrEmpty(documentPath))
            {
                // log error - document path is null or empty
                _errors.Add(new ArgumentNullException(
                    nameof(documentPath), 
                    "Document path cannot be null or empty when determining target current folder.")
                );
                return string.Empty;
            }

            if (!string.IsNullOrEmpty(_settings.CurrentFolderPath))
            {
                return _settings.CurrentFolderPath;
            }
            else
            {
                // implement logic for multiple folder mode based on document properties and folder distribution rules
                foreach (var rule in _settings.FilingRules!)
                {
                    // get the file name from the document path
                    string fileName = System.IO.Path.GetFileName(documentPath!);
                    if (rule.IsMatch(fileName))
                    {
                        return rule.TargetDirectory;
                    }
                }
            }
            
            return string.Empty;
        }

        /// <summary>
        /// moves matched incoming files to their respective current folders based on filing rules.
        /// <paramref name="currentDocuments"/> is used to determine the target current folder for each incoming document.
        /// </summary>
        private bool MoveMatchedIncomingFilesToCurrentFolders(List<Document> currentDocuments)
        {
            // Summary:
            // loop through all matched incoming documents
            // for each matched document, check if the target current folder is set ( for single folder mode) and if not multiple folders are in use if all of them exist
            // check if the document is locked by another process
            // if locked, log an error and skip to next document
            // if not locked, move the document to the current folder(s) based on filing rules
            // keep track of which files were moved successfully and which not
            // log results for user information

            bool allFilesMovedSuccessfully = true;

            foreach (var incomingDocumentStatus in _matchedDocuments!)
            {
                try
                {
                    //only move files without problems
                    if (incomingDocumentStatus.IsDuplicate ||
                        incomingDocumentStatus.MatchedDocumentId == null ||
                        incomingDocumentStatus.IncomingDocumentRevision == null)
                    {
                        // skip to next document
                        continue;
                    }


                    // determine target current folder based on filing rules
                    var targetCurrentFolder = DetermineTargetCurrentFolder(incomingDocumentStatus.NewDocumentPath);
                    if (string.IsNullOrEmpty(targetCurrentFolder))
                    {
                        // log error
                        incomingDocumentStatus.AddProcessMessage(
                            new Exceptions.FolderDoesNotExistException(
                                $"{incomingDocumentStatus.NewDocumentPath}")
                        );
                        // errors are logged inside DetermineTargetCurrentFolder
                        allFilesMovedSuccessfully = false;
                        // skip to next document
                        continue;
                    }

                    //log success - target current folder determined
                    incomingDocumentStatus.AddProcessMessage(
                        $"Target current folder determined: {targetCurrentFolder}",
                        Stores.ProcessMessageTypes.Information
                    );

                    // check if file is locked
                    if (IsFileLocked(incomingDocumentStatus.NewDocumentPath!))
                    {
                        // log error - file is locked
                        incomingDocumentStatus.AddProcessMessage(
                            new Exceptions.FileLockedException(
                                $"File is locked and cannot be moved to current folder: {incomingDocumentStatus.NewDocumentPath}",
                                incomingDocumentStatus.NewDocumentPath!)
                        );

                        //set flag indicating not all files moved successfully
                        allFilesMovedSuccessfully = false;
                        
                        // skip to next file
                        continue;
                    }

                    // move file to target current folder
                    var fileName = System.IO.Path.GetFileName(incomingDocumentStatus.NewDocumentPath!);
                    var destinationPath = System.IO.Path.Combine(targetCurrentFolder, fileName);

                    // perform the move
                    try
                    {
                        System.IO.File.Move(incomingDocumentStatus.NewDocumentPath!, destinationPath);
                    }
                    catch (Exception ex)
                    {
                        // mark as not all files moved successfully
                        allFilesMovedSuccessfully = false;
                        // log exception details
                        incomingDocumentStatus.AddProcessMessage(ex);
                    }
                    
                    // log success - file moved successfully
                    incomingDocumentStatus.AddProcessMessage(
                        $"File moved to current folder successfully: {destinationPath}",
                        Stores.ProcessMessageTypes.Information
                    );
                }
                catch (Exception ex)
                {
                    // mark as not all files moved successfully
                    allFilesMovedSuccessfully = false;
                    // log exception details
                    incomingDocumentStatus.AddProcessMessage(ex);
                }
            }

            return allFilesMovedSuccessfully;
        }

        #endregion move matched incoming files to current folder(s)


        #region move matched files to superseded folder

        /// <summary>
        /// Identifies and retrieves the file paths of documents in the current folders that match the specified
        /// incoming documents and need to be superseded.
        /// </summary>
        /// <remarks>This method processes a collection of incoming documents and attempts to find
        /// corresponding matches in the current folders based on metadata. If a match is found, the file path of the
        /// matched document is added to the result list. Documents without a match are skipped.</remarks>
        /// <param name="currentDocuments">A list of current documents to compare against. Each document in this list is checked to determine if it
        /// matches any of the incoming documents.</param>
        /// <returns>A list of file paths representing the matched documents in the current folders. The list will be empty if no
        /// matches are found.</returns>
        private Dictionary<IncomingDocumentProcessingStatus,List< string>> GetMatchedFilesInCurrentFolders(List<Document> currentDocuments)
        {
            // Summary:
            // loop through all matched documents
            // for each matched document, check if the document
            // has a match in the current folder(s)
            // if so, add the document to the list of matched files
            // return the list of matched files

            //container to hold matched files to be superseded
            Dictionary<IncomingDocumentProcessingStatus, List<string>> matchedFilesToSupersede = [];

            foreach (var incomingDocumentStatus in _matchedDocuments!)
            {

                //skip documents without a match
                if (incomingDocumentStatus.MatchedDocumentId == null)
                {
                    // no match found, skip to next document
                    continue;
                }

                //skip duplicate documents
                if (incomingDocumentStatus.IsDuplicate)
                {
                    // is a duplicate, skip to next document
                    continue;
                }

                //skip documents without a revision
                if (incomingDocumentStatus.IncomingDocumentRevision == null)
                {
                    // no revision found, skip to next document
                    continue;
                }

                // determine target current folder based on filing rules
                var targetCurrentFolder = DetermineTargetCurrentFolder(incomingDocumentStatus.NewDocumentPath);

                // get the location of old files to be superseded
                if (string.IsNullOrEmpty(targetCurrentFolder))
                {
                    // log error
                    incomingDocumentStatus.AddProcessMessage(
                        new Exceptions.FolderDoesNotExistException(
                            $"Target current folder could not be determined for document: {incomingDocumentStatus.NewDocumentPath}")
                    );
                    // skip to next document
                    continue;
                }

                // get all files in the target current folder
                var allFilesInTargetFolder = GetSupportedFilesFromFolder(targetCurrentFolder);

                if (allFilesInTargetFolder.Count == 0)
                {
                    // no files in target folder
                    //log information
                    incomingDocumentStatus.AddProcessMessage(
                        $"No supported files found in target current folder: {targetCurrentFolder}. Skipping supersede action.",
                        Stores.ProcessMessageTypes.Information
                    );
                    // skip to next document
                    continue;
                }

                // loop through all incoming files and extract metadata
                foreach (var existingFilePath in allFilesInTargetFolder)
                {
                    // get the current document from the id of the matched document
                    var currentDocument = currentDocuments
                        .FirstOrDefault(d => d.Id == incomingDocumentStatus.MatchedDocumentId);

                    // extract metadata from file name
                    Models.IncomingDocumentProcessingStatus incomingDocument = ExtractDocumentMetadataFromFileName(
                        existingFilePath,
                        new List<Document>() { currentDocument! }
                    );

                    // check if a match was found
                    if (incomingDocument.MatchedDocumentId == null)
                    {
                        // this file does not match the incoming document, no action required
                        // skip to next file
                        continue;
                    }

                    // a match was found, add to the list of files to be superseded
                    // use a discard: '_', since we do not care if the key already exists
                    if (!matchedFilesToSupersede.TryGetValue(incomingDocumentStatus, out _))
                    {
                        matchedFilesToSupersede[incomingDocumentStatus] = [];
                    }

                    // add the existing file path to the list of files to be superseded
                    matchedFilesToSupersede[incomingDocumentStatus].Add(existingFilePath);
                                        
                    //log information
                    incomingDocumentStatus.AddProcessMessage(
                        $"Matched file for supersede found: {existingFilePath}",
                        Stores.ProcessMessageTypes.Information
                    );
                }
            }

            return matchedFilesToSupersede;
        }

        /// <summary>
        /// Moves matched files from the current folders to the superseded folder.
        /// </summary>
        /// <remarks>This method processes a list of documents to identify matched files in the current
        /// folders. For each matched file, it checks whether the file is locked by another process. If a file is
        /// locked, it is skipped, and an error message is logged. If the file is not locked, it is moved to the
        /// superseded folder. The method logs the results of the operation, including any errors encountered during the
        /// process.</remarks>
        /// <param name="currentDocuments">A list of <see cref="Document"/> objects representing the current documents to process.</param>
        /// <returns><see langword="true"/> if all matched files were successfully moved to the superseded folder; otherwise,
        /// <see langword="false"/>.</returns>
        private bool MoveMatchedFilesToSupersededFolder(List<Document> currentDocuments)
        {
            // Summary:
            // loop through all matched documents
            // for each matched document, check if the document
            // has a match in the current folder(s)
            // and if so if it is locked by another process
            // if locked, log an error and skip to next document
            // if not locked, move the document to the superseded folder
            // keep track of which files were moved successfully and which not
            // log results for user information

            // get matched files in current folders
            Dictionary<IncomingDocumentProcessingStatus, List<string>> matchedFiles = GetMatchedFilesInCurrentFolders(currentDocuments);

            // check if there are matched files to move
            if (matchedFiles.Count == 0)
            {
                // no matched files to move
                return true;
            }

            bool allFilesMovedSuccessfully = true;

            foreach (var matchedFile in matchedFiles)
            {
                try
                {
                    foreach (var fileToMove in matchedFile.Value)
                    {
                        // check if file is locked
                        if (IsFileLocked(fileToMove))
                        {
                            allFilesMovedSuccessfully = false;

                            // log error - file is locked
                            matchedFile.Key.AddProcessMessage(
                                new Exceptions.FileLockedException(
                                    $"File is locked and cannot be moved to superseded folder: {fileToMove}",
                                    fileToMove)
                            );

                            //skip to next file
                            continue;
                        }
                        // move file to superseded folder
                        var fileName = System.IO.Path.GetFileName(fileToMove);
                        var destinationPath = System.IO.Path.Combine(_settings.SupersededFolderPath!, fileName);
                        try
                        {
                            System.IO.File.Move(fileToMove, destinationPath);
                            // log success - file moved successfully
                            matchedFile.Key.AddProcessMessage(
                                $"File moved to superseded folder successfully: {destinationPath}",
                                Stores.ProcessMessageTypes.Information
                            );
                        }
                        catch (Exception ex)
                        {
                            // log exception details
                            matchedFile.Key.AddProcessMessage(ex);

                            // mark as not all files moved successfully
                            allFilesMovedSuccessfully = false;
                        }
                    }
                }
                catch (Exception ex)
                {
                    // log exception details
                    matchedFile.Key.AddProcessMessage(ex);
                }
            }

            return allFilesMovedSuccessfully;
        }

        #endregion move matched files to superseded folder
    }
}
