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
        #region supersede documents

        /// <summary>
        /// Attempts to match up files in the current folder system with incoming new versions of documents.
        /// If any matches are found these files are moved into the superseded location.
        /// </summary>
        /// <param name="newDocuments"></param>
        /// <returns>A list of file path of documents which could not be moved into the superseded location, combined with an error message why the move failed.</returns>
        public List<string>? SupersedeDocuments(List<Document> newDocuments)
        {
            throw new NotImplementedException();

            // check first if we have an incoming folder
            // check if there are any new documents
            // also need to make sure that the superseded folder exists
            // if not, create it
            // check if target current folder is set ( for single folder mode) and if not multiple folders are in use if all of them exist
            // otherwise create them
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

        }

        #endregion supersede documents
    }
}
