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

using System.Collections.Generic;

namespace duHastNet.PushIt.Models
{
    /// <summary>
    /// Holds the list of shared parameters that are bound in the active Revit
    /// document and available for use in data source mappings or validation.
    /// <para>
    /// Populated once at startup by <c>Main.LoadSharedParametersFromDocument</c>
    /// and kept stable for the lifetime of the session. It is intentionally
    /// separate from <see cref="ParameterDataModelContainer"/>, which carries
    /// the column-header metadata read from a specific data source (CSV, drofus).
    /// </para>
    /// </summary>
    public class AvailableParameterContainer
    {
        private List<AvailableParameter> _parameters;

        // ── Constructor ───────────────────────────────────────────────────────

        public AvailableParameterContainer()
        {
            _parameters = [];
        }

        // ── Mutation ──────────────────────────────────────────────────────────

        /// <summary>
        /// Adds a parameter to the container.
        /// </summary>
        /// <remarks>
        /// Duplicate GUID entries are silently skipped — a parameter already
        /// registered under the same GUID does not need to be registered twice.
        /// Duplicate name entries with a different GUID are also silently skipped
        /// since the GUID is the authoritative identity.
        /// </remarks>
        /// <param name="parameter">
        /// The parameter to add. Must not be <c>null</c>.
        /// </param>
        /// <exception cref="System.ArgumentNullException">
        /// Thrown when <paramref name="parameter"/> is <c>null</c>.
        /// </exception>
        public void AddParameter(AvailableParameter parameter)
        {
            if (parameter == null)
                throw new System.ArgumentNullException(nameof(parameter));

            // Guard against duplicates by GUID — GUIDs are the authoritative key.
            foreach (var existing in _parameters)
            {
                if (string.Equals(
                        existing.ParameterGuid,
                        parameter.ParameterGuid,
                        System.StringComparison.OrdinalIgnoreCase))
                {
                    return;
                }
            }

            _parameters.Add(parameter);
        }

        /// <summary>
        /// Removes all entries from the container.
        /// </summary>
        public void Clear()
        {
            _parameters = [];
        }

        // ── Query ─────────────────────────────────────────────────────────────

        /// <summary>
        /// Returns a read-only snapshot of all available parameters.
        /// </summary>
        public IReadOnlyList<AvailableParameter> GetAll()
        {
            return _parameters.AsReadOnly();
        }

        /// <summary>
        /// Returns <c>true</c> when a parameter with the supplied GUID exists in
        /// the container.
        /// </summary>
        /// <param name="guid">The GUID string to look up (case-insensitive).</param>
        public bool ContainsGuid(string guid)
        {
            if (string.IsNullOrWhiteSpace(guid))
                return false;

            foreach (var p in _parameters)
            {
                if (string.Equals(p.ParameterGuid, guid, System.StringComparison.OrdinalIgnoreCase))
                    return true;
            }

            return false;
        }

        /// <summary>
        /// Returns <c>true</c> when a parameter with the supplied display name
        /// exists in the container (case-insensitive).
        /// </summary>
        /// <param name="name">The display name to look up.</param>
        public bool ContainsName(string name)
        {
            if (string.IsNullOrWhiteSpace(name))
                return false;

            foreach (var p in _parameters)
            {
                if (string.Equals(p.ParameterName, name, System.StringComparison.OrdinalIgnoreCase))
                    return true;
            }

            return false;
        }
    }
}
