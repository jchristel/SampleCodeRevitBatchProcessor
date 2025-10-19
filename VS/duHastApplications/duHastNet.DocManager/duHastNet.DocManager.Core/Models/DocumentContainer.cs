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


using static System.Runtime.InteropServices.JavaScript.JSType;

namespace duHastNet.DocManager.Core.Models
{
    public class DocumentContainer
    {
        private List<Document> _documents;

        public int DocumentCount
        {
            get { return _documents.Count; }
        }

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

        #region custom properties

        /// <summary>
        /// Get a list of all the custom property names
        /// </summary>
        /// <returns></returns>
        public List<string> GetAllCustomPropertyNames()
        {
            //get the custom property names of the first document only since they are the same for all documents
            if (_documents.Count == 0)
            {
                return [];
            }

            var doc = _documents[0];
            List<string> propertyNames = [];
            foreach (var prop in doc.CustomProperties)
            {
                propertyNames.Add(prop.PropertyName);
            }
            
            return propertyNames;
        }


        #endregion custom properties

        #region edit documents

        /// <summary>
        /// removes all documents from the container
        /// </summary>
        public void ClearDocuments()
        {
            _documents.Clear();
        }

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

        #region export documents to csv

        public bool ExportDocumentsToCsv(string filePath)
        {
            try
            {
                //prepare header with default columns
                List<string> header = ["DocumentId", "Number", "Name", "IsActive", "Revision", "Revision Description", "Revision Date"];

                //prepare header add custom property names
                var customPropertyNames = GetAllCustomPropertyNames();
                header.AddRange(customPropertyNames);

                // prepare data rows
                List<List<string>> data = [];

                foreach (var doc in _documents)
                {
                    List<string> row = [];
                    row.Add(doc.Id.ToString());
                    row.Add(doc.Number);
                    row.Add(doc.Name);
                    row.Add(doc.IsActive.ToString());
                    row.Add(doc.Revision);
                    row.Add(doc.RevisionDescription ?? string.Empty);
                    row.Add(doc.RevisionDate.ToString("yyyy-MM-dd"));
                    // add custom property values
                    foreach (var propName in customPropertyNames)
                    {
                        var prop = doc.CustomProperties.FirstOrDefault(p => p.PropertyName == propName);
                        row.Add(prop != null ? prop.PropertyValue : string.Empty);
                    }
                    data.Add(row);
                }


                return true;
            }
            catch (Exception ex)
            {
                // Handle exceptions as needed
                Console.WriteLine($"Error exporting documents to CSV: {ex.Message}");
                return false;
            }
        }

        

        #endregion export documents to csv

        public DocumentContainer()
        {
            _documents = [];
        }
    }
}
