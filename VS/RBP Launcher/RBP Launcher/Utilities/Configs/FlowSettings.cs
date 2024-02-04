using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Serilog;

namespace RBP_Launcher.Utilities.Configs
{
    public class FlowSettings
    {
        public static ScriptConfiguration? GetFlowSettings(string settingsFilePath)
        {
            try
            {
                // Read the JSON string from the file
                string jsonString = File.ReadAllText(settingsFilePath);
                ScriptConfiguration? config = ScriptConfiguration.FromJson(jsonString);
                return config;
            }
            catch (Exception ex)
            {
                Log.Error(ex, "An error occurred in {ClassName}.{MethodName}", nameof(FlowSettings), nameof(GetFlowSettings));
            }
            return null;
        }
    }
}
