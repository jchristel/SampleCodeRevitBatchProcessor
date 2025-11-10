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

namespace duHastNet.DocManager.Core.Models
{
    public class IncomingDocumentProcessingStatus
    {
        /// <summary>
        /// a class to hold
        /// - the fully qualified file path of the new document
        /// - process log messages
        /// - the database update status if applicable
        /// </summary>

        /// process messages collected during processing
        private List<(string,Stores.ProcessMessageTypes)> _processMessages;

        /// <summary>
        /// Add process messages collected during processing
        /// </summary> 
        public void AddProcessMessage(string message, Stores.ProcessMessageTypes messageType)
        {
            _processMessages.Add((message, messageType));
        }

        /// <summary>
        /// Overload to add exception messages as error process messages
        /// <paramref name="ex"/> The exception to add the message from
        /// </summary>
        public void AddProcessMessage(Exception ex)
        {
            _processMessages.Add((ex.Message, Stores.ProcessMessageTypes.Error));
        }

        /// the fully qualified file path of the new document
        private readonly string _newDocumentPath;

        /// the fully qualified file path of the new document
        public string? NewDocumentPath { get => _newDocumentPath; }

        /// <summary>
        /// The matched document id in the database if applicable
        /// null indicates no match found!
        /// </summary>
        public int? MatchedDocumentId { get; set; }

        public string? IncomingDocumentRevision { get; set; }

        /// <summary>
        /// Indicates if this is a duplicate document (multiple files with same file type matched to same document)
        /// </summary>
        public bool IsDuplicate { get; set; }

        /// <summary>
        /// Gets the list of other file paths that are duplicates of this document
        /// </summary>
        public List<string> DuplicateFilePaths { get; set; }

        public IncomingDocumentProcessingStatus(string newDocumentPath)
        {
            _newDocumentPath = newDocumentPath;
            _processMessages = [];
            DuplicateFilePaths = [];
        }
    }
}
