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
    /// <summary>
    /// a class which manages documents in a current folder or multiple folders.
    /// 
    /// A current folder or folders are defined as keeping the latest version of a document.
    /// Previous versions of a document are moved into a superseded folder
    /// 
    /// Multiple folder can be used when documentation is split into packages with a large number of documents each.
    /// This allowes for multiple folders with an easier (less) document structure
    /// </summary>
    /// 
    public partial class CurrentFolderManager
    {
        /// <summary>
        /// the path top the folder containing the incoming documents
        /// Documents in that folder will be moved to the current folder(s) if:
        /// - there is no matching document in the current location(s)
        /// - the previous version of the document was superseded succesfully (moved out of the current folder)
        /// </summary>
        private string? _incomingFolderPath;

        /// <summary>
        /// the path to the folder containing the current documents.
        /// Can be null if multiple folders are in use. Refer to folder distribution rules.
        /// </summary>
        private string? _currentFolderPath;

        /// <summary>
        /// the path to the folder containing all superseded documents. If null, documents will not be moved, if a newer version is added to the current folder(s)
        /// If the superseded folder allready contains a document (file) with the same name, ie. document manager has been run a number of times
        /// using the same documents, the document will be replaced with the new version.
        /// </summary>
        private string? _supersededFolderPath;

        /// <summary>
        /// a unique character in the file name indicating the start of a revision i.e. if the revision is indicated using square brackets: '[a]'
        /// the prefix is '['
        /// </summary>
        private string? _revisionPrefix;

        /// <summary>
        /// a unique character in the file name indicating the end of a revision, i.e. if the revision is indicated using square brackets: '[a]'
        /// the suffix is ']'
        /// </summary>
        private string? _revisionSuffix;

        /// <summary>
        /// These rules are used to distribute the documents to folders, if current document sets are maintained across multiples.
        /// </summary>
        private List<Interfaces.IFilingRule>? _filingRules;


        #region add new documents

        /// <summary>
        /// Attempts to move files from the incoming folder to current folder(s)
        /// </summary>
        /// <returns></returns>
        /// <exception cref="NotImplementedException"></exception>
        public List<string>? AddNewDocuments()
        {
            throw new NotImplementedException();
        }

        #endregion add new documents

        


        #region filing rules

        public void AddFilingRule(Interfaces.IFilingRule filingRule)
        {
            throw new NotImplementedException();
        }

        public void RemoveFilingRule(Interfaces.IFilingRule filingRule)
        {
            throw new NotImplementedException();
        }

        public void ClearFilingRules()
        {
            //clear all rules
            if (_filingRules != null)
            {
                _filingRules.Clear();
            }
        }


        #endregion

        public CurrentFolderManager ()
        {
            _filingRules = [];
        }
    }
}
