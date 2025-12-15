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

namespace duHastNet.DocManager.Core.Models.Database;

/// <summary>
/// Represents a custom property for a document.
/// Allows flexible extension of document properties without schema changes.
/// Uses CustomFieldDefinitionId to reference the field definition rather than storing the name directly.
/// </summary>
[Table("CustomProperties")]
public class CustomProperty
{
    /// <summary>
    /// Unique identifier for each custom property
    /// </summary>
    [PrimaryKey, AutoIncrement]
    public int Id { get; set; }

    /// <summary>
    /// Foreign key to Documents table
    /// </summary>
    [NotNull]
    [Indexed]
    public int DocumentId { get; set; }

    /// <summary>
    /// Foreign key to CustomFieldDefinitions table
    /// References which custom field this property belongs to
    /// </summary>
    [NotNull]
    [Indexed]
    public int CustomFieldDefinitionId { get; set; }

    /// <summary>
    /// Value of the custom property (always stored as string)
    /// </summary>
    [NotNull]
    public string PropertyValue { get; set; } = string.Empty;

    /// <summary>
    /// Name of the custom property (e.g., "ProjectPhase", "DisciplineCode")
    /// This is not stored in the database - it's resolved from CustomFieldDefinitions
    /// Used for display and convenience
    /// </summary>
    [Ignore]
    public string PropertyName { get; set; } = string.Empty;

    public CustomProperty()
    {
    }

    /// <summary>
    /// Creates a new custom property with specified values using field definition ID
    /// </summary>
    /// <param name="documentId">Document ID</param>
    /// <param name="customFieldDefinitionId">Custom field definition ID</param>
    /// <param name="propertyValue">Property value</param>
    public CustomProperty(int documentId, int customFieldDefinitionId, string propertyValue)
    {
        DocumentId = documentId;
        CustomFieldDefinitionId = customFieldDefinitionId;
        PropertyValue = propertyValue;
    }

    /// <summary>
    /// Creates a new custom property with specified values including property name for convenience
    /// PropertyName is not stored in database but useful for object initialization
    /// </summary>
    /// <param name="documentId">Document ID</param>
    /// <param name="customFieldDefinitionId">Custom field definition ID</param>
    /// <param name="propertyName">Property name (for display, not stored)</param>
    /// <param name="propertyValue">Property value</param>
    public CustomProperty(int documentId, int customFieldDefinitionId, string propertyName, string propertyValue)
    {
        DocumentId = documentId;
        CustomFieldDefinitionId = customFieldDefinitionId;
        PropertyName = propertyName;
        PropertyValue = propertyValue;
    }

    public override string ToString()
    {
        return $"{PropertyName}: {PropertyValue}";
    }
}