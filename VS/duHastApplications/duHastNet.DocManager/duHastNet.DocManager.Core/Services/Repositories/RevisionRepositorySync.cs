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
/// Synchronous repository implementation for Revision entities.
/// Provides sync methods for IronPython/PyRevit compatibility.
/// </summary>
public class RevisionRepositorySync : BaseRepositorySync<Revision>, IRevisionRepositorySync
{
    public RevisionRepositorySync(SQLiteConnection connection) : base(connection)
    {
    }

    #region existing methods

    public List<Revision> GetRevisionsByDateRange(DateTime startDate, DateTime endDate)
    {
        return _connection.Table<Revision>()
            .Where(r => r.RevisionDate >= startDate && r.RevisionDate <= endDate)
            .OrderByDescending(r => r.RevisionDate)
            .ToList();
    }

    public Revision? GetLatestRevision()
    {
        return _connection.Table<Revision>()
            .OrderByDescending(r => r.RevisionDate)
            .ThenByDescending(r => r.Id)
            .FirstOrDefault();
    }

    public List<Revision> GetRevisionsByDate(DateTime date)
    {
        var startOfDay = date.Date;
        var endOfDay = startOfDay.AddDays(1).AddTicks(-1);
        return _connection.Table<Revision>()
            .Where(r => r.RevisionDate >= startOfDay && r.RevisionDate <= endOfDay)
            .OrderBy(r => r.Id)
            .ToList();
    }

    #endregion

    #region document management methods

    /// <summary>
    /// Adds a document to a revision's document list (sync version)
    /// </summary>
    /// <param name="revisionId">Revision to update</param>
    /// <param name="documentId">Document ID to add</param>
    /// <returns>Number of records affected</returns>
    public int AddDocumentToRevision(int revisionId, int documentId)
    {
        var count = 0;
        _connection.RunInTransaction(() =>
        {
            var revision = _connection.Find<Revision>(revisionId);
            if (revision == null) return;

            if (!revision.DocumentIds.Contains(documentId))
            {
                var currentIds = revision.DocumentIds;
                currentIds.Add(documentId);
                revision.DocumentIds = currentIds;
                count = _connection.Update(revision);
            }
        });
        return count;
    }

    /// <summary>
    /// Removes a document from a revision's document list (sync version)
    /// </summary>
    /// <param name="revisionId">Revision to update</param>
    /// <param name="documentId">Document ID to remove</param>
    /// <returns>Number of records affected</returns>
    public int RemoveDocumentFromRevision(int revisionId, int documentId)
    {
        var count = 0;
        _connection.RunInTransaction(() =>
        {
            var revision = _connection.Find<Revision>(revisionId);
            if (revision == null) return;

            var currentIds = revision.DocumentIds;
            if (currentIds.Remove(documentId))
            {
                revision.DocumentIds = currentIds;
                count = _connection.Update(revision);
            }
        });
        return count;
    }

    /// <summary>
    /// Adds multiple documents to a revision (sync version)
    /// </summary>
    /// <param name="revisionId">Revision to update</param>
    /// <param name="documentIds">Document IDs to add</param>
    /// <returns>Number of records affected</returns>
    public int AddDocumentsToRevision(int revisionId, IEnumerable<int> documentIds)
    {
        var idList = documentIds.ToList();
        var count = 0;
        _connection.RunInTransaction(() =>
        {
            var revision = _connection.Find<Revision>(revisionId);
            if (revision == null) return;

            var currentIds = revision.DocumentIds;
            bool changed = false;
            foreach (var documentId in idList)
            {
                if (!currentIds.Contains(documentId))
                {
                    currentIds.Add(documentId);
                    changed = true;
                }
            }

            if (changed)
            {
                revision.DocumentIds = currentIds;
                count = _connection.Update(revision);
            }
        });
        return count;
    }

    /// <summary>
    /// Removes multiple documents from a revision (sync version)
    /// </summary>
    /// <param name="revisionId">Revision to update</param>
    /// <param name="documentIds">Document IDs to remove</param>
    /// <returns>Number of records affected</returns>
    public int RemoveDocumentsFromRevision(int revisionId, IEnumerable<int> documentIds)
    {
        var idList = documentIds.ToList();
        var count = 0;
        _connection.RunInTransaction(() =>
        {
            var revision = _connection.Find<Revision>(revisionId);
            if (revision == null) return;

            var currentIds = revision.DocumentIds;
            bool changed = false;
            foreach (var documentId in idList)
            {
                if (currentIds.Remove(documentId))
                {
                    changed = true;
                }
            }

            if (changed)
            {
                revision.DocumentIds = currentIds;
                count = _connection.Update(revision);
            }
        });
        return count;
    }

    /// <summary>
    /// Replaces all documents in a revision with a new list (sync version)
    /// </summary>
    /// <param name="revisionId">Revision to update</param>
    /// <param name="documentIds">New list of document IDs</param>
    /// <returns>Number of records affected</returns>
    public int SetRevisionDocuments(int revisionId, IEnumerable<int> documentIds)
    {
        var idList = documentIds.Distinct().ToList();
        var count = 0;
        _connection.RunInTransaction(() =>
        {
            var revision = _connection.Find<Revision>(revisionId);
            if (revision == null) return;

            revision.DocumentIds = idList;
            count = _connection.Update(revision);
        });
        return count;
    }

    /// <summary>
    /// Gets all revisions that contain a specific document (sync version)
    /// This builds the document's revision history
    /// </summary>
    /// <param name="documentId">Document ID to search for</param>
    /// <returns>List of revisions containing this document</returns>
    public List<Revision> GetRevisionsByDocumentId(int documentId)
    {
        // DocumentIdsJson stores integers without quotes e.g. [100,101,102].
        // A reliable broad LIKE pre-filter is to search for the raw number surrounded
        // by any JSON delimiter (bracket, comma, or space). We then apply the accurate
        // in-memory check on the deserialized list to guarantee correctness.
        var searchTerm = documentId.ToString();
        var revisions = _connection.Table<Revision>()
            .Where(r => r.DocumentIdsJson.Contains(searchTerm))
            .OrderByDescending(r => r.RevisionDate)
            .ToList();

        // In-memory filter eliminates any false positives from the LIKE pre-filter
        // (e.g. documentId=1 matching against [10,11,12])
        return revisions.Where(r => r.DocumentIds.Contains(documentId)).ToList();
    }

    /// <summary>
    /// Gets the count of documents in a revision (sync version)
    /// </summary>
    /// <param name="revisionId">Revision ID</param>
    /// <returns>Number of documents in this revision</returns>
    public int GetDocumentCount(int revisionId)
    {
        var revision = GetById(revisionId);
        return revision?.DocumentIds.Count ?? 0;
    }

    /// <summary>
    /// Checks if a revision contains a specific document (sync version)
    /// </summary>
    /// <param name="revisionId">Revision ID</param>
    /// <param name="documentId">Document ID to check</param>
    /// <returns>True if the revision contains the document</returns>
    public bool RevisionContainsDocument(int revisionId, int documentId)
    {
        var revision = GetById(revisionId);
        return revision?.DocumentIds.Contains(documentId) ?? false;
    }

    /// <summary>
    /// Gets all revisions that are empty (contain no documents) (sync version)
    /// </summary>
    /// <returns>List of empty revisions</returns>
    public List<Revision> GetEmptyRevisions()
    {
        var allRevisions = GetAll();
        return allRevisions.Where(r => r.DocumentIds.Count == 0).ToList();
    }

    /// <summary>
    /// Gets revision statistics (sync version)
    /// </summary>
    /// <returns>Dictionary with revision statistics</returns>
    public Dictionary<string, int> GetRevisionStatistics()
    {
        var allRevisions = GetAll();

        return new Dictionary<string, int>
        {
            ["TotalRevisions"] = allRevisions.Count,
            ["EmptyRevisions"] = allRevisions.Count(r => r.DocumentIds.Count == 0),
            ["RevisionsWithDocuments"] = allRevisions.Count(r => r.DocumentIds.Count > 0),
            ["TotalDocumentReferences"] = allRevisions.Sum(r => r.DocumentIds.Count),
            ["MaxDocumentsInRevision"] = allRevisions.Any() ? allRevisions.Max(r => r.DocumentIds.Count) : 0,
            ["MinDocumentsInRevision"] = allRevisions.Any() ? allRevisions.Min(r => r.DocumentIds.Count) : 0
        };
    }

    #endregion
}
