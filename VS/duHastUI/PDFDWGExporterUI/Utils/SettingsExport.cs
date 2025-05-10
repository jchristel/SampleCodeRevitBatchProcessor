using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;

namespace duHastNet.UI.PDFDWGExporterUI.Utils
{
    public static class SettingsExport
    {
        public static void ExportSettingsToJson(
            string filePath,
            Dictionary<string, object> settings,
            Action<string, duHastNet.Utils.WPF.Stores.MessageTypes> AddMessage
            )
        {
            try
            {
                string json = Newtonsoft.Json.JsonConvert.SerializeObject(settings, Newtonsoft.Json.Formatting.None);
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
