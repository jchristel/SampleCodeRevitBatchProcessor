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

using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.Database;
using duHastNet.DocManager.Core.Models.Results;

namespace duHastNet.DocManager.Core.Interfaces;

/// <summary>
/// High-level service interface for document management operations
/// Note: Methods return active documents by default unless explicitly stated otherwise
/// </summary>
public interface IDocumentService
{
    #region Revision Operations

    /// <summary>
    /// Creates a new revision batch
    /// </summary>
    Task<Revision> CreateRevisionAsync(DateTime revisionDate, string? description = null);

    /// <summary>
    /// Gets all revisions ordered by date (newest first)
    /// </summary>
    Task<List<Revision>> GetAllRevisionsAsync();

    /// <summary>
    /// Gets a revision by ID
    /// </summary>
    Task<Revision?> GetRevisionAsync(int revisionId);

    /// <summary>
    /// Updates a revision's description
    /// </summary>
    Task<Revision> UpdateRevisionAsync(int revisionId, string? description);

    /// <summary>
    /// Deletes a revision and all its documents
    /// </summary>
    Task DeleteRevisionAsync(int revisionId);

    /// <summary>
    /// Gets revisions within a date range
    /// </summary>
    Task<List<Revision>> GetRevisionsByDateRangeAsync(DateTime startDate, DateTime endDate);

    #endregion

    #region Document Operations (Active Documents by Default)

    /// <summary>
    /// Adds a document to an existing revision
    /// </summary>
    Task<Document> AddDocumentToRevisionAsync(int revisionId, string number, string name, string revision);

    /// <summary>
    /// Creates a new revision and adds multiple documents to it
    /// </summary>
    Task<Revision> CreateRevisionWithDocumentsAsync(DateTime revisionDate, string? description,
        IEnumerable<(string Number, string Name, string Revision)> documents);

    /// <summary>
    /// Gets all active documents for a specific revision
    /// </summary>
    Task<List<Document>> GetDocumentsByRevisionAsync(int revisionId);

    /// <summary>
    /// Gets the revision history for a specific document number (active documents only)
    /// </summary>
    Task<List<Document>> GetDocumentHistoryAsync(string documentNumber);

    /// <summary>
    /// Gets the latest active revision for each unique document number
    /// </summary>
    Task<List<Document>> GetLatestDocumentsAsync();

    /// <summary>
    /// Searches active documents by number, name, or revision
    /// </summary>
    Task<List<Document>> SearchDocumentsAsync(string searchTerm);

    /// <summary>
    /// Updates a document's information
    /// </summary>
    Task<Document> UpdateDocumentAsync(int documentId, string? name = null, string? revision = null);

    /// <summary>
    /// Deletes a specific document
    /// </summary>
    Task DeleteDocumentAsync(int documentId);

    #endregion

    #region Document Status Management (NEW)

    /// <summary>
    /// Gets all active documents
    /// </summary>
    Task<List<Document>> GetActiveDocumentsAsync();

    /// <summary>
    /// Gets all inactive documents
    /// </summary>
    Task<List<Document>> GetInactiveDocumentsAsync();

    /// <summary>
    /// Updates the active status of a document
    /// </summary>
    /// <param name="documentId">Document ID to update</param>
    /// <param name="isActive">New active status</param>
    /// <returns>Updated document</returns>
    Task<Document> UpdateDocumentActiveStatusAsync(int documentId, bool isActive);

    /// <summary>
    /// Activates a document
    /// </summary>
    Task<Document> ActivateDocumentAsync(int documentId);

    /// <summary>
    /// Deactivates a document
    /// </summary>
    Task<Document> DeactivateDocumentAsync(int documentId);

    #endregion

    #region Document History Management (NEW)

    /// <summary>
    /// Adds a document number to a document's history
    /// </summary>
    /// <param name="documentId">Document to update</param>
    /// <param name="historicalNumber">Historical document number to add</param>
    /// <param name="date">Date to associate with the historical number (optional, defaults to today)</param>
    Task<Document> AddDocumentToHistoryAsync(int documentId, string historicalNumber, DateOnly? date = null);

    /// <summary>
    /// Removes a document number from a document's history
    /// </summary>
    /// <param name="documentId">Document to update</param>
    /// <param name="historicalNumber">Historical document number to remove</param>
    Task<Document> RemoveDocumentFromHistoryAsync(int documentId, string historicalNumber);

    /// <summary>
    /// Gets documents that have the specified number in their history
    /// </summary>
    Task<List<Document>> GetDocumentsByHistoryNumberAsync(string documentNumber);

    /// <summary>
    /// Gets all document numbers ever used (current numbers + historical numbers)
    /// </summary>
    Task<List<string>> GetAllDocumentNumbersEverUsedAsync();

    /// <summary>
    /// Checks if a document number exists anywhere in the system (current or historical)
    /// </summary>
    Task<bool> DocumentNumberExistsAnywhereAsync(string documentNumber);

    #endregion

    #region All Documents Methods (Active and Inactive)

    /// <summary>
    /// Gets ALL documents for a specific revision (including inactive)
    /// </summary>
    Task<List<Document>> GetAllDocumentsByRevisionAsync(int revisionId);

    /// <summary>
    /// Gets complete revision history for a document number (including inactive)
    /// </summary>
    Task<List<Document>> GetCompleteDocumentHistoryAsync(string documentNumber);

    /// <summary>
    /// Searches ALL documents (active and inactive) by number, name, or revision
    /// </summary>
    Task<List<Document>> SearchAllDocumentsAsync(string searchTerm);

    #endregion

    #region Custom Properties Operations

    /// <summary>
    /// Adds or updates a custom property for a document
    /// </summary>
    Task<CustomProperty> SetDocumentCustomPropertyAsync(int documentId, string propertyName, string propertyValue);

    /// <summary>
    /// Gets all custom properties for a document
    /// </summary>
    Task<List<CustomProperty>> GetDocumentCustomPropertiesAsync(int documentId);

    /// <summary>
    /// Gets a specific custom property value for a document
    /// </summary>
    Task<string?> GetDocumentCustomPropertyAsync(int documentId, string propertyName);

    /// <summary>
    /// Removes a custom property from a document
    /// </summary>
    Task DeleteDocumentCustomPropertyAsync(int documentId, string propertyName);

    /// <summary>
    /// Gets all documents that have a specific custom property
    /// </summary>
    Task<List<Document>> GetDocumentsByCustomPropertyAsync(string propertyName, string? propertyValue = null);

    /// <summary>
    /// Gets all distinct custom property names used in the database
    /// </summary>
    Task<List<string>> GetCustomPropertyNamesAsync();

    #endregion

    #region Validation and Utility

    /// <summary>
    /// Validates document data before saving
    /// </summary>
    Task<ValidationResult> ValidateDocumentAsync(string number, string name, string revision);

    /// <summary>
    /// Checks if an active document with the same number and revision already exists
    /// </summary>
    Task<bool> DocumentExistsAsync(string number, string revision);

    /// <summary>
    /// Checks if ANY document (active or inactive) with the same number and revision exists
    /// </summary>
    Task<bool> AnyDocumentExistsAsync(string number, string revision);

    /// <summary>
    /// Gets statistics about the document database
    /// </summary>
    Task<DatabaseStatistics> GetDatabaseStatisticsAsync();

    #endregion
}