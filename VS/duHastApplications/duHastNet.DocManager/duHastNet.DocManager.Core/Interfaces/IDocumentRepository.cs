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

namespace duHastNet.DocManager.Core.Interfaces
{
    /// <summary>
    /// Repository interface for Document entities with support for new features
    /// Active documents are returned by default unless specifically requesting inactive/all documents
    /// </summary>
    public interface IDocumentRepository : IRepository<Document>
    {
        // Original methods (now return active documents by default)
        Task<List<Document>> GetDocumentsByRevisionAsync(int revisionId);
        Task<List<Document>> GetDocumentsByNumberAsync(string documentNumber);
        Task<Document?> GetLatestDocumentRevisionAsync(string documentNumber);
        Task<List<string>> GetDistinctDocumentNumbersAsync();
        Task<List<Document>> SearchDocumentsAsync(string searchTerm);
        Task<bool> DocumentExistsAsync(string number, string revision);

        // New methods for IsActive field
        Task<List<Document>> GetActiveDocumentsAsync();
        Task<List<Document>> GetInactiveDocumentsAsync();
        Task<int> UpdateActiveStatusAsync(int documentId, bool isActive);

        // New methods for DocumentNumberHistory
        Task<List<Document>> GetDocumentsByHistoryNumberAsync(string documentNumber);
        Task<bool> DocumentNumberExistsAnywhereAsync(string documentNumber);
        Task<List<string>> GetAllDocumentNumbersEverUsedAsync();

        // New methods for when you specifically need ALL documents (active and inactive)
        Task<List<Document>> GetAllDocumentsByRevisionAsync(int revisionId);
        Task<List<Document>> GetAllDocumentsByNumberAsync(string documentNumber);
        Task<bool> AnyDocumentExistsAsync(string number, string revision);
    }
}
