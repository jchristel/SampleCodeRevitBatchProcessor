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

using Newtonsoft.Json.Linq;


namespace duHastNet.UI.DocManagerSettingsUI.Utils
{
    public static class SettingsImport
    {
        public static Dictionary<string, string> ImportSettingsFromJson(
            string filePath,
            Action<string, duHastNet.Utils.WPF.Stores.MessageTypes> AddMessage
            )
        {

            Dictionary<string, string> settings = [];

            try
            {
                // Read the JSON file
                string json = System.IO.File.ReadAllText(filePath);

                // i only need a dictionary created from the json file
                // Parse the JSON into a JObject
                var jsonObject = JObject.Parse(json);

                // Iterate through the first-level properties
                foreach (var property in jsonObject.Properties())
                {
                    // Use the property name as the key
                    string key = property.Name;

                    // Deserialize the value into a collection of DocumentSetting
                    var value = property.Value.ToString();

                    // Add the key-value pair to the dictionary
                    settings[key] = value;
                }

                AddMessage($"Settings imported from {filePath}", duHastNet.Utils.WPF.Stores.MessageTypes.Information);
            }
            catch (Exception ex)
            {
                AddMessage($"Error importing settings: {ex.Message}", duHastNet.Utils.WPF.Stores.MessageTypes.Error);
                settings = null;
            }

            return settings;
        }
    }
}
