
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

namespace duHastNet.UI.DocManagerSettingsUI.Utils
{
    public static class SettingsFromRevit
    {
        public static Settings InitialiseSettingsFromRevitJson(string jsonString)
        {
            Settings settings;

            var trimmed = jsonString?.TrimStart() ?? string.Empty;

            if (string.IsNullOrEmpty(trimmed))
            {
                return new Settings();
            }

            // this will take care of both formats:
            // "[" = old format (bare JSON array) — migrated to dictionary with DocumentNumber key only
            // "{" = new format (JSON dictionary keyed by document property key)
            // anything else / empty = return empty Settings
            if (trimmed.StartsWith("["))
            {
                // Old format — bare JSON array of DocumentSetting objects.
                // Wrap it under the DocumentNumber key so it is compatible with the new dictionary format.
                var parts = JsonConvert.DeserializeObject<List<DocumentSetting>>(jsonString) ?? new List<DocumentSetting>();
                string bareArrayString = JsonConvert.SerializeObject(parts);
                string dictionaryString = JsonConvert.SerializeObject(
                    new Dictionary<string, string>
                    {
                        [Constants.DocumentPropertyKeyDocumentNumber] = bareArrayString
                    });
                settings = new Settings
                {
                    DocumentNumberBuilderString = dictionaryString,
                    DatabasePath = string.Empty
                };
            }
            else
            {
                // New format - Settings object
                // DocumentNumberBuilderString is populated from JSON if present;
                // defaults to string.Empty for files written before this property existed.
                settings = JsonConvert.DeserializeObject<Settings>(jsonString) ?? new Settings();
            }

            return settings;
        }
    }
}
