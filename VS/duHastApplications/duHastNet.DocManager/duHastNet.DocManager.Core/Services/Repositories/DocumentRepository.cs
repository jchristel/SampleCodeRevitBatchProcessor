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
/// Repository implementation for Document entities
/// Active documents are returned by default unless specifically requesting inactive/all documents
/// </summary>
public class DocumentRepository : BaseRepository<Document>, IDocumentRepository
{
    public DocumentRepository(SQLiteAsyncConnection connection) : base(connection)
    {
    }

    #region functions for active documents only

    public async Task<List<Document>> GetDocumentsByRevisionAsync(int revisionId)
    {
        return await _connection.Table<Document>()
            .Where(d => d.RevisionId == revisionId && d.IsActive)
            .OrderBy(d => d.Number)
            .ToListAsync();
    }

    public async Task<List<Document>> GetDocumentsByNumberAsync(string documentNumber)
    {
        return await _connection.Table<Document>()
            .Where(d => d.Number == documentNumber && d.IsActive)
            .OrderByDescending(d => d.Id) // Most recent first
            .ToListAsync();
    }

    public async Task<Document?> GetLatestDocumentRevisionAsync(string documentNumber)
    {
        return await _connection.Table<Document>()
            .Where(d => d.Number == documentNumber && d.IsActive)
            .OrderByDescending(d => d.Id)
            .FirstOrDefaultAsync();
    }

    public async Task<List<string>> GetDistinctDocumentNumbersAsync()
    {
        var documents = await _connection.Table<Document>()
            .Where(d => d.IsActive)
            .ToListAsync();

        return documents.Select(d => d.Number)
            .Distinct()
            .OrderBy(n => n)
            .ToList();
    }

    public async Task<List<Document>> SearchDocumentsAsync(string searchTerm)
    {
        var term = searchTerm.ToLower();

        return await _connection.Table<Document>()
            .Where(d => d.IsActive &&
                       (d.Number.ToLower().Contains(term) ||
                        d.Name.ToLower().Contains(term) ||
                        d.Revision.ToLower().Contains(term)))
            .OrderBy(d => d.Number)
            .ThenByDescending(d => d.Id)
            .ToListAsync();
    }

    public async Task<bool> DocumentExistsAsync(string number, string revision)
    {
        var count = await _connection.Table<Document>()
            .CountAsync(d => d.Number == number && d.Revision == revision && d.IsActive);

        return count > 0;
    }

    /// <summary>
    /// Gets all active documents
    /// </summary>
    public async Task<List<Document>> GetActiveDocumentsAsync()
    {
        return await _connection.Table<Document>()
            .Where(d => d.IsActive)
            .OrderBy(d => d.Number)
            .ToListAsync();
    }

    /// <summary>
    /// Updates the active status of a document
    /// </summary>
    /// <param name="documentId">Document ID to update</param>
    /// <param name="isActive">New active status</param>
    /// <returns>Number of records affected</returns>
    public async Task<int> UpdateActiveStatusAsync(int documentId, bool isActive)
    {
        var count = 0;
        await _connection.RunInTransactionAsync(conn =>
        {
            var document = conn.Find<Document>(documentId);
            if (document == null) return;

            document.IsActive = isActive;
            count = conn.Update(document);
        });
        return count;
    }

    #endregion

    #region inactive docs functions

    /// <summary>
    /// Gets all inactive documents
    /// </summary>
    public async Task<List<Document>> GetInactiveDocumentsAsync()
    {
        return await _connection.Table<Document>()
            .Where(d => !d.IsActive)
            .OrderBy(d => d.Number)
            .ToListAsync();
    }

    #endregion

    #region document history

    /// <summary>
    /// Finds documents that have the specified document number in their history
    /// </summary>
    /// <param name="documentNumber">Document number to search for in history</param>
    /// <returns>List of documents that have this number in their history</returns>
    public async Task<List<Document>> GetDocumentsByHistoryNumberAsync(string documentNumber)
    {
        // Since DocumentNumberHistory is stored as JSON, we need to search the JSON text
        // This is a simple LIKE search - for more complex queries, consider using FTS
        var documents = await _connection.Table<Document>()
            .Where(d => d.DocumentNumberHistoryJson.Contains($"\"{documentNumber}\""))
            .ToListAsync();

        // Filter results by actually checking the deserialized dictionary
        // to ensure accurate matching
        return documents.Where(d => d.DocumentNumberHistory.ContainsKey(documentNumber)).ToList();
    }

    /// <summary>
    /// Checks if any document has the given number in its current number or history
    /// This is useful for preventing conflicts when adding new documents
    /// </summary>
    /// <param name="documentNumber">Document number to check</param>
    /// <returns>True if the number exists anywhere in the system</returns>
    public async Task<bool> DocumentNumberExistsAnywhereAsync(string documentNumber)
    {
        // Check current document numbers
        var existsAsCurrent = await _connection.Table<Document>()
            .CountAsync(d => d.Number == documentNumber) > 0;

        if (existsAsCurrent) return true;

        // Check document histories
        var documentsWithHistory = await GetDocumentsByHistoryNumberAsync(documentNumber);
        return documentsWithHistory.Any();
    }

    /// <summary>
    /// Gets all document numbers from current documents and all histories
    /// Useful for generating reports or checking for complete uniqueness
    /// </summary>
    /// <returns>Distinct list of all document numbers ever used</returns>
    public async Task<List<string>> GetAllDocumentNumbersEverUsedAsync()
    {
        var allDocs = await GetAllAsync();
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
    /// Gets ALL documents by revision (including inactive) - for revision history tracking
    /// </summary>
    public async Task<List<Document>> GetAllDocumentsByRevisionAsync(int revisionId)
    {
        return await _connection.Table<Document>()
            .Where(d => d.RevisionId == revisionId)
            .OrderBy(d => d.Number)
            .ToListAsync();
    }

    /// <summary>
    /// Gets ALL documents by number (including inactive) - for complete document history
    /// </summary>
    public async Task<List<Document>> GetAllDocumentsByNumberAsync(string documentNumber)
    {
        return await _connection.Table<Document>()
            .Where(d => d.Number == documentNumber)
            .OrderByDescending(d => d.Id) // Most recent first
            .ToListAsync();
    }

    /// <summary>
    /// Checks if any document (active or inactive) exists with the given number and revision
    /// </summary>
    public async Task<bool> AnyDocumentExistsAsync(string number, string revision)
    {
        var count = await _connection.Table<Document>()
            .CountAsync(d => d.Number == number && d.Revision == revision);

        return count > 0;
    }

    #endregion
}