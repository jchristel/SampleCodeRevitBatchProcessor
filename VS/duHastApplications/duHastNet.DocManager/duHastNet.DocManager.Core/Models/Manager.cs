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

namespace duHastNet.DocManager.Core.Models
{
    public class Manager
    {
        /// <summary>
        /// contains all the documents
        /// </summary>
        private readonly DocumentContainer _documentContainer;

        /// <summary>
        /// Contains all the revisions
        /// </summary>
        private readonly RevisionContainer _revisionContainer;

        /// <summary>
        /// Contains all custom field definitions
        /// </summary>
        private readonly CustomFieldsContainer _customFieldContainer;

        /// <summary>
        /// Cloud document manager for metadata mapping and upload configuration
        /// </summary>
        private readonly CloudDocumentManager _cloudDocumentManager;

        /// <summary>
        /// Flag indicating data has been loaded from the database
        /// </summary>
        public bool IsDataLoaded { get; private set; }

        #region Documents

        #region get documents

        /// <summary>
        /// returns all documents
        /// </summary>
        /// <returns></returns>
        public IEnumerable<Document> GetAllDocuments()
        {
            return _documentContainer.GetAllDocuments();
        }

        /// <summary>
        /// Number of documents in the container
        /// </summary>
        public int DocumentCount
        {
            get { return _documentContainer.DocumentCount; }
        }

        /// <summary>
        /// Gets all documents with a matching revision id
        /// </summary>
        /// <param name="revisionId"></param>
        /// <returns></returns>
        public IEnumerable<Document> GetAllDocumentsOfRevisionId(int revisionId)
        {
            return _documentContainer.GetAllDocumentsOfRevisionId(revisionId);
        }

        #endregion get documents

        #region edit documents

        /// <summary>
        /// adds a document to the container
        /// </summary>
        /// <param name="doc"></param>
        public void AddDocument(Document doc)
        {
            _documentContainer.AddDocument(doc);
        }

        #endregion edit documents

        #region custom properties

        #region custom properties

        /// <summary>
        /// Returns a list of all custom property names in the document container
        /// </summary>
        /// <returns></returns>
        public IEnumerable<string> GetAllCustomPropertyNames()
        {
            return _documentContainer.GetAllCustomPropertyNames();
        }

        #endregion custom properties

        #region custom field definitions

        /// <summary>
        /// Returns all custom field definitions
        /// </summary>
        /// <returns></returns>
        public IEnumerable<CustomFieldDefinition> GetAllCustomFieldDefinitions()
        {
            return _customFieldContainer.GetAllCustomFields();
        }

        /// <summary>
        /// Returns only active custom field definitions
        /// </summary>
        /// <returns></returns>
        public IEnumerable<CustomFieldDefinition> GetActiveCustomFieldDefinitions()
        {
            return _customFieldContainer.GetActiveCustomFieldDefinitions();
        }

        /// <summary>
        /// Number of custom field definitions
        /// </summary>
        public int CustomFieldDefinitionCount
        {
            get { return _customFieldContainer.CustomFieldsCount; }
        }

        /// <summary>
        /// Adds a custom field definition to the list
        /// Called by DocManagerApi when loading data
        /// </summary>
        /// <param name="definition"></param>
        internal void AddCustomFieldDefinition(CustomFieldDefinition definition)
        {
            _customFieldContainer.AddCustomField(definition);
        }

        /// <summary>
        /// Clears all custom field definitions
        /// Called when clearing data
        /// </summary>
        internal void ClearCustomFieldDefinitions()
        {
            _customFieldContainer.ClearCustomFields();
        }

        #endregion custom field definitions

        #endregion custom properties

        #region Cloud Document Manager

        /// <summary>
        /// Gets the cloud document manager instance
        /// Used for metadata mapping configuration and validation
        /// </summary>
        public CloudDocumentManager CloudDocumentManager
        {
            get { return _cloudDocumentManager; }
        }

        #endregion Cloud Document Manager

        /// <summary>
        /// Exports the documents to a CSV file at the specified file path.
        /// </summary>
        /// <remarks>This method exports all documents contained in the current document container to a
        /// CSV file.  Ensure that the specified file path is accessible and that the application has the necessary
        /// permissions to write to it.</remarks>
        /// <param name="filePath">The full path, including the file name, where the CSV file will be created. The path must be valid and
        /// writable.</param>
        /// <returns><see langword="true"/> if the documents were successfully exported to the CSV file; otherwise, <see
        /// langword="false"/>.</returns>
        public bool ExportDocumentsToCsv(string filePath)
        {
            return _documentContainer.ExportDocumentsToCsv(filePath, _revisionContainer);
        }

        #endregion Documents

        #region Revisions

        #region get revisions

        /// <summary>
        /// returns all revisions
        /// </summary>
        /// <returns></returns>
        public IEnumerable<Revision> GetAllRevisions()
        {
            return _revisionContainer.GetAllRevisions();
        }

        /// <summary>
        /// number of revisions in the container
        /// </summary>
        public int RevisionCount
        {
            get { return _revisionContainer.RevisionCount; }
        }

        #endregion get revisions

        #region edit revisions

        /// <summary>
        /// adds a document to the container
        /// </summary>
        /// <param name="rev"></param>
        public void AddRevision(Revision rev)
        {
            _revisionContainer.AddRevision(rev);
        }

        #endregion edit revisions

        #endregion Revisions

        #region data operations

        /// <summary>
        /// Marks data as loaded (called by DocManagerApi after loading data)
        /// </summary>
        internal void MarkDataAsLoaded()
        {
            IsDataLoaded = true;
        }

        /// <summary>
        /// Clears the data in all containers
        /// </summary>
        public void ClearData()
        {
            _documentContainer.ClearDocuments();
            _revisionContainer.ClearRevisions();
            _customFieldContainer.ClearCustomFields();
        }


        #endregion data operations


        /// <summary>
        /// bussiness logic manager containing all documents and revisions of a project
        /// </summary>
        /// <param name="cloudDocumentManager">Cloud document manager instance (typically loaded from settings)</param>
        public Manager(CloudDocumentManager cloudDocumentManager)
        {
            _documentContainer = new DocumentContainer();
            _revisionContainer = new RevisionContainer();
            _customFieldContainer = new CustomFieldsContainer();
            _cloudDocumentManager = cloudDocumentManager ?? throw new ArgumentNullException(nameof(cloudDocumentManager));

            // set default loader flag
            IsDataLoaded = false;
        }
    }
}
