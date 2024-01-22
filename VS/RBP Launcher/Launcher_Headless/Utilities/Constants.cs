﻿using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Launcher_Headless.Utilities
{
    public class Constants
    {
        // settings
        public static string settingsFolderName = "BatchRvtLauncher";
        public static string settingsFileName = "settings.json";
        public static string localAppDataPath = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        public static string settigsFilePath = Path.Combine(localAppDataPath,settingsFolderName,settingsFileName);
    }
}
