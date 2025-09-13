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
/// Represents a revision batch or issuance event.
/// Groups documents that were issued together on the same date.
/// </summary>
[Table("Revisions")]
public class Revision
{
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
    /// Creates a new revision with the current date
    /// </summary>
    public Revision()
    {
        RevisionDate = DateTime.Now.Date;
    }

    /// <summary>
    /// Creates a new revision with specified date and description
    /// </summary>
    public Revision(DateTime revisionDate, string? description = null)
    {
        RevisionDate = revisionDate.Date; // Ensure we store only the date part
        Description = description;
    }

    public override string ToString()
    {
        var desc = string.IsNullOrEmpty(Description) ? "" : $" - {Description}";
        return $"{RevisionDate:yyyy-MM-dd}{desc}";
    }
}