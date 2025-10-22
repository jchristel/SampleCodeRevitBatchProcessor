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
    /// <summary>
    /// A class which manages documents in a current folder or multiple folders.
    /// 
    /// A current folder or folders are defined as keeping the latest version of a document.
    /// Previous versions of a document are moved into a superseded folder
    /// 
    /// Multiple folder can be used when documentation is split into packages with a large number of documents each.
    /// This allows for multiple folders with an easier (less) document structure
    /// </summary>
    /// 
    public partial class CurrentFolderManager
    {
        /// <summary>
        /// Configuration settings for this manager instance
        /// </summary>
        private readonly CurrentFolderManagerSettings _settings;

        /// <summary>
        /// Gets the configuration settings for this manager
        /// </summary>
        public CurrentFolderManagerSettings Settings => _settings;

        /// <summary>
        /// Represents a collection of matched incoming document.
        /// </summary>
        /// <remarks>
        /// This field holds the statuses of incoming files that have been matched to a
        /// specific documents. It may be empty if no documents have been
        /// matched.
        /// This is runtime state that should not be persisted.
        /// </remarks>
        private List<Models.IncomingDocumentProcessingStatus> _matchedDocuments;

        /// <summary>
        /// Gets the collection of matched incoming documents
        /// </summary>
        public List<Models.IncomingDocumentProcessingStatus> MatchedDocuments
        {
            get { return _matchedDocuments; }
        }

        /// <summary>
        /// Contains any errors which occurred during operations
        /// This is runtime state that should not be persisted.
        /// </summary>
        private List<Exception> _errors;

        /// <summary>
        /// Gets the collection of errors that occurred during operations
        /// </summary>
        public List<Exception> Errors => _errors;

        #region filing rules delegation to settings

        /// <summary>
        /// Adds a filing rule to the configuration
        /// </summary>
        public void AddFilingRule(Interfaces.IFilingRule filingRule)
        {
            _settings.AddFilingRule(filingRule);
        }

        /// <summary>
        /// Removes a filing rule from the configuration
        /// </summary>
        public void RemoveFilingRule(Interfaces.IFilingRule filingRule)
        {
            _settings.RemoveFilingRule(filingRule);
        }

        /// <summary>
        /// Clears all filing rules
        /// </summary>
        public void ClearFilingRules()
        {
            _settings.ClearFilingRules();
        }

        #endregion

        #region supported file types delegation to settings

        /// <summary>
        /// Adds a supported file type to the configuration
        /// </summary>
        public void AddSupportedFileType(Models.SupportedFileType supportedFileType)
        {
            _settings.AddSupportedFileType(supportedFileType);
        }

        /// <summary>
        /// Removes a supported file type from the configuration
        /// </summary>
        public void RemoveSupportedFileType(Models.SupportedFileType supportedFileType)
        {
            _settings.RemoveSupportedFileType(supportedFileType);
        }

        /// <summary>
        /// Clears all supported file types
        /// </summary>
        public void ClearSupportedFileTypes()
        {
            _settings.ClearSupportedFileTypes();
        }

        #endregion

        /// <summary>
        /// Initializes a new instance of CurrentFolderManager with the specified settings
        /// </summary>
        /// <param name="settings">Configuration settings for the manager</param>
        public CurrentFolderManager(CurrentFolderManagerSettings settings)
        {
            _settings = settings ?? throw new ArgumentNullException(nameof(settings));
            _errors = new List<Exception>();
            _matchedDocuments = new List<Models.IncomingDocumentProcessingStatus>();
        }

        /// <summary>
        /// Initializes a new instance of CurrentFolderManager with default settings
        /// </summary>
        public CurrentFolderManager() : this(new CurrentFolderManagerSettings())
        {
        }
    }
}