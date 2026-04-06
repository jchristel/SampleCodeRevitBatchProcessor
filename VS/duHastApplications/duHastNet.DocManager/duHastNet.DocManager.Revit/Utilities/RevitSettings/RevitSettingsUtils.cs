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

using Autodesk.Revit.DB;
using duHastNet.DocManager.Core.Models.Database;
using duHastNet.UI.DocManagerSettingsUI.Utils;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace duHastNet.DocManager.Revit.Utilities.RevitSettings
{
    public static class RevitSettingsUtils
    {
        public static string LoadSettingsFromRevitModel(Document doc)
        {
            // load settings from Revit model, e.g. from extensible storage
            return string.Empty;
        }


        public static void SaveSettingsToRevitModel(Document doc, string settingsJson)
        {
            // save settings to Revit model, e.g. to extensible storage

        }


        /// <summary>
        /// Initialises the settings object for the UI from a JSON string loaded from the Revit model.
        /// </summary>
        /// <param name="settingsJson">JSON string containing the settings loaded from the Revit model.</param>
        /// <returns>Initialised settings object for the UI.</returns>
        public static duHastNet.UI.DocManagerSettingsUI.Utils.Settings InitialiseRevitSettings(string settingsJson)
        {
            // initialise settings from json, e.g. by deserialisation
            // use function from settings utils to convert from json to settings object
            duHastNet.UI.DocManagerSettingsUI.Utils.Settings deserializedSettings = duHastNet.UI.DocManagerSettingsUI.Utils.SettingsFromRevit.InitialiseSettingsFromRevitJson(settingsJson);
            return deserializedSettings;
        }
    }
}
