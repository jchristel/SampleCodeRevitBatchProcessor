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
/// Represents a custom field definition.
/// Defines the available custom property fields that can be used across all documents.
/// </summary>
[Table("CustomFieldDefinitions")]
public class CustomFieldDefinition
{
    /// <summary>
    /// Unique identifier for each custom field definition
    /// </summary>
    [PrimaryKey, AutoIncrement]
    public int Id { get; set; }

    /// <summary>
    /// Name of the custom field (e.g., "ProjectPhase", "DisciplineCode")
    /// Must be unique across all definitions
    /// </summary>
    [NotNull]
    [Unique]
    public string PropertyName { get; set; } = string.Empty;

    /// <summary>
    /// Indicates whether this custom field is active or deactivated
    /// Inactive fields are not shown in UI but data is preserved
    /// </summary>
    [NotNull]
    public bool IsActive { get; set; } = true;

    public CustomFieldDefinition()
    {
    }

    /// <summary>
    /// Creates a new custom field definition with specified values
    /// </summary>
    public CustomFieldDefinition(string propertyName, bool isActive = true)
    {
        PropertyName = propertyName;
        IsActive = isActive;
    }

    public override string ToString()
    {
        return $"{PropertyName} ({(IsActive ? "Active" : "Inactive")})";
    }

    /// <summary>
    /// Checks whether this custom field conflicts with another (same name)
    /// </summary>
    /// <param name="other"></param>
    /// <returns></returns>
    public bool Conflicts(CustomFieldDefinition other)
    {
        // null check
        if (other == null)
        {
            return false;
        }

        // check whether customd fiel names are identical
        if (PropertyName == other.PropertyName)
        {
            return true;
        }

        return false;
    }
}