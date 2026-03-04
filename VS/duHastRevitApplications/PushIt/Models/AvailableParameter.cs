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

namespace duHastNet.PushIt.Models
{
    /// <summary>
    /// Represents a single shared parameter that is bound in the active Revit
    /// document and available for use in data source mappings.
    /// <para>
    /// This is intentionally lightweight — it carries only the two fields needed
    /// to identify a parameter for matching purposes. It is distinct from
    /// <see cref="RoomDataProperty"/>, which is a runtime data-carrying object
    /// used inside loaded room records.
    /// </para>
    /// </summary>
    public class AvailableParameter
    {
        /// <summary>
        /// The human-readable display name of the shared parameter, as shown in
        /// Revit's Shared Parameters dialog and in the mapping UI.
        /// </summary>
        public string ParameterName { get; }

        /// <summary>
        /// The GUID that uniquely identifies this shared parameter definition.
        /// Used to look up the parameter in the Revit document regardless of any
        /// display-name changes.
        /// </summary>
        public string ParameterGuid { get; }

        /// <summary>
        /// Constructs an <see cref="AvailableParameter"/>.
        /// </summary>
        /// <param name="parameterName">
        /// The display name of the parameter. Must not be null or whitespace.
        /// </param>
        /// <param name="parameterGuid">
        /// The GUID string of the shared parameter. Must not be null or whitespace.
        /// </param>
        /// <exception cref="System.ArgumentException">
        /// Thrown when either argument is null or whitespace.
        /// </exception>
        public AvailableParameter(string parameterName, string parameterGuid)
        {
            if (string.IsNullOrWhiteSpace(parameterName))
                throw new System.ArgumentException(
                    "Parameter name must not be null or whitespace.", nameof(parameterName));

            if (string.IsNullOrWhiteSpace(parameterGuid))
                throw new System.ArgumentException(
                    "Parameter GUID must not be null or whitespace.", nameof(parameterGuid));

            ParameterName = parameterName;
            ParameterGuid = parameterGuid;
        }

        /// <summary>
        /// Returns a string in the form <c>Name (GUID)</c> for diagnostics and
        /// log messages.
        /// </summary>
        public override string ToString() => $"{ParameterName} ({ParameterGuid})";
    }
}
