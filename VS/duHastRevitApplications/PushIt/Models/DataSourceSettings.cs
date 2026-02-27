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

using Newtonsoft.Json;

namespace duHastNet.PushIt.Models
{
    /// <summary>
    /// Serialisable configuration for the active data source.
    /// Replaces the legacy <c>DataPath</c> string in <see cref="Settings"/>.
    /// <para>
    /// Only one provider is active at a time. The nested config object for the
    /// active provider is populated; all others are <c>null</c> and are omitted
    /// from the JSON file by <see cref="JsonProperty"/> with
    /// <see cref="NullValueHandling.Ignore"/>.
    /// </para>
    /// <para>
    /// To add a new provider: create a new <c>XxxDataSourceConfig</c> class,
    /// add a property for it here, add a value to <see cref="DataSourceType"/>,
    /// and register it in <see cref="Utilities.DataSourceFactory"/>.
    /// No other changes to the data-loading pipeline are required.
    /// </para>
    /// </summary>
    public class DataSourceSettings
    {
        /// <summary>
        /// The type of data source to use.
        /// Defaults to <see cref="DataSourceType.None"/> so that a fresh install
        /// forces the user to make an explicit selection in the UI.
        /// </summary>
        public DataSourceType SourceType { get; set; } = DataSourceType.None;

        // ── Per-provider config objects ───────────────────────────────────────────
        // Only the config matching the active SourceType will be non-null.
        // NullValueHandling.Ignore ensures unused configs are omitted from JSON.

        /// <summary>
        /// Configuration for <see cref="DataSourceType.Csv"/>.
        /// Null when any other provider is active.
        /// </summary>
        [JsonProperty(NullValueHandling = NullValueHandling.Ignore)]
        public CsvDataSourceConfig CsvConfig { get; set; }

        // Future providers – add a config class and a property here:
        //
        // [JsonProperty(NullValueHandling = NullValueHandling.Ignore)]
        // public DrofusDataSourceConfig DrofusConfig { get; set; }

        /// <summary>
        /// Initialises a new <see cref="DataSourceSettings"/> with safe defaults.
        /// </summary>
        public DataSourceSettings() { }

        /// <summary>
        /// Convenience constructor used by the settings migration path in
        /// <see cref="Utilities.SettingsUtils"/> when upgrading from the
        /// legacy <c>DataPath</c> string format to the nested config structure.
        /// </summary>
        /// <param name="sourceType">The provider type to select.</param>
        /// <param name="filePath">The file path carried over from the old format.</param>
        public DataSourceSettings(DataSourceType sourceType, string filePath)
        {
            SourceType = sourceType;

            if (sourceType == DataSourceType.Csv)
            {
                CsvConfig = new CsvDataSourceConfig
                {
                    FilePath = filePath ?? string.Empty
                };
            }
        }
    }
}
