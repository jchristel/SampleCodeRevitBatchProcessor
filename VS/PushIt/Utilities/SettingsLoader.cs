using Newtonsoft.Json;
using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PushIt.Utilities
{
    public static class SettingsLoader
    {
        public static Models.Settings LoadSettings()
        {
            try
            {
                string localAppDataPath = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
                string settingsDirectory = Path.Combine(localAppDataPath, "duHast");
                string settingsFilePath = Path.Combine(settingsDirectory, "pushIt_settings.json");

                // return a default settings object if the settings file does not exist
                if (!File.Exists(settingsFilePath))
                {
                    //initialize settings default
                    Models.Settings settingsDefault = new Models.Settings();
                    settingsDefault.DataPath = @"C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\VS\PushIt\Testdata\20250205_CSB.csv";
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
    }
}
