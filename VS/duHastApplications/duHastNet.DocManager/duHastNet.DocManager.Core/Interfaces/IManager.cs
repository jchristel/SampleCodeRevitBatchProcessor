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

using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.Database;

namespace duHastNet.DocManager.Core.Interfaces;

/// <summary>
/// Interface for Manager - manages in-memory collections of documents, revisions, and custom fields
/// </summary>
public interface IManager
{
    #region Properties

    /// <summary>
    /// Gets whether data has been loaded into the manager
    /// </summary>
    bool IsDataLoaded { get; }

    /// <summary>
    /// Gets or sets the cloud document manager
    /// </summary>
    Models.CloudDocManager.CloudDocumentManager? CloudDocManager { get; set; }

    #endregion

    #region Document Operations

    /// <summary>
    /// Gets all documents
    /// </summary>
    /// <returns>Collection of all documents</returns>
    IEnumerable<Document> GetAllDocuments();

    /// <summary>
    /// Gets all documents for a specific revision
    /// </summary>
    /// <param name="revisionId">Revision ID to filter by</param>
    /// <returns>Collection of documents for the specified revision</returns>
    IEnumerable<Document> GetAllDocumentsOfRevisionId(int revisionId);

    /// <summary>
    /// Adds a document to the collection
    /// </summary>
    /// <param name="doc">Document to add</param>
    void AddDocument(Document doc);

    #endregion

    #region Custom Field Operations

    /// <summary>
    /// Gets all custom property names
    /// </summary>
    /// <returns>Collection of custom property names</returns>
    IEnumerable<string> GetAllCustomPropertyNames();

    /// <summary>
    /// Gets all custom field definitions
    /// </summary>
    /// <returns>Collection of custom field definitions</returns>
    IEnumerable<CustomFieldDefinition> GetAllCustomFieldDefinitions();

    /// <summary>
    /// Gets only active custom field definitions
    /// </summary>
    /// <returns>Collection of active custom field definitions</returns>
    IEnumerable<CustomFieldDefinition> GetActiveCustomFieldDefinitions();

    #endregion

    #region Revision Operations

    /// <summary>
    /// Gets all revisions
    /// </summary>
    /// <returns>Collection of all revisions</returns>
    IEnumerable<Revision> GetAllRevisions();

    /// <summary>
    /// Adds a revision to the collection
    /// </summary>
    /// <param name="rev">Revision to add</param>
    void AddRevision(Revision rev);

    #endregion

    #region Data Management

    /// <summary>
    /// Clears all data from the manager
    /// </summary>
    void ClearData();

    #endregion
}
