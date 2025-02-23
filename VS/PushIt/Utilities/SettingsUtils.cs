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
using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace duHast.PushIt.Utilities
{
    public static class SettingsUtils
    {
        private static string settingsDirectory = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "duHast");
        private static string settingsFilePath = Path.Combine(settingsDirectory, "pushIt_settings.json");

        // Load settings from the settings file
        public static Models.Settings LoadSettings()
        {
            try
            {

                // return a default settings object if the settings file does not exist
                if (!File.Exists(settingsFilePath))
                {
                    //initialize settings default
                    Models.Settings settingsDefault = new Models.Settings();
                    settingsDefault.DataPath = string.Empty;
                    settingsDefault.SupportedCategories = new List<string> { "Walls" };
                    return settingsDefault;
                }

                //read the settings file
                string jsonString = File.ReadAllText(settingsFilePath);
                Models.Settings settings = JsonConvert.DeserializeObject<Models.Settings>(jsonString);
                return settings;
            }
            catch (Exception ex)
            {
                // Handle exceptions (e.g., file not found, JSON deserialization errors)
                Console.WriteLine($"Error loading settings: {ex.Message}");
                return null;
            }
        }

        // Save settings to the settings file
        public static void SaveSettings(Models.Settings settings)
        {
            try
            {
                // Ensure the settings directory exists
                if (!Directory.Exists(settingsDirectory))
                {
                    try
                    {
                        Directory.CreateDirectory(settingsDirectory);
                    }
                    catch (Exception ex)
                    {
                        System.Windows.Forms.MessageBox.Show(
                            $"failed to save settings with exception {ex.Message}", 
                            "Exception at save", 
                            System.Windows.Forms.MessageBoxButtons.OK, System.Windows.Forms.MessageBoxIcon.Error);
                        return;
                    }
                }

                // Serialize the settings object to JSON
                string jsonString = JsonConvert.SerializeObject(settings, Formatting.None);

                // Write the JSON string to the settings file
                File.WriteAllText(settingsFilePath, jsonString);
            }
            catch (Exception ex)
            {
                // Handle exceptions (e.g., file write errors)
                System.Windows.Forms.MessageBox.Show(
                            $"failed to save settings with exception {ex.Message}",
                            "Exception at save",
                            System.Windows.Forms.MessageBoxButtons.OK, System.Windows.Forms.MessageBoxIcon.Error);
            }
        }
    }
}
