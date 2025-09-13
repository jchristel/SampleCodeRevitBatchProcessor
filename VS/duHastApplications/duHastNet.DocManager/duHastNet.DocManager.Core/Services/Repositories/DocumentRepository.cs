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
/// </summary>
public class DocumentRepository : BaseRepository<Document>, IDocumentRepository
{
    public DocumentRepository(SQLiteAsyncConnection connection) : base(connection)
    {
    }

    public async Task<List<Document>> GetDocumentsByRevisionAsync(int revisionId)
    {
        return await _connection.Table<Document>()
            .Where(d => d.RevisionId == revisionId)
            .OrderBy(d => d.Number)
            .ToListAsync();
    }

    public async Task<List<Document>> GetDocumentsByNumberAsync(string documentNumber)
    {
        return await _connection.Table<Document>()
            .Where(d => d.Number == documentNumber)
            .OrderByDescending(d => d.Id) // Most recent first
            .ToListAsync();
    }

    public async Task<Document?> GetLatestDocumentRevisionAsync(string documentNumber)
    {
        return await _connection.Table<Document>()
            .Where(d => d.Number == documentNumber)
            .OrderByDescending(d => d.Id)
            .FirstOrDefaultAsync();
    }

    public async Task<List<string>> GetDistinctDocumentNumbersAsync()
    {
        var documents = await _connection.Table<Document>()
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
            .Where(d => d.Number.ToLower().Contains(term) ||
                       d.Name.ToLower().Contains(term) ||
                       d.Revision.ToLower().Contains(term))
            .OrderBy(d => d.Number)
            .ThenByDescending(d => d.Id)
            .ToListAsync();
    }

    public async Task<bool> DocumentExistsAsync(string number, string revision)
    {
        var count = await _connection.Table<Document>()
            .CountAsync(d => d.Number == number && d.Revision == revision);

        return count > 0;
    }
}