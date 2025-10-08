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
        /// The cloud meta data interface implementation
        /// </summary>
        private readonly Interfaces.ICloudMetaData _cloudMetaData;

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

        /// <summary>
        /// Returns a list of all custom property names in the document container
        /// </summary>
        /// <returns></returns>
        public IEnumerable<string> GetAllCustomPropertyNames()
        {
            return _documentContainer.GetAllCustomPropertyNames();
        }

        #endregion custom properties

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
        }


        #endregion data operations
        /// <summary>
        /// bussiness logic manager containing all documents and revisions of a project
        /// </summary>
        public Manager() 
        { 
            _documentContainer = new DocumentContainer();
            _revisionContainer = new RevisionContainer();

            // set default loader flag
            IsDataLoaded = false;
        }
    }
}
