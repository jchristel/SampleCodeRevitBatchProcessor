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
using System.Collections.ObjectModel;


namespace duHastNet.DocManager.Revit.Utilities
{
    public static class SettingsStringParser
    {

        /// <summary>
        /// parse the settings string for PDF export
        /// <paramref name="settingsString"/> is the settings string to parse 
        /// </summary>
        public static ObservableCollection<DocumentSetting> ParseRevitSheetNumberSettingsString(string settingsString, List<string> availableParameters)
        {
            // Create a new ObservableCollection to hold the valid settings
            ObservableCollection<DocumentSetting> settings = [];

            if (string.IsNullOrEmpty(settingsString))
            {
                return settings; // Return an empty collection if the input string is null or empty
            }
            

            List<DocumentSetting> deserializedSettings = JsonConvert.DeserializeObject<List<DocumentSetting>>(settingsString);

            if (deserializedSettings == null)
            {
                return settings; // Return an empty collection if deserialization fails
            }
            else
            {

                // Check if the settings are valid (e.g., if the parameters are available)
                foreach (DocumentSetting setting in deserializedSettings)
                {
                    if (availableParameters.Contains(setting.PropertyName))
                    {
                        settings.Add(setting);
                    }
                }

                //return settings;
                return settings;
            }
        }

        /// <summary>
        /// Convert the settings to a string for PDF export
        /// </summary>
        /// <param name="settings"></param>
        /// <returns></returns>
        public static string ConvertSettingsToRevitSheetNumberString(ObservableCollection<DocumentSetting> settings)
        {
            // Convert the ObservableCollection to a JSON string
            return JsonConvert.SerializeObject(settings, Formatting.None);
        }
    }
}
