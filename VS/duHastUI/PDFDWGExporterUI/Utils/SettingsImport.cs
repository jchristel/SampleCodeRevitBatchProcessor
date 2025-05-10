using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace duHastNet.UI.PDFDWGExporterUI.Utils
{
    public static class SettingsImport
    {
        public static Dictionary<string, string> ImportSettingsFromJson(
            string filePath,
            Action<string, duHastNet.Utils.WPF.Stores.MessageTypes> AddMessage
            )
        {

            Dictionary<string, string> settings = new Dictionary<string, string>();

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
