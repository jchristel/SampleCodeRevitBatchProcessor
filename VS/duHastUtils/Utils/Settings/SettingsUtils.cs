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

using duHastNet.Utils.Logging;
using Newtonsoft.Json;
using System;
using System.IO;

namespace duHastNet.Utils.Settings
{
    public class SettingsUtils : LogActionsBase
    {

        private string _settingsFilePath = string.Empty;

        /// <summary>
        /// Function loading settings
        /// </summary>
        /// <typeparam name="T"></typeparam>
        /// <returns></returns>
        public T LoadSettings<T>() where T : new()
        {
            try
            {
                // Return a default settings object if the settings file does not exist
                if (!File.Exists(_settingsFilePath))
                {
                    return new T(); // Using generics to instantiate the default settings object
                }

                // Read the settings file
                string jsonString = File.ReadAllText(_settingsFilePath);
                T settings = JsonConvert.DeserializeObject<T>(jsonString);
                return settings;
            }
            catch (Exception ex)
            {
                // Handle exceptions (e.g., file not found, JSON deserialization errors)
                AddMessage($"Error loading settings: {ex.Message}", WPF.Stores.MessageTypes.Error);
                return new T(); // Return a default instance to ensure the function doesn't return null
            }
        }

        /// <summary>
        /// function saving settings as json string
        /// </summary>
        /// <typeparam name="T"></typeparam>
        /// <param name="settings"></param>
        /// <returns></returns>
        public bool SaveSettings<T>(T settings)
        {
            try
            {
                // Ensure the settings directory exists
                string settingsDirectory = Path.GetDirectoryName(_settingsFilePath);
                if (!Directory.Exists(settingsDirectory))
                {
                    try
                    {
                        Directory.CreateDirectory(settingsDirectory);
                    }
                    catch (Exception ex)
                    {
                        AddMessage($"Failed to save settings with exception: {ex.Message}", WPF.Stores.MessageTypes.Error);

                        return false;
                    }
                }

                // Serialize the settings object to JSON
                string jsonString = JsonConvert.SerializeObject(settings, Formatting.None);

                // Write the JSON string to the settings file
                File.WriteAllText(_settingsFilePath, jsonString);

                return true;
            }
            catch (Exception ex)
            {
                AddMessage($"Failed to save settings with exception: {ex.Message}", WPF.Stores.MessageTypes.Error);
                return false;
            }
        }

        //hide the default constructor
        private SettingsUtils()
        {

        }

        /// <summary>
        /// Constructor
        /// </summary>
        /// <param name="settingsFilePath"></param>
        /// <exception cref="ArgumentNullException"></exception>
        public SettingsUtils(string settingsFilePath)
        {
            // settings path cant be empty
            if (string.IsNullOrEmpty(settingsFilePath))
            {
                throw new ArgumentNullException(nameof(settingsFilePath));
            }

            _settingsFilePath = settingsFilePath;
        }
    }
}
