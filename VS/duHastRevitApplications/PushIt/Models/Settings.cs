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
using System.Collections.Generic;

namespace duHastNet.PushIt.Models
{
    public class Settings
    {
        // ── Legacy field ──────────────────────────────────────────────────────────
        // Kept solely for JSON deserialisation compatibility with settings files
        // written before the DataSource refactor. SettingsUtils.LoadSettings()
        // migrates any non-empty DataPath value into DataSource.CsvConfig
        // automatically on first load. Do NOT use DataPath in new code.
        //
        // The JsonProperty name matches the key used by the original PushIt
        // settings file ("rooms_data_file_path") so old files are migrated
        // correctly. NullValueHandling.Ignore ensures the field is omitted from
        // JSON on the first save after migration.
        [JsonProperty(NullValueHandling = NullValueHandling.Ignore)]
        public string? DataPath { get; set; }

        // ── Data source ───────────────────────────────────────────────────────────

        /// <summary>
        /// Configuration for the active data source.
        /// Replaces the legacy <see cref="DataPath"/> string.
        /// Populated on load by <see cref="Utilities.SettingsUtils.LoadSettings"/>,
        /// which migrates old settings files transparently.
        /// </summary>
        public DataSourceSettings DataSource { get; set; }

        // ── Category settings ─────────────────────────────────────────────────────

        // List of enabled Revit category names.
        // These are not all the categories PushIt supports, just the ones enabled.
        public List<string> EnabledCategoryNames { get; set; }

        // ── Column / UI state ─────────────────────────────────────────────────────

        /// <summary>
        /// Column ids (room properties) to be displayed.
        /// The id matches the property name with all spaces removed.
        /// </summary>
        private readonly List<string> _columnIds;

        public List<string> ColumnIds
        {
            get => _columnIds;
        }

        /// <summary>
        /// Serialised state of navigation controls (e.g. DataGrid columns,
        /// filters, sorting). Preserved between sessions.
        /// </summary>
        private Dictionary<string, string> _navigationStates;

        public Dictionary<string, string> NavigationStates
        {
            get => _navigationStates;
            set => _navigationStates = value;
        }

        public Settings()
        {
            EnabledCategoryNames = [];
            _columnIds = [];
            DataPath = string.Empty;
            DataSource = new DataSourceSettings();
            _navigationStates = new Dictionary<string, string>();
        }
    }
}