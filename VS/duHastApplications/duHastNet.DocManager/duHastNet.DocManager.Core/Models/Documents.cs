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
using SQLite;

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
    /// </summary>
    [NotNull]
    public string Revision { get; set; } = string.Empty;

    /// <summary>
    /// Foreign key to Revisions table
    /// </summary>
    [NotNull]
    [Indexed]
    public int RevisionId { get; set; }

    /// <summary>
    /// Custom properties for this document (stored in CustomProperties table, populated by repository)
    /// </summary>
    [Ignore]
    public List<CustomProperty> CustomProperties { get; set; } = new();

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
        return $"{Number} Rev {Revision} - {Name}";
    }

    /// <summary>
    /// Determines if this document represents a newer revision than another
    /// Note: This is a basic alphanumeric comparison - projects may need custom logic
    /// </summary>
    public bool IsNewerThan(Document other)
    {
        if (other == null || Number != other.Number)
            return false;

        // Simple comparison - may need project-specific logic
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
}