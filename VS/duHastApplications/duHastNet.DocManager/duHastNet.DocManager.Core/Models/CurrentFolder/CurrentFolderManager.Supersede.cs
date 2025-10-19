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

            //check incoming folder
            if (string.IsNullOrEmpty(_incomingFolderPath) || !System.IO.Directory.Exists(_incomingFolderPath))
            {
                // log error
                _errors.Add(new Exceptions.FolderDoesNotExistException(_incomingFolderPath ?? "null"));
                return false;
            }

            // check if there are any new documents
            List<string> incomingFiles = System.IO.Directory.GetFiles(_incomingFolderPath, "*", System.IO.SearchOption.AllDirectories).ToList();
            
            if (incomingFiles.Count == 0)
            {
                // log info
                _errors.Add(new Exceptions.IncomingFolderEmptyException());
                return false;
            }

            // check if there are supported file types in the incoming folder
            if (_supportedFileTypes != null && _supportedFileTypes.Count != 0)
            {

                // check supported file types
                List<string> supportedIncomingFiles = incomingFiles.Where(file =>
                    _supportedFileTypes.Any(supportedType =>
                        file.EndsWith(supportedType.FileExtension, StringComparison.OrdinalIgnoreCase))).ToList();

                if (supportedIncomingFiles.Count == 0)
                {
                    // build a list of supported file types
                    string supportedTypesList = string.Join(", ", _supportedFileTypes.Select(t => t.FileExtension));

                    // log info
                    _errors.Add(new Exceptions.IncomingFolderEmptyException($"Incoming folder does not contain any supported file type: {supportedTypesList}"));
                    return false;
                }
            }
            else
            {
                // log error
                _errors.Add(new Exceptions.IncomingFolderEmptyException("No supported file types defined, all files in incoming folder will be ignored."));
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
                    if (!System.IO.Directory.Exists(rule.TargetFolderPath))
                    {
                        // log error
                        _errors.Add(new Exceptions.FolderDoesNotExistException(rule.Description, rule.TargetFolderPath));
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
            return true;
        }

        private bool MatchIncomingFilesToDocuments (List<Document> currentDocuments)
        {
            // loop through all incoming files
            // for each file, extract document metadata (number, revision, etc)
            // compare extracted metadata with current documents in the database
            // if a match is found, add to matchedDocuments list with status indicating a match
            // if no match is found, add to matchedDocuments list with status indicating no match
            return true;
        }

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

            return true;

        }

        #endregion supersede documents
    }
}
