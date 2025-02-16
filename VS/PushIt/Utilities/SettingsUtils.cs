using Newtonsoft.Json;
using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PushIt.Utilities
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
