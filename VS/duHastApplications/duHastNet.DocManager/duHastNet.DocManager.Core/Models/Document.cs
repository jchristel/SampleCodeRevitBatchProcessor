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
    /// Revision indicator (parsed from document, can be number, character, or both)
    /// this is not stored in the revisiona table as revisions group multiple documents which can have different revision indicators
    /// TODO: this should be a dictioanry to support revision history where the key is the revision Id and the value the revision indicator
    /// </summary>
    [NotNull]
    public string Revision { get; set; } = string.Empty;

    /// <summary>
    /// Indicates whether a document is active or no longer in use
    /// </summary>
    [NotNull]
    public bool IsActive { get; set; } = true;

    /// <summary>
    /// Foreign key to Revisions table
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
    /// Sets a custom property value (for in-memory operations, database update requires repository)
    /// </summary>
    public void SetCustomProperty(string propertyName, string propertyValue)
    {
        var existing = CustomProperties.FirstOrDefault(p =>
            string.Equals(p.PropertyName, propertyName, StringComparison.OrdinalIgnoreCase));

        if (existing != null)
        {
            existing.PropertyValue = propertyValue;
        }
        else
        {
            CustomProperties.Add(new CustomProperty(Id, propertyName, propertyValue));
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
}