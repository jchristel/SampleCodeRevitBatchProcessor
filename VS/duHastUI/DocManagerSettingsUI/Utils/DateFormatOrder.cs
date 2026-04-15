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

namespace duHastNet.UI.DocManagerSettingsUI.Utils
{
    /// <summary>
    /// Specifies the order of day and month components in revision date strings sourced from Revit.
    /// </summary>
    /// <remarks>
    /// Revit stores revision dates as free-text strings entered by the user. The separator
    /// character and zero-padding of day/month digits are handled automatically by the parser —
    /// this enum only controls whether the first numeric component is the day or the month,
    /// which is the only genuine ambiguity in strings such as "03/04/2026".
    /// <para>
    /// Stored in the Revit project settings JSON under the key
    /// <c>"DateFormatOrder"</c> as the string <c>"DayMonthYear"</c> or
    /// <c>"MonthDayYear"</c>. Defaults to <see cref="DayMonthYear"/> when the key is
    /// absent or unrecognised.
    /// </para>
    /// </remarks>
    public enum DateFormatOrder
    {
        /// <summary>
        /// The first component is the day, the second is the month.
        /// Example: "03/04/2026" is interpreted as 3 April 2026.
        /// This is the default and covers most non-US locales.
        /// </summary>
        DayMonthYear,

        /// <summary>
        /// The first component is the month, the second is the day.
        /// Example: "03/04/2026" is interpreted as 4 March 2026.
        /// </summary>
        MonthDayYear
    }
}
