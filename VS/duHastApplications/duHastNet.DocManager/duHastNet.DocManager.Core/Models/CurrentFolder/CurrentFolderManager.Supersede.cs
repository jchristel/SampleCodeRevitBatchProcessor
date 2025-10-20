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

        #region identifying incoming files and matching them to current documents

        /// <summary>
        /// Checks if there are any supported files in the incoming folder.
        /// if any errors occur during the process, they are logged in the _errors list.
        /// if no supported files are found, an empty list is returned.
        /// </summary>
        private List<string> GetSupportedFilesFromFolder(string? folderPath)
        {
            List<string> supportedIncomingFiles = [];

            if (string.IsNullOrEmpty( folderPath) || !System.IO.Directory.Exists(folderPath))
            {
                // log error
                _errors.Add(new Exceptions.FolderDoesNotExistException(folderPath ?? "null"));
                return supportedIncomingFiles;
            }

            // check if there are any new documents
            List<string> incomingFiles = System.IO.Directory.GetFiles(folderPath, "*", System.IO.SearchOption.AllDirectories).ToList();

            if (incomingFiles.Count == 0)
            {
                // log info
                _errors.Add(new Exceptions.IncomingFolderEmptyException());
                return supportedIncomingFiles;
            }

            // check if there are supported file types in the incoming folder
            if (_supportedFileTypes != null && _supportedFileTypes.Count != 0)
            {

                // check supported file types
                supportedIncomingFiles = incomingFiles.Where(file =>
                    _supportedFileTypes.Any(supportedType =>
                        file.EndsWith(supportedType.FileExtension, StringComparison.OrdinalIgnoreCase))).ToList();

                if (supportedIncomingFiles.Count == 0)
                {
                    // build a list of supported file types
                    string supportedTypesList = string.Join(", ", _supportedFileTypes.Select(t => t.FileExtension));

                    // log info
                    _errors.Add(new Exceptions.IncomingFolderEmptyException($"Incoming folder does not contain any supported file type: {supportedTypesList}"));
                    return supportedIncomingFiles;
                }
            }
            else
            {
                // log error
                _errors.Add(new Exceptions.IncomingFolderEmptyException("No supported file types defined, all files in incoming folder will be ignored."));
                return supportedIncomingFiles;
            }

            return supportedIncomingFiles;
        }

        /// <summary>
        /// Validates if all prerequisites are met to start the supersede process
        /// </summary>
        /// <returns></returns>
        private bool ValidateSupersedePrerequisites()
        {
            // check first if we have an incoming folder
            // check if there are any new documents
            // also need to make sure that the superseded folder exists
            // check if target current folder is set ( for single folder mode) and if not multiple folders are in use if all of them exist
            // return true if all prerequisites are met, otherwise false
            // check revision prefix and suffix are set

            //check incoming folder
            var files = GetSupportedFilesFromFolder(_incomingFolderPath);
            if (files.Count == 0)
            {
                return false;
            }
            
            //check if current folder or folders exists
            if (string.IsNullOrEmpty(_currentFolderPath) && (_filingRules == null || _filingRules.Count == 0))
            {
                // log error
                _errors.Add(new Exceptions.FolderDoesNotExistException("Current folder path is not set and no filing rules defined for multiple folder mode."));
                return false;
            }

            //if there is a single current folder mode, check if that folder exists
            if (!string.IsNullOrEmpty(_currentFolderPath))
            {
                if (!System.IO.Directory.Exists(_currentFolderPath))
                {
                    // log error
                    _errors.Add(new Exceptions.FolderDoesNotExistException("Current folder path does not exist.", _currentFolderPath));
                    return false;
                }
            }

            // check if we are in multiple folder mode but no folders are defined
            if (string.IsNullOrEmpty(_currentFolderPath) && _filingRules!=null && _filingRules.Count == 0)
            {
                // single folder mode but no folder set
                // log error
                _errors.Add(new Exceptions.FolderDoesNotExistException("Current folder path is not set and no filing rules defined for multiple folder mode."));
                return false;
            }

            //check if multiple current folders are in use
            if (_filingRules != null && _filingRules.Count > 0)
            {
                // multiple folders in use, check if all superseded folders exist
                bool allFoldersExist = true;

                // multiple folders in use, check if all superseded folders exist
                foreach (var rule in _filingRules)
                {
                    if (!System.IO.Directory.Exists(rule.TargetDirectory))
                    {
                        // log error
                        _errors.Add(new Exceptions.FolderDoesNotExistException(rule.Description, rule.TargetDirectory));
                        allFoldersExist = false;
                    }
                }

                // return false if any folder does not exist
                if (!allFoldersExist)
                {
                    return false;
                }
            }
            
            // check superseded folder
            if (string.IsNullOrEmpty(_supersededFolderPath))
            {
                // folder is not set, log error
                _errors.Add(new Exceptions.FolderDoesNotExistException("Supersede folder path is not set."));

            }


            // check revision prefix and suffix are set
            if (string.IsNullOrEmpty(_revisionPrefix) || string.IsNullOrEmpty(_revisionSuffix))
            {
                // log error
                _errors.Add(new Exceptions.InvalidRevisionFormatException("Revision prefix and/or suffix are not set."));
                return false;
            }

            return true;
        }

        /// <summary>
        /// Generates a list of document number options based on the provided document number and supported file types.
        /// </summary>
        /// <param name="number">The original document number to be processed.</param>
        /// <returns>A list of document number options. If supported file types are defined, the list contains modified document
        /// numbers based on each supported file type. If no supported file types are defined, the list contains the
        /// original document number.</returns>
        private List<string> GetDocumentNumberOptionsForDocument(string number)
        {
            List<string> documentNumberOptions = new List<string>();
            if (_supportedFileTypes != null && _supportedFileTypes.Count != 0)
            {
                // loop over all supported file types and get modified document numbers
                foreach (var supportedType in _supportedFileTypes)
                {
                    string modifiedNumber = supportedType.GetModifiedDocumentNumber(number);
                    documentNumberOptions.Add(modifiedNumber);
                }
            }
            else
            {
                // no supported file types defined, use original number
                documentNumberOptions.Add(number);
            }
            return documentNumberOptions;
        }

        /// <summary>
        /// Returns the document id based on the document number extracted from the specified file name by comparing it against a list of current documents.
        /// </summary>
        /// <param name="fileName"></param>
        /// <param name="currentDocuments"></param>
        /// <param name="incomingDocumentStatus"></param>
        /// <returns></returns>
        private int? GetDocumentIdFromFileName(string fileName, List<Document> currentDocuments, IncomingDocumentProcessingStatus incomingDocumentStatus)
        {
            // Summary:
            // extract document number from file name
            // this is a simplified example, actual implementation may vary based on naming conventions
            int? documentId = null;

            //dictionary to hold document number options and their corresponding files
            Dictionary<string, int> docNumberMatchesMapper = [];

            // loop over all documents in the database and check if the file name contains the document number
            foreach (var doc in currentDocuments)
            {
                //get the various document numbers for each supported document type of the base document
                List<string> documentNumberOptions = GetDocumentNumberOptionsForDocument(doc.Number);

                
                foreach (var docNumberOption in documentNumberOptions)
                {
                    // check if file name contains the document number option
                    if (fileName.Contains(docNumberOption, StringComparison.OrdinalIgnoreCase))
                    {
                        docNumberMatchesMapper[docNumberOption] = doc.Id;
                    }
                }
            }

            // check if we have multiple matches
            // there is the possbility that a file name contains multiple matches i.e.
            // DOC-123 and DOC-123-DWG
            // in that case we need to select the most specific match (i.e. the longest match)
            if (docNumberMatchesMapper.Count > 0)
            {
                // select the longest match (key value) from the mapping dictionary
                var documentNumber = docNumberMatchesMapper.Keys.OrderByDescending(s => s.Length).First();
                documentId = docNumberMatchesMapper[documentNumber];

                // log success
                incomingDocumentStatus.AddProcessMessage(
                    $"Extracted document number '{documentNumber}' from file name '{fileName}' and matched to document id {documentId}.",
                    Stores.ProcessMessageTypes.Information
                );
            }
            else
            {
                // log error
                incomingDocumentStatus.AddProcessMessage(
                    new Exceptions.DocumentNotFoundException(fileName)
                );
            }

            return documentId;
        }

        /// <summary>
        /// Extracts the revision identifier from the specified file name based on the configured prefix and suffix.
        /// </summary>
        /// <remarks>This method relies on the presence of a configured revision prefix and suffix to
        /// locate the revision  within the file name. If either the prefix or suffix is not set, or if they are not
        /// found in the file name,  the method returns <see langword="null"/> and logs an error. Additionally, if the
        /// prefix appears after the  suffix in the file name, the method logs an error and returns <see
        /// langword="null"/>.</remarks>
        /// <param name="fileName">The name of the file from which to extract the revision identifier.</param>
        /// <param name="incomingDocumentStatus">The status object used to log processing messages.</param>
        /// <returns>The extracted revision identifier if both the prefix and suffix are found and properly formatted; 
        /// otherwise, <see langword="null"/>.</returns>
        private string? GetRevisionFromFileName(string fileName, IncomingDocumentProcessingStatus incomingDocumentStatus)
        {
            // Summary:
            // extract revision from file name
            string? revision = null;

            // check if revision prefix and suffix are set
            if (_revisionPrefix == null || _revisionSuffix == null)
            {
                return revision;
            }
            int revisionEndIndex = fileName.LastIndexOf(_revisionSuffix);
            int revisionStartIndex = fileName.LastIndexOf(_revisionPrefix);

            // check if both prefix and suffix are found
            if (revisionStartIndex == -1)
            {
                //log error
                incomingDocumentStatus.AddProcessMessage(new Exceptions.InvalidRevisionFormatException($"Revision prefix '{_revisionPrefix}' not found in file name '{fileName}'"));
            }

            if (revisionEndIndex == -1)
            {
                //log error
                incomingDocumentStatus.AddProcessMessage(new Exceptions.InvalidRevisionFormatException($"Revision suffix '{_revisionSuffix}' not found in file name '{fileName}'"));
            }

            if (revisionEndIndex > revisionStartIndex)
            {
                // extract revision
                int start = revisionStartIndex + _revisionPrefix.Length;
                int length = revisionEndIndex - start;
                revision = fileName.Substring(start, length);

                //log success
                incomingDocumentStatus.AddProcessMessage(
                    $"Extracted revision '{revision}' from file name '{fileName}'.",
                    Stores.ProcessMessageTypes.Information
                );
            }
            else
            {
                // log error
                incomingDocumentStatus.AddProcessMessage(new Exceptions.InvalidRevisionFormatException($"Invalid revision format in file name '{fileName}'"));
            }

            return revision;
        }

        /// <summary>
        /// extracts document metadata from the specified file name and compares it against a list of current documents to find a match.
        /// <paramref name="filePath"/> The full path of the file to extract metadata from.
        /// <paramref name="currentDocuments"/> The list of current documents to compare against.
        /// </summary>  
        private Models.IncomingDocumentProcessingStatus ExtractDocumentMetadataFromFileName(string filePath, List<Document> currentDocuments)
        {
            // Summary:
            // extract document number and revision from file name
            // compare extracted metadata with current documents in the database
            // if a match is found, return IncomingDocumentStatus with matched document id
            // if no match is found, return IncomingDocumentStatus with null matched document id
            Models.IncomingDocumentProcessingStatus incomingDocumentStatus = new Models.IncomingDocumentProcessingStatus(filePath);
            string fileName = System.IO.Path.GetFileNameWithoutExtension(filePath);

            // extract document number (doc id) and revision from file name
            int? documentId = GetDocumentIdFromFileName(
                fileName, 
                currentDocuments,
                incomingDocumentStatus
            );

            if (documentId == null)
            {
                // return with no match
                return incomingDocumentStatus;
            }

            //store the id of the matched document
            incomingDocumentStatus.MatchedDocumentId = documentId;

            // extract revision
            string? revision = GetRevisionFromFileName(fileName, incomingDocumentStatus);
            
            if (revision == null)
            {
                // return with no match
                return incomingDocumentStatus;
            }
            
            // set incoming document revision
            incomingDocumentStatus.IncomingDocumentRevision = revision;

            
            return incomingDocumentStatus;
        }

        /// <summary>
        /// matches incoming files against current documents in the database.
        /// </summary>
        /// <param name="currentDocuments"></param>
        /// <returns>true if all files where matched to documents, otherwise false</returns>
        private bool MatchIncomingFilesToDocuments (List<Document> currentDocuments)
        {
            // loop through all incoming files
            // for each file, extract document metadata (number, revision, etc)
            // compare extracted metadata with current documents in the database
            // if a match is found, add to matchedDocuments list with status indicating a match
            // if no match is found, add to matchedDocuments list with status indicating no match
            
            List<string> incomingFiles = GetSupportedFilesFromFolder(_incomingFolderPath);
            // proceed only if there are incoming files, errors are logged in the GetSupportedFilesFromIncomingFolder method
            if (incomingFiles.Count == 0)
            {
                // log error
                return false;
            }

            // whipe matched documents list
            if (_matchedDocuments == null)
            {
                _matchedDocuments = new List<Models.IncomingDocumentProcessingStatus>();
            }
            else
            {
                _matchedDocuments.Clear();
            }

            // flag to indicate if all files were matched successfully
            bool allFilesMatched = true;

            // loop through all incoming files and extract metadata
            foreach (var filePath in incomingFiles)
            {
                // extract metadata from file name
                Models.IncomingDocumentProcessingStatus incomingDocument = ExtractDocumentMetadataFromFileName(
                    filePath, 
                    currentDocuments
                );

                // check if a match was found
                if (incomingDocument.MatchedDocumentId == null)
                {
                    // specific errors are logged in the ExtractDocumentMetadataFromFileName method
                    allFilesMatched = false;
                }
                _matchedDocuments.Add(incomingDocument);
            }

            return allFilesMatched;
        }

        #endregion identifying incoming files and matching them to current documents

        
        #region supersede documents

        /// <summary>
        /// Attempts to match up files in the current folder system with incoming new versions of documents.
        /// If any matches are found these files are moved into the superseded location.
        /// </summary>
        /// <param name="currentDocuments">The list of current documents in the database</param>
        /// <returns>A list of file path of documents which could not be moved into the superseded location, combined with an error message why the move failed.</returns>
        public bool SupersedeDocuments(List<Document> currentDocuments)
        {
            // Summary:
            // check first if we have an incoming folder
            // check if there are any new documents
            // also need to make sure that the superseded folder exists
            // check if target current folder is set ( for single folder mode) and if not multiple folders are in use if all of them exist
            // when superseding documents, we need to make sure that the document to be moved is not locked by another process
            // if it is locked, we cannot move it and need to log that as an error
            // need to loop through all new documents and identify for each of them if there is a matching document in the database
            // if a document is found without a match in the database log a warning and skip to next document
            // check if the there are matching documents which need to be superseded, if so check if they are locked
            // if not locked, move them to the superseded folder
            // if locked, log an error and skip to next document
            // need to keep track of which files got superseded successfully and which not in global lists
            // need to whipe that list first
            // need to log results for user information

            bool prerequisitesMet = ValidateSupersedePrerequisites();

            // proceed only if all prerequisites are met
            if (!prerequisitesMet)
            {
                // log error
                return false;
            }

            // match incoming files against current documents
            bool matchedDocuments = MatchIncomingFilesToDocuments(currentDocuments);
            
            // proceed only if matching was successful
            if (!matchedDocuments)
            {
                // log error
                return false;
            }

            // loop through all matched documents and supersede them
            // move matched documents to superseded folder
            // unlike the other steps, this step can partially fail, so we proceed even if some files could not be moved
            bool moveSupersededFiles = MoveMatchedFilesToSupersededFolder(currentDocuments);

            //move incoming documents to current folder(s)
            //unlike the other steps, this step can partially fail, so we proceed even if some files could not be moved
            bool moveIncomingFiles = MoveMatchedIncomingFilesToCurrentFolders(currentDocuments);

            // return the result of both move operations
            // both need to be successful for the overall operation to be considered successful
            return moveSupersededFiles && moveIncomingFiles;

        }

        #endregion supersede documents
    }
}
