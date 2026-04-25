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

using duHastNet.DocManager.Core.Interfaces;
using duHastNet.DocManager.Core.Models;
using SQLite;

namespace duHastNet.DocManager.Core.Services.Repositories;

/// <summary>
/// Synchronous repository implementation for Document entities.
/// Active documents are returned by default unless specifically requesting inactive/all documents.
/// Provides sync methods for IronPython/PyRevit compatibility.
/// </summary>
public class DocumentRepositorySync : BaseRepositorySync<Document>, IDocumentRepositorySync
{
    public DocumentRepositorySync(SQLiteConnection connection) : base(connection)
    {
    }

    #region functions for active documents only

    public List<Document> GetDocumentsByRevision(int revisionId)
    {
        return _connection.Table<Document>()
            .Where(d => d.RevisionId == revisionId && d.IsActive)
            .OrderBy(d => d.Number)
            .ToList();
    }

    public List<Document> GetDocumentsByNumber(string documentNumber)
    {
        return _connection.Table<Document>()
            .Where(d => d.Number == documentNumber && d.IsActive)
            .OrderByDescending(d => d.Id) // Most recent first
            .ToList();
    }

    public Document? GetLatestDocumentRevision(string documentNumber)
    {
        return _connection.Table<Document>()
            .Where(d => d.Number == documentNumber && d.IsActive)
            .OrderByDescending(d => d.Id)
            .FirstOrDefault();
    }

    public List<string> GetDistinctDocumentNumbers()
    {
        var documents = _connection.Table<Document>()
            .Where(d => d.IsActive)
            .ToList();

        return documents.Select(d => d.Number)
            .Distinct()
            .OrderBy(n => n)
            .ToList();
    }

    public List<Document> SearchDocuments(string searchTerm)
    {
        var term = searchTerm.ToLower();

        return _connection.Table<Document>()
            .Where(d => d.IsActive &&
                       (d.Number.ToLower().Contains(term) ||
                        d.Name.ToLower().Contains(term) ||
                        d.Revision.ToLower().Contains(term)))
            .OrderBy(d => d.Number)
            .ThenByDescending(d => d.Id)
            .ToList();
    }

    public bool DocumentExists(string number, string revision)
    {
        var count = _connection.Table<Document>()
            .Count(d => d.Number == number && d.Revision == revision && d.IsActive);

        return count > 0;
    }

    /// <summary>
    /// Gets all active documents (sync version)
    /// </summary>
    public List<Document> GetActiveDocuments()
    {
        return _connection.Table<Document>()
            .Where(d => d.IsActive)
            .OrderBy(d => d.Number)
            .ToList();
    }

    /// <summary>
    /// Updates the active status of a document (sync version)
    /// </summary>
    /// <param name="documentId">Document ID to update</param>
    /// <param name="isActive">New active status</param>
    /// <returns>Number of records affected</returns>
    public int UpdateActiveStatus(int documentId, bool isActive)
    {
        var count = 0;
        _connection.RunInTransaction(() =>
        {
            var document = _connection.Find<Document>(documentId);
            if (document == null) return;

            document.IsActive = isActive;
            count = _connection.Update(document);
        });
        return count;
    }

    #endregion

    #region inactive docs functions

    /// <summary>
    /// Gets all inactive documents (sync version)
    /// </summary>
    public List<Document> GetInactiveDocuments()
    {
        return _connection.Table<Document>()
            .Where(d => !d.IsActive)
            .OrderBy(d => d.Number)
            .ToList();
    }

    #endregion

    #region document history

    /// <summary>
    /// Finds documents that have the specified document number in their history (sync version)
    /// </summary>
    /// <param name="documentNumber">Document number to search for in history</param>
    /// <returns>List of documents that have this number in their history</returns>
    public List<Document> GetDocumentsByHistoryNumber(string documentNumber)
    {
        // DocumentNumberHistoryJson stores keys as quoted strings e.g. {"A-101-OLD":"2024-01-01"}.
        // We pre-filter using a LIKE search on the raw number, then apply the accurate
        // in-memory check on the deserialized dictionary to eliminate any false positives.
        var documents = _connection.Table<Document>()
            .Where(d => d.DocumentNumberHistoryJson.Contains(documentNumber))
            .ToList();

        // In-memory filter ensures accurate matching via the deserialized dictionary
        return documents.Where(d => d.DocumentNumberHistory.ContainsKey(documentNumber)).ToList();
    }

    /// <summary>
    /// Checks if any document has the given number in its current number or history (sync version)
    /// This is useful for preventing conflicts when adding new documents
    /// </summary>
    /// <param name="documentNumber">Document number to check</param>
    /// <returns>True if the number exists anywhere in the system</returns>
    public bool DocumentNumberExistsAnywhere(string documentNumber)
    {
        // Check current document numbers
        var existsAsCurrent = _connection.Table<Document>()
            .Count(d => d.Number == documentNumber) > 0;

        if (existsAsCurrent) return true;

        // Check document histories
        var documentsWithHistory = GetDocumentsByHistoryNumber(documentNumber);
        return documentsWithHistory.Any();
    }

    /// <summary>
    /// Gets all document numbers from current documents and all histories (sync version)
    /// Useful for generating reports or checking for complete uniqueness
    /// </summary>
    /// <returns>Distinct list of all document numbers ever used</returns>
    public List<string> GetAllDocumentNumbersEverUsed()
    {
        var allDocs = GetAll();
        var allNumbers = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

        foreach (var doc in allDocs)
        {
            // Add current number
            allNumbers.Add(doc.Number);

            // Add all numbers from history
            foreach (var historyNumber in doc.DocumentNumberHistory.Keys)
            {
                allNumbers.Add(historyNumber);
            }
        }

        return allNumbers.OrderBy(n => n).ToList();
    }

    #endregion

    #region all documents (active and inactive) when specifically needed

    /// <summary>
    /// Gets ALL documents by revision (including inactive) - for revision history tracking (sync version)
    /// </summary>
    public List<Document> GetAllDocumentsByRevision(int revisionId)
    {
        return _connection.Table<Document>()
            .Where(d => d.RevisionId == revisionId)
            .OrderBy(d => d.Number)
            .ToList();
    }

    /// <summary>
    /// Gets ALL documents by number (including inactive) - for complete document history (sync version)
    /// </summary>
    public List<Document> GetAllDocumentsByNumber(string documentNumber)
    {
        return _connection.Table<Document>()
            .Where(d => d.Number == documentNumber)
            .OrderByDescending(d => d.Id) // Most recent first
            .ToList();
    }

    /// <summary>
    /// Checks if any document (active or inactive) exists with the given number and revision (sync version)
    /// </summary>
    public bool AnyDocumentExists(string number, string revision)
    {
        var count = _connection.Table<Document>()
            .Count(d => d.Number == number && d.Revision == revision);

        return count > 0;
    }

    #endregion
}
