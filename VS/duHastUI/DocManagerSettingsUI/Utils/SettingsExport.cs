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

namespace duHastNet.UI.DocManagerSettingsUI.Utils
{
    public static class SettingsExport
    {
        /// <summary>
        /// Exports the full settings to a JSON file. The builder dictionary string (which contains
        /// the builder rules for all property keys) is stored as-is in the Settings object and
        /// serialised to the file.
        /// </summary>
        /// <param name="filePath">The full file path to write the exported JSON to.</param>
        /// <param name="builderDictionaryString">
        /// The full DocumentNumberBuilderString value — a JSON dictionary keyed by document
        /// property keys (e.g. "DocumentNumber", "DocumentName") whose values are bare JSON
        /// array strings of DocumentSetting objects.
        /// </param>
        /// <param name="AddMessage">Callback for surfacing status or error messages to the UI.</param>
        public static void ExportSettingsToJson(
            string filePath,
            string builderDictionaryString,
            Action<string, duHastNet.Utils.WPF.Stores.MessageTypes> AddMessage)
        {
            try
            {
                // Create a Settings object carrying the full builder dictionary string
                Settings settingsObject = new Settings(builderDictionaryString, string.Empty);

                // Serialize the Settings object to JSON
                string json = Newtonsoft.Json.JsonConvert.SerializeObject(settingsObject, Newtonsoft.Json.Formatting.Indented);

                // Write to file
                System.IO.File.WriteAllText(filePath, json);

                AddMessage($"Settings exported to {filePath}", duHastNet.Utils.WPF.Stores.MessageTypes.Information);
            }
            catch (Exception ex)
            {
                AddMessage($"Error exporting settings: {ex.Message}", duHastNet.Utils.WPF.Stores.MessageTypes.Error);
            }
        }
    }
}
