//
//License: BSD License
// Copyright 2025, Jan Christel
//

using SQLite;
using System.Text.Json;

namespace duHastNet.DocManager.Core.Models;

/// <summary>
/// Represents a document version with complete revision history.
/// Each entry tracks a specific revision of a document over time.
/// </summary>
[Table("Documents")]
public class Document
{
    /// <summary>
    /// Unique identifier for each document version
    /// </summary>
    [PrimaryKey, AutoIncrement]
    public int Id { get; set; }

    /// <summary>
    /// Document identifier (alphanumeric)
    /// </summary>
    [NotNull]
    [Indexed]
    public string Number { get; set; } = string.Empty;

    /// <summary>
    /// Full document name
    /// </summary>
    [NotNull]
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Current revision indicator (parsed from document, can be number, character, or both)
    /// For complete revision history, see RevisionIndicatorHistory dictionary
    /// </summary>
    [NotNull]
    public string Revision { get; set; } = string.Empty;

    /// <summary>
    /// Indicates whether a document is active or no longer in use
    /// </summary>
    [NotNull]
    public bool IsActive { get; set; } = true;

    /// <summary>
    /// Foreign key to Revisions table (current revision)
    /// </summary>
    [NotNull]
    [Indexed]
    public int RevisionId { get; set; }

    /// <summary>
    /// JSON serialized document number history for database storage
    /// SQLite doesn't support Dictionary directly, so we serialize to JSON
    /// </summary>
    public string DocumentNumberHistoryJson { get; set; } = "{}";

    /// <summary>
    /// JSON serialized revision indicator history for database storage
    /// Maps RevisionId to the revision indicator for this document in that revision
    /// SQLite doesn't support Dictionary directly, so we serialize to JSON
    /// </summary>
    public string RevisionIndicatorHistoryJson { get; set; } = "{}";

    /// <summary>
    /// Gets or sets a dictionary that tracks the history of document numbers and their associated dates.
    /// This property handles serialization/deserialization to/from JSON for database storage.
    /// </summary>
    [Ignore]
    public Dictionary<string, DateOnly> DocumentNumberHistory
    {
        get
        {
            try
            {
                if (string.IsNullOrEmpty(DocumentNumberHistoryJson))
                    return new Dictionary<string, DateOnly>();

                var stringDict = JsonSerializer.Deserialize<Dictionary<string, string>>(DocumentNumberHistoryJson)
                    ?? new Dictionary<string, string>();

                var result = new Dictionary<string, DateOnly>();
                foreach (var kvp in stringDict)
                {
                    if (DateOnly.TryParse(kvp.Value, out var date))
                    {
                        result[kvp.Key] = date;
                    }
                }
                return result;
            }
            catch
            {
                return new Dictionary<string, DateOnly>();
            }
        }
        set
        {
            try
            {
                var stringDict = value.ToDictionary(kvp => kvp.Key, kvp => kvp.Value.ToString("yyyy-MM-dd"));
                DocumentNumberHistoryJson = JsonSerializer.Serialize(stringDict);
            }
            catch
            {
                DocumentNumberHistoryJson = "{}";
            }
        }
    }

    /// <summary>
    /// Gets or sets a dictionary that tracks the revision indicator for this document across different revisions.
    /// This property handles serialization/deserialization to/from JSON for database storage.
    /// Key: RevisionId, Value: Revision indicator string for this document in that revision
    /// </summary>
    [Ignore]
    public Dictionary<int, string> RevisionIndicatorHistory
    {
        get
        {
            try
            {
                if (string.IsNullOrEmpty(RevisionIndicatorHistoryJson))
                    return new Dictionary<int, string>();

                var result = JsonSerializer.Deserialize<Dictionary<int, string>>(RevisionIndicatorHistoryJson)
                    ?? new Dictionary<int, string>();

                return result;
            }
            catch
            {
                return new Dictionary<int, string>();
            }
        }
        set
        {
            try
            {
                RevisionIndicatorHistoryJson = JsonSerializer.Serialize(value ?? new Dictionary<int, string>());
            }
            catch
            {
                RevisionIndicatorHistoryJson = "{}";
            }
        }
    }

    /// <summary>
    /// Custom properties for this document (stored in CustomProperties table, populated by repository)
    /// </summary>
    [Ignore]
    public List<CustomProperty> CustomProperties { get; set; } = [];

    public Document()
    {
    }

    /// <summary>
    /// Creates a new document with specified details
    /// </summary>
    public Document(string number, string name, string revision, int revisionId)
    {
        Number = number;
        Name = name;
        Revision = revision;
        RevisionId = revisionId;
        IsActive = true;
        DocumentNumberHistory = new Dictionary<string, DateOnly>();
        RevisionIndicatorHistory = new Dictionary<int, string>();

        // Initialize with current revision indicator
        SetRevisionIndicator(revisionId, revision);
    }

    /// <summary>
    /// Gets a custom property value by name
    /// </summary>
    public string? GetCustomProperty(string propertyName)
    {
        return CustomProperties.FirstOrDefault(p =>
            string.Equals(p.PropertyName, propertyName, StringComparison.OrdinalIgnoreCase))?.PropertyValue;
    }

    /// <summary>
    /// Sets a custom property value using CustomFieldDefinitionId
    /// This is the preferred method as it properly uses the ID-based architecture
    /// </summary>
    /// <param name="customFieldDefinitionId">ID of the custom field definition</param>
    /// <param name="propertyName">Property name (for display, stored in [Ignore] field)</param>
    /// <param name="propertyValue">Property value</param>
    public void SetCustomProperty(int customFieldDefinitionId, string propertyName, string propertyValue)
    {
        var existing = CustomProperties.FirstOrDefault(p => p.CustomFieldDefinitionId == customFieldDefinitionId);

        if (existing != null)
        {
            existing.PropertyValue = propertyValue;
            existing.PropertyName = propertyName; // Update display name in case it changed
        }
        else
        {
            CustomProperties.Add(new CustomProperty(Id, customFieldDefinitionId, propertyName, propertyValue));
        }
    }

    public override string ToString()
    {
        var status = IsActive ? "Active" : "Inactive";
        return $"{Number} Rev {Revision} - {Name} ({status})";
    }

    /// <summary>
    /// Determines if this document represents a newer revision than another
    /// </summary>
    public bool IsNewerThan(Document other)
    {
        if (other == null || Number != other.Number)
            return false;

        return string.Compare(Revision, other.Revision, StringComparison.OrdinalIgnoreCase) > 0;
    }

    /// <summary>
    /// Checks if this document has the same number as another (same document, different revision)
    /// </summary>
    public bool IsSameDocumentAs(Document other)
    {
        return other != null &&
               string.Equals(Number, other.Number, StringComparison.OrdinalIgnoreCase);
    }

    /// <summary>
    /// Checks whether this document conflicts with another (same number or same number in document history)
    /// </summary>
    public bool Conflicts(Document other)
    {
        if (other == null)
            return false;

        // Check whether document number is the same
        if (string.Equals(Number, other.Number, StringComparison.OrdinalIgnoreCase))
            return true;

        // Check if other document's number exists in this document's history
        if (DocumentNumberHistory.ContainsKey(other.Number))
            return true;

        // Check if this document's number exists in other document's history
        if (other.DocumentNumberHistory.ContainsKey(Number))
            return true;

        // Check for cross-references in document histories
        foreach (var historyEntry in DocumentNumberHistory.Keys)
        {
            if (string.Equals(historyEntry, other.Number, StringComparison.OrdinalIgnoreCase) ||
                other.DocumentNumberHistory.ContainsKey(historyEntry))
            {
                return true;
            }
        }

        return false;
    }

    #region Document Number History Methods

    /// <summary>
    /// Adds a document number to the history with the current date
    /// </summary>
    public void AddToHistory(string documentNumber)
    {
        AddToHistory(documentNumber, DateOnly.FromDateTime(DateTime.Now));
    }

    /// <summary>
    /// Adds a document number to the history with a specific date
    /// </summary>
    public void AddToHistory(string documentNumber, DateOnly date)
    {
        if (!string.IsNullOrWhiteSpace(documentNumber))
        {
            var history = DocumentNumberHistory;
            history[documentNumber] = date;
            DocumentNumberHistory = history; // Trigger serialization
        }
    }

    /// <summary>
    /// Removes a document number from the history
    /// </summary>
    public bool RemoveFromHistory(string documentNumber)
    {
        var history = DocumentNumberHistory;
        var removed = history.Remove(documentNumber);
        if (removed)
        {
            DocumentNumberHistory = history; // Trigger serialization
        }
        return removed;
    }

    #endregion

    #region Revision Indicator History Methods

    /// <summary>
    /// Sets the revision indicator for a specific revision
    /// </summary>
    /// <param name="revisionId">Revision ID</param>
    /// <param name="indicator">Revision indicator string</param>
    public void SetRevisionIndicator(int revisionId, string indicator)
    {
        if (!string.IsNullOrWhiteSpace(indicator))
        {
            var history = RevisionIndicatorHistory;
            history[revisionId] = indicator;
            RevisionIndicatorHistory = history; // Trigger serialization
        }
    }

    /// <summary>
    /// Gets the revision indicator for a specific revision
    /// </summary>
    /// <param name="revisionId">Revision ID</param>
    /// <returns>Revision indicator string, or null if not found</returns>
    public string? GetRevisionIndicator(int revisionId)
    {
        var history = RevisionIndicatorHistory;
        return history.TryGetValue(revisionId, out var indicator) ? indicator : null;
    }

    /// <summary>
    /// Removes a revision indicator from the history
    /// </summary>
    /// <param name="revisionId">Revision ID to remove</param>
    /// <returns>True if the revision indicator was removed, false if it wasn't present</returns>
    public bool RemoveRevisionIndicator(int revisionId)
    {
        var history = RevisionIndicatorHistory;
        var removed = history.Remove(revisionId);
        if (removed)
        {
            RevisionIndicatorHistory = history; // Trigger serialization
        }
        return removed;
    }

    /// <summary>
    /// Checks if a revision indicator exists for a specific revision
    /// </summary>
    /// <param name="revisionId">Revision ID to check</param>
    /// <returns>True if a revision indicator exists for this revision</returns>
    public bool HasRevisionIndicator(int revisionId)
    {
        return RevisionIndicatorHistory.ContainsKey(revisionId);
    }

    /// <summary>
    /// Gets all revision IDs that have indicators stored
    /// </summary>
    /// <returns>Collection of revision IDs</returns>
    public IEnumerable<int> GetRevisionIdsWithIndicators()
    {
        return RevisionIndicatorHistory.Keys;
    }

    /// <summary>
    /// Clears all revision indicator history
    /// </summary>
    public void ClearRevisionIndicatorHistory()
    {
        RevisionIndicatorHistory = new Dictionary<int, string>();
    }

    #endregion
}