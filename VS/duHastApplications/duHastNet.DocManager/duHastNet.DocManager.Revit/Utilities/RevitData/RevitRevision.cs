//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2026, Jan Christel
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

namespace duHastNet.DocManager.Revit.Utilities.RevitData
{
    /// <summary>
    /// Represents a Revit revision with a date string and description.
    /// </summary>
    /// <remarks>
    /// <para>
    /// Revit stores revision dates as free-text strings in whatever format the user entered them.
    /// The string is not guaranteed to be parseable as a date value, and even when parseable it
    /// may be in a locale-specific format such as "12/01/2026" or "10/04/26".
    /// </para>
    /// <para>
    /// Use <see cref="IsDateValid"/> to check parseability and <see cref="TryGetDate"/> to obtain
    /// a parsed <see cref="DateTime"/> value. All date-matching logic must go through
    /// <see cref="TryGetDate"/> so that locale-format differences between the Revit string and
    /// the database <see cref="global::duHastNet.DocManager.Core.Models.Revision.RevisionDate"/>
    /// DateTime are handled correctly in one place.
    /// </para>
    /// <para>
    /// Revisions where <see cref="IsDateValid"/> is <c>false</c> must not be imported into the
    /// database and are shown with a grey indicator in the UI.
    /// </para>
    /// </remarks>
    public class RevitRevision
    {
        #region Properties

        /// <summary>
        /// Gets or sets the Revit element ID of this revision.
        /// </summary>
        public Int64 RevitRevisionElementId { get; set; }

        /// <summary>
        /// Gets or sets the revision date as a raw string sourced directly from Revit.
        /// This value is not guaranteed to be in a specific format — see <see cref="IsDateValid"/>
        /// and <see cref="TryGetDate"/>.
        /// </summary>
        public string RevisionDate { get; set; }

        /// <summary>
        /// Gets or sets the revision description.
        /// </summary>
        public string RevisionDescription { get; set; }

        /// <summary>
        /// Gets whether <see cref="RevisionDate"/> can be parsed as a valid <see cref="DateTime"/>.
        /// Delegates to <see cref="TryGetDate"/> so parsing logic exists in one place.
        /// </summary>
        public bool IsDateValid => TryGetDate(out _);

        #endregion Properties

        #region Constructors

        /// <summary>
        /// Initializes a new instance of <see cref="RevitRevision"/> with the supplied values.
        /// </summary>
        /// <param name="revitRevisionElementId">The Revit element ID of the revision.</param>
        /// <param name="revisionDate">
        /// The date string as supplied by Revit. May be in any locale format.
        /// Use <see cref="IsDateValid"/> and <see cref="TryGetDate"/> before performing
        /// any date operations.
        /// </param>
        /// <param name="revisionDescription">The revision description. Must not be null.</param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="revisionDate"/> or <paramref name="revisionDescription"/>
        /// is null.
        /// </exception>
        public RevitRevision(Int64 revitRevisionElementId, string revisionDate, string revisionDescription)
        {
            RevitRevisionElementId = revitRevisionElementId;
            RevisionDate = revisionDate ?? throw new ArgumentNullException(nameof(revisionDate));
            RevisionDescription = revisionDescription ?? throw new ArgumentNullException(nameof(revisionDescription));
        }

        /// <summary>
        /// Initializes a new default instance of <see cref="RevitRevision"/> with zeroed/empty values.
        /// <see cref="IsDateValid"/> will return <c>false</c> for instances created via this constructor.
        /// </summary>
        public RevitRevision()
        {
            RevitRevisionElementId = 0;
            RevisionDate = string.Empty;
            RevisionDescription = string.Empty;
        }

        #endregion Constructors

        #region Public Methods

        /// <summary>
        /// Attempts to parse <see cref="RevisionDate"/> into a <see cref="DateTime"/>.
        /// </summary>
        /// <param name="date">
        /// When this method returns <c>true</c>, contains the date portion of the parsed value
        /// with the time component set to midnight. When <c>false</c>, contains
        /// <see cref="DateTime.MinValue"/>.
        /// </param>
        /// <returns>
        /// <c>true</c> if <see cref="RevisionDate"/> is non-empty and parseable by
        /// <see cref="DateTime.TryParse(string, out DateTime)"/>; otherwise <c>false</c>.
        /// </returns>
        /// <remarks>
        /// All callers that need to match a Revit revision date against a database
        /// <see cref="global::duHastNet.DocManager.Core.Models.Revision.RevisionDate"/> must use
        /// this method to obtain a <see cref="DateTime"/> and compare date portions directly,
        /// rather than comparing formatted strings, to avoid locale-format mismatches such as
        /// "12/01/2026" vs "2026-01-12".
        /// </remarks>
        public bool TryGetDate(out DateTime date)
        {
            if (string.IsNullOrWhiteSpace(RevisionDate))
            {
                date = DateTime.MinValue;
                return false;
            }

            if (DateTime.TryParse(RevisionDate, out DateTime parsed))
            {
                date = parsed.Date;
                return true;
            }

            date = DateTime.MinValue;
            return false;
        }

        /// <summary>
        /// Determines whether this revision conflicts with another, based on element ID.
        /// There cannot be two revisions with the same element ID in a Revit model.
        /// </summary>
        /// <param name="other">The other revision to compare against.</param>
        /// <returns><c>true</c> if the element IDs are equal; otherwise <c>false</c>.</returns>
        public bool Conflicts(RevitRevision other)
        {
            return RevitRevisionElementId == other.RevitRevisionElementId;
        }

        /// <summary>
        /// Returns a string representation of this revision.
        /// Appends an invalid-date warning when <see cref="IsDateValid"/> is <c>false</c>.
        /// </summary>
        public override string ToString()
        {
            string dateInfo = IsDateValid
                ? RevisionDate
                : $"{RevisionDate} [INVALID DATE]";

            return $"Revision Element Id: {RevitRevisionElementId}, Revision Date: {dateInfo}, Revision Description: {RevisionDescription}";
        }

        #endregion Public Methods
    }
}