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
    /// Synchronous repository interface for Document entities.
    /// Active documents are returned by default unless specifically requesting inactive/all documents.
    /// Provides sync methods for IronPython/PyRevit compatibility.
    /// </summary>
    public interface IDocumentRepositorySync : IRepositorySync<Document>
    {
        // Original methods (now return active documents by default)
        List<Document> GetDocumentsByRevision(int revisionId);
        List<Document> GetDocumentsByNumber(string documentNumber);
        Document? GetLatestDocumentRevision(string documentNumber);
        List<string> GetDistinctDocumentNumbers();
        List<Document> SearchDocuments(string searchTerm);
        bool DocumentExists(string number, string revision);

        // New methods for IsActive field
        List<Document> GetActiveDocuments();
        List<Document> GetInactiveDocuments();
        int UpdateActiveStatus(int documentId, bool isActive);

        // New methods for DocumentNumberHistory
        List<Document> GetDocumentsByHistoryNumber(string documentNumber);
        bool DocumentNumberExistsAnywhere(string documentNumber);
        List<string> GetAllDocumentNumbersEverUsed();

        // New methods for when you specifically need ALL documents (active and inactive)
        List<Document> GetAllDocumentsByRevision(int revisionId);
        List<Document> GetAllDocumentsByNumber(string documentNumber);
        bool AnyDocumentExists(string number, string revision);
    }
}
