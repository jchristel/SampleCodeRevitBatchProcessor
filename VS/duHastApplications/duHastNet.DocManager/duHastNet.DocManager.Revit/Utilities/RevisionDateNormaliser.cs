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

using duHastNet.DocManager.Revit.Models.Revit;
using duHastNet.UI.DocManagerSettingsUI.Utils;

namespace duHastNet.DocManager.Revit.Utilities
{
    /// <summary>
    /// Parses raw Revit revision date strings into <see cref="DateTime"/> values and stores the
    /// result in <see cref="RevitData.RevitRevision.ParsedDate"/>.
    /// </summary>
    /// <remarks>
    /// <para>
    /// Revit revision dates are free-text strings with no guaranteed format. This class
    /// interprets them by splitting on any common separator character (<c>/</c>, <c>-</c>,
    /// <c>.</c>, space) and assigning the three resulting components to day, month, and year
    /// according to the supplied <see cref="DateFormatOrder"/>. This approach handles:
    /// </para>
    /// <list type="bullet">
    ///   <item>Single or double digit days and months (e.g. <c>3/4/2026</c> and <c>03/04/2026</c>)</item>
    ///   <item>Two or four digit years (e.g. <c>26</c> interpreted as <c>2026</c> via <see cref="DateTime.TryParse"/>)</item>
    ///   <item>Mixed separator characters (e.g. <c>3.4.26</c>)</item>
    /// </list>
    /// <para>
    /// On success <see cref="RevitData.RevitRevision.ParsedDate"/> is set to the date-only
    /// <see cref="DateTime"/> value (time component midnight). On failure it remains
    /// <c>null</c> and the revision is shown with a grey indicator in the UI.
    /// </para>
    /// </remarks>
    public static class RevisionDateNormaliser
    {
        // All separator characters accepted in Revit date strings.
        private static readonly char[] Separators = { '/', '-', '.', ' ' };

        /// <summary>
        /// Iterates all revisions in the supplied <paramref name="revitDataModel"/> and
        /// attempts to parse each <see cref="RevitData.RevitRevision.RevisionDate"/> string
        /// into a <see cref="DateTime"/>, storing the result in
        /// <see cref="RevitData.RevitRevision.ParsedDate"/>.
        /// </summary>
        /// <param name="revitDataModel">The data model containing revisions to normalise. Must not be null.</param>
        /// <param name="dateFormatOrder">
        /// Controls whether the first date component is treated as the day or the month.
        /// </param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="revitDataModel"/> is null.
        /// </exception>
        public static void NormaliseRevisionDates(
            RevitDataModel revitDataModel,
            DateFormatOrder dateFormatOrder)
        {
            _ = revitDataModel ?? throw new ArgumentNullException(nameof(revitDataModel));

            foreach (var revision in revitDataModel.GetRevisions())
            {
                revision.ParsedDate = TryParseRevitDate(revision.RevisionDate, dateFormatOrder);
            }
        }

        /// <summary>
        /// Attempts to parse a single Revit date string using the supplied format order.
        /// </summary>
        /// <param name="dateString">The raw date string from Revit.</param>
        /// <param name="dateFormatOrder">Whether the first component is the day or the month.</param>
        /// <returns>
        /// The parsed <see cref="DateTime"/> with time set to midnight on success;
        /// <c>null</c> if the string is empty, has fewer than three components, or any
        /// component cannot be parsed as an integer.
        /// </returns>
        internal static DateTime? TryParseRevitDate(string dateString, DateFormatOrder dateFormatOrder)
        {
            if (string.IsNullOrWhiteSpace(dateString))
                return null;

            // Split on any recognised separator.
            var parts = dateString.Split(Separators, StringSplitOptions.RemoveEmptyEntries);

            if (parts.Length < 3)
                return null;

            // Assign components according to the configured order.
            string firstPart  = parts[0].Trim();
            string secondPart = parts[1].Trim();
            string yearPart   = parts[2].Trim();

            string dayPart, monthPart;

            if (dateFormatOrder == DateFormatOrder.DayMonthYear)
            {
                dayPart   = firstPart;
                monthPart = secondPart;
            }
            else
            {
                monthPart = firstPart;
                dayPart   = secondPart;
            }

            if (!int.TryParse(dayPart,   out int day))   return null;
            if (!int.TryParse(monthPart, out int month)) return null;
            if (!int.TryParse(yearPart,  out int year))  return null;

            // Expand two-digit years: 00-99 → 2000-2099.
            // Matches the behaviour callers would expect for modern project dates.
            if (year < 100)
                year += 2000;

            try
            {
                return new DateTime(year, month, day);
            }
            catch (ArgumentOutOfRangeException)
            {
                // day/month/year combination is not a valid calendar date.
                return null;
            }
        }
    }
}
