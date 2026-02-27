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

using duHastNet.PushIt.Interfaces;
using duHastNet.PushIt.Models;
using System.Collections.Generic;
using System.IO;

namespace duHastNet.PushIt.Utilities
{
    /// <summary>
    /// <see cref="IDataSource"/> implementation that reads room data from a
    /// comma-separated value (.csv) file.
    /// <para>
    /// All CSV parsing logic stays inside <see cref="ReadRoomsData"/>; this
    /// class is a thin adapter that bridges the <see cref="IDataSource"/>
    /// interface to that existing static utility.
    /// </para>
    /// <para>
    /// This class reads exclusively from
    /// <see cref="DataSourceSettings.CsvConfig"/> and ignores all other
    /// nested config objects on <see cref="DataSourceSettings"/>.
    /// </para>
    /// </summary>
    public class CsvDataSource : IDataSource
    {
        /// <inheritdoc/>
        public List<RoomDataModel> GetRoomsData(DataSourceSettings settings)
        {
            if (!Validate(settings, out _))
            {
                return null;
            }

            return ReadRoomsData.GetRoomsData(settings.CsvConfig.FilePath);
        }

        /// <inheritdoc/>
        public List<RoomDataProperty> GetHeaderProperties(DataSourceSettings settings)
        {
            if (!Validate(settings, out _))
            {
                return null;
            }

            return ReadRoomsData.GetRoomsDataHeaderRows(settings.CsvConfig.FilePath);
        }

        /// <inheritdoc/>
        /// <remarks>
        /// Checks that <see cref="DataSourceSettings.CsvConfig"/> is present,
        /// that <see cref="CsvDataSourceConfig.FilePath"/> is non-empty, and
        /// that the file exists on disk. Does not open or parse the file.
        /// </remarks>
        public bool Validate(DataSourceSettings settings, out string errorMessage)
        {
            if (settings == null)
            {
                errorMessage = "Data source settings are null.";
                return false;
            }

            if (settings.CsvConfig == null)
            {
                errorMessage = "CSV configuration is missing.";
                return false;
            }

            if (string.IsNullOrWhiteSpace(settings.CsvConfig.FilePath))
            {
                errorMessage = "No CSV file path has been configured.";
                return false;
            }

            if (!File.Exists(settings.CsvConfig.FilePath))
            {
                errorMessage = $"CSV file does not exist at: {settings.CsvConfig.FilePath}";
                return false;
            }

            errorMessage = null;
            return true;
        }
    }
}
