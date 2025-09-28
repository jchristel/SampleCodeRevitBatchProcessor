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
    public class DocumentContainer
    {
        private List<Document> _documents;

        #region get documents

        /// <summary>
        /// returns all documents
        /// </summary>
        /// <returns></returns>
        public IEnumerable<Document> GetAllDocuments()
        {
            return _documents;
        }

        /// <summary>
        /// Gets all documents with a matching revision id
        /// </summary>
        /// <param name="revisionId"></param>
        /// <returns></returns>
        public IEnumerable<Document> GetAllDocumentsOfRevisionId(int  revisionId)
        {
            return _documents.Where(x => x.RevisionId == revisionId);
        }

        #endregion get documents

        #region edit documents

        /// <summary>
        /// adds a document to the container
        /// </summary>
        /// <param name="doc"></param>
        public void AddDocument(Document doc)
        {
            //null check
            if (doc == null)
            {
                throw new ArgumentNullException(nameof(doc), "Document cannot be null.");
            }

            //check if a document with this number allready exists
            foreach (var existingDocument in _documents)
            {
                if (existingDocument.Conflicts(doc))
                { 
                    throw new Exceptions.DocumentDuplicateException(existingDocument, doc); 
                }
            }

            //no conflict found - add document
            _documents.Add(doc);
        }

        #endregion edit documents

        public DocumentContainer()
        {
            _documents = [];
        }
    }
}
