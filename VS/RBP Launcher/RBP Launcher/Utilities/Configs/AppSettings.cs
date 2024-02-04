using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Serilog;

namespace RBP_Launcher.Utilities.Configs
{
    public class AppSettings
    {
        /// <summary>
        /// Get the application settings object from a json formatted file.
        /// </summary>
        /// <returns>
        /// LauncherHeadlessConfiguration if file was read succesfully, otherwise null.
        /// </returns>
        public static LauncherHeadlessConfiguration? GetAppSettings()
        {
            try
            {
                string jsonApplicationSettings = File.ReadAllText(Constants.settigsFilePath);
                LauncherHeadlessConfiguration? configApplication = LauncherHeadlessConfiguration.FromJson(jsonApplicationSettings);
                return configApplication;
            }
            catch (Exception ex)
            {
                Log.Error(ex, "An error occurred in {ClassName}.{MethodName}", nameof(AppSettings), nameof(GetAppSettings));
            }
            return null;
        }
    }
}
