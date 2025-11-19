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

namespace duHastNet.DocManager.Core.Exceptions
{
    /// <summary>
    /// Exception thrown when duplicate incoming files are detected - multiple files with the same file type matched to the same document
    /// </summary>
    public class IncomingFileDuplicateException : Exception
    {
        /// <summary>
        /// Gets the incoming file path that is a duplicate
        /// </summary>
        public string IncomingFilePath { get; }

        /// <summary>
        /// Gets the matched document ID in the database
        /// </summary>
        public int MatchedDocumentId { get; }

        /// <summary>
        /// Gets the list of other file paths that are duplicates
        /// </summary>
        public List<string> DuplicateFilePaths { get; }

        /// <summary>
        /// Gets the file extension of the duplicate files
        /// </summary>
        public string FileExtension { get; }

        /// <summary>
        /// Initializes a new instance of the <see cref="IncomingFileDuplicateException"/> class
        /// </summary>
        /// <param name="incomingFilePath">The file path that is a duplicate</param>
        /// <param name="matchedDocumentId">The document ID it matched to</param>
        /// <param name="duplicateFilePaths">List of other duplicate file paths</param>
        /// <param name="fileExtension">The file extension of the duplicates</param>
        public IncomingFileDuplicateException(
            string incomingFilePath, 
            int matchedDocumentId, 
            List<string> duplicateFilePaths, 
            string fileExtension)
            : base(BuildMessage(incomingFilePath, matchedDocumentId, duplicateFilePaths, fileExtension))
        {
            IncomingFilePath = incomingFilePath;
            MatchedDocumentId = matchedDocumentId;
            DuplicateFilePaths = duplicateFilePaths ?? new List<string>();
            FileExtension = fileExtension;
        }

        /// <summary>
        /// Initializes a new instance of the <see cref="IncomingFileDuplicateException"/> class with a custom message
        /// </summary>
        /// <param name="message">The error message</param>
        /// <param name="incomingFilePath">The file path that is a duplicate</param>
        /// <param name="matchedDocumentId">The document ID it matched to</param>
        /// <param name="duplicateFilePaths">List of other duplicate file paths</param>
        /// <param name="fileExtension">The file extension of the duplicates</param>
        public IncomingFileDuplicateException(
            string message,
            string incomingFilePath,
            int matchedDocumentId,
            List<string> duplicateFilePaths,
            string fileExtension)
            : base(message)
        {
            IncomingFilePath = incomingFilePath;
            MatchedDocumentId = matchedDocumentId;
            DuplicateFilePaths = duplicateFilePaths ?? new List<string>();
            FileExtension = fileExtension;
        }

        /// <summary>
        /// Initializes a new instance of the <see cref="IncomingFileDuplicateException"/> class with a custom message and inner exception
        /// </summary>
        /// <param name="message">The error message</param>
        /// <param name="innerException">The inner exception</param>
        /// <param name="incomingFilePath">The file path that is a duplicate</param>
        /// <param name="matchedDocumentId">The document ID it matched to</param>
        /// <param name="duplicateFilePaths">List of other duplicate file paths</param>
        /// <param name="fileExtension">The file extension of the duplicates</param>
        public IncomingFileDuplicateException(
            string message,
            Exception innerException,
            string incomingFilePath,
            int matchedDocumentId,
            List<string> duplicateFilePaths,
            string fileExtension)
            : base(message, innerException)
        {
            IncomingFilePath = incomingFilePath;
            MatchedDocumentId = matchedDocumentId;
            DuplicateFilePaths = duplicateFilePaths ?? new List<string>();
            FileExtension = fileExtension;
        }

        /// <summary>
        /// Builds a default error message for the exception
        /// </summary>
        private static string BuildMessage(
            string incomingFilePath, 
            int matchedDocumentId, 
            List<string> duplicateFilePaths, 
            string fileExtension)
        {
            var duplicateCount = (duplicateFilePaths?.Count ?? 0) + 1; // +1 for the current file
            var fileName = System.IO.Path.GetFileName(incomingFilePath);
            var duplicateFileNames = duplicateFilePaths?
                .Select(fp => System.IO.Path.GetFileName(fp))
                .ToList() ?? new List<string>();

            return $"Duplicate {fileExtension} file found for document ID {matchedDocumentId}. " +
                   $"Total duplicates: {duplicateCount}. " +
                   $"File: {fileName}, " +
                   $"Other duplicates: {string.Join(", ", duplicateFileNames)}";
        }
    }
}
