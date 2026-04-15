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
    /// Represents a Revit revision with a raw date string and description.
    /// </summary>
    /// <remarks>
    /// <para>
    /// Revit stores revision dates as free-text strings in whatever format the user entered them.
    /// The string is not guaranteed to be parseable or to follow a consistent locale format.
    /// </para>
    /// <para>
    /// <see cref="ParsedDate"/> is populated by
    /// <see cref="Utilities.RevisionDateNormaliser.NormaliseRevisionDates"/> in <c>Main.cs</c>
    /// immediately after document numbers are built. Once set it is a locale-independent
    /// <see cref="DateTime"/> value suitable for direct comparison against
    /// <see cref="global::duHastNet.DocManager.Core.Models.Revision.RevisionDate"/>.
    /// </para>
    /// <para>
    /// Use <see cref="IsDateValid"/> to check whether parsing succeeded and
    /// <see cref="TryGetDate"/> to obtain the parsed value via an out parameter.
    /// Revisions where <see cref="IsDateValid"/> is <c>false</c> must not be imported into
    /// the database and are shown with a grey indicator in the UI.
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
        /// Kept for display purposes only. Use <see cref="ParsedDate"/> for all date comparisons.
        /// </summary>
        public string RevisionDate { get; set; }

        /// <summary>
        /// Gets or sets the revision description.
        /// </summary>
        public string RevisionDescription { get; set; }

        /// <summary>
        /// Gets or sets the parsed date value produced by
        /// <see cref="Utilities.RevisionDateNormaliser.NormaliseRevisionDates"/>.
        /// <c>null</c> when <see cref="RevisionDate"/> could not be parsed.
        /// The time component is always midnight — only the date portion is meaningful.
        /// </summary>
        public DateTime? ParsedDate { get; set; }

        /// <summary>
        /// Gets whether <see cref="ParsedDate"/> has been successfully populated.
        /// <c>false</c> when the raw <see cref="RevisionDate"/> string could not be parsed,
        /// or before <see cref="Utilities.RevisionDateNormaliser.NormaliseRevisionDates"/>
        /// has been called.
        /// </summary>
        public bool IsDateValid => ParsedDate.HasValue;

        #endregion Properties

        #region Constructors

        /// <summary>
        /// Initializes a new instance of <see cref="RevitRevision"/> with the supplied values.
        /// <see cref="ParsedDate"/> is <c>null</c> until
        /// <see cref="Utilities.RevisionDateNormaliser.NormaliseRevisionDates"/> is called.
        /// </summary>
        /// <param name="revitRevisionElementId">The Revit element ID of the revision.</param>
        /// <param name="revisionDate">
        /// The date string as supplied by Revit. May be in any locale format.
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
        /// <see cref="IsDateValid"/> returns <c>false</c> for instances created via this constructor.
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
        /// Attempts to retrieve the parsed date value.
        /// </summary>
        /// <param name="date">
        /// When this method returns <c>true</c>, contains the parsed date with time set to midnight.
        /// When <c>false</c>, contains <see cref="DateTime.MinValue"/>.
        /// </param>
        /// <returns>
        /// <c>true</c> if <see cref="ParsedDate"/> has a value; otherwise <c>false</c>.
        /// </returns>
        public bool TryGetDate(out DateTime date)
        {
            if (ParsedDate.HasValue)
            {
                date = ParsedDate.Value;
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
                ? ParsedDate!.Value.ToString("yyyy-MM-dd")
                : $"{RevisionDate} [INVALID DATE]";

            return $"Revision Element Id: {RevitRevisionElementId}, Revision Date: {dateInfo}, Revision Description: {RevisionDescription}";
        }

        #endregion Public Methods
    }
}
