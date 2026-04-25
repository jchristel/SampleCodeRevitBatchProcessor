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

using Newtonsoft.Json;
using SQLite;

namespace duHastNet.DocManager.Core.Models;

/// <summary>
/// Represents a revision batch or issuance event.
/// Groups documents that were issued together on the same date.
/// </summary>
[Table("Revisions")]
public class Revision
{

    /// <summary>
    /// constants for property names
    /// used in mapping and querying
    /// </summary> 
    public const string PropertyRevisionDate = "RevisionDate";
    public const string PropertyDescription = "RevisionDescription";

    /// <summary>
    /// Unique identifier for each revision batch
    /// </summary>
    [PrimaryKey, AutoIncrement]
    public int Id { get; set; }

    /// <summary>
    /// Date when documents in this batch were issued
    /// </summary>
    [NotNull]
    public DateTime RevisionDate { get; set; }

    /// <summary>
    /// Optional context for this revision (e.g., "For Construction", "For Tender")
    /// </summary>
    public string? Description { get; set; }

    /// <summary>
    /// JSON serialized document IDs for database storage
    /// SQLite doesn't support List<int> directly, so we serialize to JSON
    /// </summary>
    public string DocumentIdsJson { get; set; } = "[]";

    /// <summary>
    /// All the document IDs associated with this revision
    /// 1 to many relationship: one revision can have many documents
    /// This property handles serialization/deserialization to/from JSON for database storage.
    /// </summary>
    [Ignore]
    public List<int> DocumentIds
    {
        get
        {
            try
            {
                if (string.IsNullOrEmpty(DocumentIdsJson))
                    return new List<int>();

                var result = JsonConvert.DeserializeObject<List<int>>(DocumentIdsJson)
                    ?? new List<int>();

                return result;
            }
            catch
            {
                return new List<int>();
            }
        }
        set
        {
            try
            {
                DocumentIdsJson = JsonConvert.SerializeObject(value ?? new List<int>());
            }
            catch
            {
                DocumentIdsJson = "[]";
            }
        }
    }

    /// <summary>
    /// Creates a new revision with the current date
    /// </summary>
    public Revision()
    {
        RevisionDate = DateTime.Now.Date;
        DocumentIds = new List<int>();
    }

    /// <summary>
    /// Creates a new revision with specified date and description
    /// </summary>
    public Revision(DateTime revisionDate, string? description = null)
    {
        RevisionDate = revisionDate.Date; // Ensure we store only the date part
        Description = description;
        DocumentIds = new List<int>();
    }

    public override string ToString()
    {
        var desc = string.IsNullOrEmpty(Description) ? "" : $" - {Description}";
        var docCount = DocumentIds.Count;
        return $"{RevisionDate:yyyy-MM-dd}{desc} ({docCount} documents)";
    }

    /// <summary>
    /// Checks whether this revision conflicts with another (same date and revision description)
    /// </summary>
    /// <param name="other"></param>
    /// <returns></returns>
    public bool Conflicts(Revision other)
    {
        // null check
        if (other == null)
        {
            return false;
        }

        // check whether revision date and description are the same
        if (RevisionDate == other.RevisionDate &&
            string.Equals(Description, other.Description, StringComparison.OrdinalIgnoreCase))
        {
            return true;
        }

        return false;
    }

    /// <summary>
    /// Adds a document ID to this revision
    /// </summary>
    /// <param name="documentId">Document ID to add</param>
    /// <returns>True if the document was added, false if it was already present</returns>
    public bool AddDocument(int documentId)
    {
        var currentIds = DocumentIds;
        if (!currentIds.Contains(documentId))
        {
            currentIds.Add(documentId);
            DocumentIds = currentIds; // Trigger serialization
            return true;
        }
        return false;
    }

    /// <summary>
    /// Removes a document ID from this revision
    /// </summary>
    /// <param name="documentId">Document ID to remove</param>
    /// <returns>True if the document was removed, false if it wasn't present</returns>
    public bool RemoveDocument(int documentId)
    {
        var currentIds = DocumentIds;
        if (currentIds.Remove(documentId))
        {
            DocumentIds = currentIds; // Trigger serialization
            return true;
        }
        return false;
    }

    /// <summary>
    /// Checks if this revision contains a specific document
    /// </summary>
    /// <param name="documentId">Document ID to check</param>
    /// <returns>True if the document is in this revision</returns>
    public bool ContainsDocument(int documentId)
    {
        return DocumentIds.Contains(documentId);
    }

    /// <summary>
    /// Gets the number of documents in this revision
    /// </summary>
    /// <returns>Document count</returns>
    public int DocumentCount => DocumentIds.Count;

    /// <summary>
    /// Adds multiple document IDs to this revision
    /// </summary>
    /// <param name="documentIds">Document IDs to add</param>
    /// <returns>Number of documents actually added (excludes duplicates)</returns>
    public int AddDocuments(IEnumerable<int> documentIds)
    {
        var currentIds = DocumentIds;
        int addedCount = 0;

        foreach (var id in documentIds)
        {
            if (!currentIds.Contains(id))
            {
                currentIds.Add(id);
                addedCount++;
            }
        }

        if (addedCount > 0)
        {
            DocumentIds = currentIds; // Trigger serialization
        }

        return addedCount;
    }

    /// <summary>
    /// Removes multiple document IDs from this revision
    /// </summary>
    /// <param name="documentIds">Document IDs to remove</param>
    /// <returns>Number of documents actually removed</returns>
    public int RemoveDocuments(IEnumerable<int> documentIds)
    {
        var currentIds = DocumentIds;
        int removedCount = 0;

        foreach (var id in documentIds)
        {
            if (currentIds.Remove(id))
            {
                removedCount++;
            }
        }

        if (removedCount > 0)
        {
            DocumentIds = currentIds; // Trigger serialization
        }

        return removedCount;
    }
}