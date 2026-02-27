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

using duHastNet.PushIt.Models;
using System.Collections.Generic;

namespace duHastNet.PushIt.Interfaces
{
    /// <summary>
    /// Abstracts the source from which room data is loaded into PushIt.
    /// Implement this interface to support additional data source types
    /// (e.g. Drofus REST API) without changing RevitDataModel or any commands.
    /// </summary>
    public interface IDataSource
    {
        /// <summary>
        /// Loads all room records from the data source described by <paramref name="settings"/>.
        /// </summary>
        /// <param name="settings">
        /// Provider-specific configuration. Each implementation reads only the
        /// nested config object that is relevant to its source type and ignores
        /// all others.
        /// </param>
        /// <returns>
        /// A list of <see cref="RoomDataModel"/> objects, or <c>null</c> if the
        /// source could not be read (implementations should surface a user-visible
        /// message before returning null).
        /// </returns>
        List<RoomDataModel> GetRoomsData(DataSourceSettings settings);

        /// <summary>
        /// Reads the column-header metadata from the data source without loading
        /// all room records. Used to populate the parameter list shown in the UI.
        /// </summary>
        /// <param name="settings">Provider-specific configuration.</param>
        /// <returns>
        /// A list of <see cref="RoomDataProperty"/> objects describing each column,
        /// or <c>null</c> if the source could not be read.
        /// </returns>
        List<RoomDataProperty> GetHeaderProperties(DataSourceSettings settings);

        /// <summary>
        /// Checks whether the current settings are sufficient for this provider
        /// to load data, without actually reading any data.
        /// </summary>
        /// <param name="settings">Provider-specific configuration.</param>
        /// <param name="errorMessage">
        /// Human-readable description of what is wrong when the method returns
        /// <c>false</c>; <c>null</c> when the method returns <c>true</c>.
        /// </param>
        /// <returns><c>true</c> if the settings are valid; otherwise <c>false</c>.</returns>
        bool Validate(DataSourceSettings settings, out string errorMessage);
    }
}
