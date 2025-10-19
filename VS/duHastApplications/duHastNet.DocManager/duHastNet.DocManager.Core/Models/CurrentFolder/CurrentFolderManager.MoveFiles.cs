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

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace duHastNet.DocManager.Core.Models.CurrentFolder
{
    public partial class CurrentFolderManager
    {
        #region file utilities
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

            if (!string.IsNullOrEmpty(_currentFolderPath))
            {
                return _currentFolderPath;
            }
            else
            {
                // implement logic for multiple folder mode based on document properties and folder distribution rules
                foreach (var rule in _filingRules!)
                {
                    // get the file name from the document path
                    string fileName = System.IO.Path.GetFileName(documentPath!);
                    if (rule.IsMatch(fileName))
                    {
                        return rule.TargetFolderPath;
                    }
                }
            }

            // log error - no matching folder found
            _errors.Add(new Exceptions.FolderDoesNotExistException(
                $"No matching target folder found for document: {documentPath}", 
                documentPath)
            );
            
            return string.Empty;
        }

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
                    // determine target current folder based on filing rules
                    var targetCurrentFolder = DetermineTargetCurrentFolder(incomingDocumentStatus.NewDocumentPath);
                    if (string.IsNullOrEmpty(targetCurrentFolder))
                    {
                        // errors are logged inside DetermineTargetCurrentFolder
                        allFilesMovedSuccessfully = false;
                        // skip to next document
                        continue;
                    }

                    // check if file is locked
                    if (IsFileLocked(incomingDocumentStatus.NewDocumentPath!))
                    {
                        allFilesMovedSuccessfully = false;
                        // log error - file is locked
                        continue;
                    }
                    // move file to target current folder
                    var fileName = System.IO.Path.GetFileName(incomingDocumentStatus.NewDocumentPath!);
                    var destinationPath = System.IO.Path.Combine(targetCurrentFolder, fileName);
                    System.IO.File.Move(incomingDocumentStatus.NewDocumentPath!, destinationPath);
                    // log success - file moved successfully
                }
                catch (Exception ex)
                {
                    // mark as not all files moved successfully
                    allFilesMovedSuccessfully = false;
                    // log exception details
                    _errors.Add(ex);
                }
            }

            return allFilesMovedSuccessfully;
        }

        #endregion move matched incoming files to current folder(s)


        #region move matched files to superseded folder

        private List<string> GetMatchedFilesInCurrentFolders(List<Document> currentDocuments)
        {
            // Summary:
            // loop through all matched documents
            // for each matched document, check if the document
            // has a match in the current folder(s)
            // if so, add the document to the list of matched files
            // return the list of matched files

            List<string> matchedFilesToSupersede = new List<string>();
            foreach (var incomingDocumentStatus in _matchedDocuments!)
            {
                // determine target current folder based on filing rules
                var targetCurrentFolder = DetermineTargetCurrentFolder(incomingDocumentStatus.NewDocumentPath);

                // get the location of old files to be superseded
                if (string.IsNullOrEmpty(targetCurrentFolder))
                {
                    // errors are logged inside DetermineTargetCurrentFolder
                    // skip to next document
                    continue;
                }

                // get all files in the target current folder
                var allFilesInTargetFolder = GetSupportedFilesFromFolder(targetCurrentFolder);

                if (allFilesInTargetFolder.Count == 0)
                {
                    // no files in target folder
                    // skip to next document
                    continue;
                }

                // find all files matching the incoming document number
                bool allFilesMatched = true;

                // loop through all incoming files and extract metadata
                foreach (var existingFilePath in allFilesInTargetFolder)
                {
                    // get the current document from the id of the matched document
                    var currentDocument = currentDocuments
                        .FirstOrDefault(d => d.Id == incomingDocumentStatus.MatchedDocumentId);

                    // extract metadata from file name
                    Models.IncomingDocumentStatus incomingDocument = ExtractDocumentMetadataFromFileName(
                        existingFilePath,
                        new List<Document>() { currentDocument! }
                    );

                    // check if a match was found
                    if (incomingDocument.MatchedDocumentId == null)
                    {
                        // specific errors are logged in the ExtractDocumentMetadataFromFileName method
                        allFilesMatched = false;

                        // skip to next file
                        continue;
                    }
                    matchedFilesToSupersede.Add(existingFilePath);
                }
            }

            return matchedFilesToSupersede;
        }

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
            
            List<string> matchedFiles = GetMatchedFilesInCurrentFolders(currentDocuments);
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
                    // check if file is locked
                    if (IsFileLocked(matchedFile))
                    {
                        allFilesMovedSuccessfully = false;
                        // log error - file is locked
                        continue;
                    }
                    // move file to superseded folder
                    var fileName = System.IO.Path.GetFileName(matchedFile);
                    var destinationPath = System.IO.Path.Combine(_supersededFolderPath!, fileName);
                    System.IO.File.Move(matchedFile, destinationPath);
                    // log success - file moved successfully
                }
                catch (Exception ex)
                {
                    // log exception details
                    _errors.Add(ex);

                    // mark as not all files moved successfully
                    allFilesMovedSuccessfully = false;
                }
            }

            return allFilesMovedSuccessfully;
        }

        #endregion move matched files to superseded folder
    }
}
