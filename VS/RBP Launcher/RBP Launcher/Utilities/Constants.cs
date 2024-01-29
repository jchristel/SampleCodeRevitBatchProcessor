using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RBP_Launcher.Utilities
{
    public class Constants
    {
        // settings
        public static string settingsFolderName = "BatchRvtLauncher";
        public static string logFolderName = "logs";
        public static string logFileName = "log.txt";
        public static string settingsFileName = "settings.json";
        public static string localAppDataPath = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        public static string settigsFilePath = Path.Combine(localAppDataPath,settingsFolderName,settingsFileName);

        public static List<string> supportedIronPythonVersions = new List<string> { "2.7", "3.5" };
    }
}
