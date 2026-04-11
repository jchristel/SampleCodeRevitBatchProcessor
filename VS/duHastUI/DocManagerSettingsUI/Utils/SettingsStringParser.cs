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

using Newtonsoft.Json;
using System.Collections.ObjectModel;


namespace duHastNet.UI.DocManagerSettingsUI.Utils
{
    public static class SettingsStringParser
    {
        /// <summary>
        /// Parses a bare JSON array settings string into a collection of DocumentSetting objects,
        /// filtering out any entries whose PropertyName is not present in availableParameters.
        /// This is the inner worker method used by both the legacy and dictionary code paths.
        /// </summary>
        /// <param name="settingsString">A bare JSON array string (e.g. "[{...},{...}]").</param>
        /// <param name="availableParameters">The list of parameter names available in the current Revit model.</param>
        /// <returns>A filtered collection of DocumentSetting objects, or an empty collection if the string is null/empty or deserialisation fails.</returns>
        public static ObservableCollection<DocumentSetting> ParseRevitSheetNumberSettingsString(string settingsString, List<string> availableParameters)
        {
            // Create a new ObservableCollection to hold the valid settings
            ObservableCollection<DocumentSetting> settings = [];

            // Check if the input string is null or empty
            if (string.IsNullOrEmpty(settingsString))
            {
                return settings;
            }

            // Deserialize the JSON string into a list of DocumentSetting objects
            List<DocumentSetting> deserializedSettings = JsonConvert.DeserializeObject<List<DocumentSetting>>(settingsString);

            // Check if the deserialization was successful and if there are any settings
            if (deserializedSettings != null && deserializedSettings.Count > 0)
            {
                // Only include settings whose parameter is available in the current model
                foreach (DocumentSetting setting in deserializedSettings)
                {
                    if (availableParameters.Contains(setting.PropertyName))
                    {
                        settings.Add(setting);
                    }
                }
            }

            return settings;
        }

        /// <summary>
        /// Serialises a collection of DocumentSetting objects to a bare JSON array string.
        /// This is the inner worker method used by both the legacy and dictionary code paths.
        /// </summary>
        /// <param name="settings">The collection of DocumentSetting objects to serialise.</param>
        /// <returns>A bare JSON array string.</returns>
        public static string ConvertSettingsToDocumentNumberString(ObservableCollection<DocumentSetting> settings)
        {
            return JsonConvert.SerializeObject(settings, Formatting.None);
        }

        /// <summary>
        /// Parses the DocumentSetting collection for a single property key out of the
        /// DocumentNumberBuilderString dictionary. If the key is absent the result is an
        /// empty collection.
        /// </summary>
        /// <param name="builderDictionaryString">
        /// The full DocumentNumberBuilderString value — a JSON dictionary whose keys are
        /// document property keys (e.g. "DocumentNumber", "DocumentName") and whose values
        /// are bare JSON array strings of DocumentSetting objects.
        /// </param>
        /// <param name="propertyKey">
        /// The document property key to look up (e.g. Constants.DocumentPropertyKeyDocumentNumber).
        /// </param>
        /// <param name="availableParameters">The list of parameter names available in the current context.</param>
        /// <returns>A filtered collection of DocumentSetting objects for the requested key.</returns>
        public static ObservableCollection<DocumentSetting> ParseSettingsForKey(
            string builderDictionaryString,
            string propertyKey,
            List<string> availableParameters)
        {
            if (string.IsNullOrEmpty(builderDictionaryString) || string.IsNullOrEmpty(propertyKey))
            {
                return [];
            }

            // Deserialise the outer dictionary
            Dictionary<string, string> dictionary = JsonConvert.DeserializeObject<Dictionary<string, string>>(builderDictionaryString);

            if (dictionary == null || !dictionary.TryGetValue(propertyKey, out string bareArrayString))
            {
                // Key not present — return empty collection
                return [];
            }

            // Delegate to the inner worker
            return ParseRevitSheetNumberSettingsString(bareArrayString, availableParameters);
        }

        /// <summary>
        /// Serialises an updated DocumentSetting collection for a single property key back into
        /// the DocumentNumberBuilderString dictionary string, leaving all other keys unchanged.
        /// If the dictionary string is null or empty a new dictionary is created containing
        /// only the supplied key.
        /// </summary>
        /// <param name="builderDictionaryString">
        /// The current full DocumentNumberBuilderString value (JSON dictionary), or null/empty
        /// when no settings have been saved yet.
        /// </param>
        /// <param name="propertyKey">
        /// The document property key to update (e.g. Constants.DocumentPropertyKeyDocumentNumber).
        /// </param>
        /// <param name="settings">The updated collection of DocumentSetting objects for this key.</param>
        /// <returns>The updated full DocumentNumberBuilderString value (JSON dictionary).</returns>
        public static string UpdateSettingsForKey(
            string builderDictionaryString,
            string propertyKey,
            ObservableCollection<DocumentSetting> settings)
        {
            // Deserialise the existing dictionary, or start with an empty one
            Dictionary<string, string> dictionary = string.IsNullOrEmpty(builderDictionaryString)
                ? []
                : JsonConvert.DeserializeObject<Dictionary<string, string>>(builderDictionaryString) ?? [];

            // Serialise the collection to a bare array string and store it under the key
            dictionary[propertyKey] = ConvertSettingsToDocumentNumberString(settings);

            // Serialise the whole dictionary back
            return JsonConvert.SerializeObject(dictionary, Formatting.None);
        }
    }
}
