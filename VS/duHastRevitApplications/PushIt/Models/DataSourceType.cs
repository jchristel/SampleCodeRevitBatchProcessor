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
    /// Identifies the type of data source used to load room data into PushIt.
    /// The selected value drives both the <see cref="Interfaces.IDataSource"/>
    /// implementation chosen by <see cref="Utilities.DataSourceFactory"/> and
    /// the configuration control shown in the UI.
    /// </summary>
    public enum DataSourceType
    {
        /// <summary>
        /// No data source has been selected.
        /// The application cannot load room data in this state.
        /// </summary>
        None,

        /// <summary>
        /// Room data is loaded from a comma-separated value (.csv) file.
        /// Requires <see cref="DataSourceSettings.CsvConfig"/> to be populated.
        /// </summary>
        Csv

        // Future providers – add entries here and register them in
        // DataSourceFactory and DataSourceViewModel without changing anything else:
        //
        // Drofus,
    }
}
