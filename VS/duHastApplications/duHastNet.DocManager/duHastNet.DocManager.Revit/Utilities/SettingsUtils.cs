//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2026, Jan Christel
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

using System.IO;

namespace duHastNet.DocManager.Revit.Utilities
{
    public static class SettingsUtils
    {
        public static string settingsDirectory = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "duHast");

        public static string settingsFileNamePrefix = "docManagerRevit_settings_";
        private static string settingsFilePath = Path.Combine(settingsDirectory, "docManagerRevit_settings.json");

        public static void SaveSettings(Models.Settings settings)
        {

        }

        public static Models.Settings LoadSettings()
        {
            return new Models.Settings();
        }

        /// <summary>
        /// Will eventually load the settings stored in the Revit model, if they exist. For now, this is a placeholder that returns an empty string.
        /// </summary>
        /// <param name="doc">The Revit document from which to load the settings.</param>
        /// <returns></returns>
        public static string LoadSettingsFromRevitModel(Autodesk.Revit.DB.Document doc)
        {
            return string.Empty;
        }
    }
}
